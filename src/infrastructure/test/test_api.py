import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from fastapi.testclient import TestClient
from domain.entities.super_admins import SuperAdmins
from infrastructure.server.server import create_application
from infrastructure.db.postgres.connection import Base, engine
from infrastructure.db.postgres.connection import session_local


@pytest.fixture(scope="module")
def client():
    app = create_application()
    return TestClient(app)


@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    db = session_local()
    yield db
    db.rollback()
    db.close()


class TestAuthAPI:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Hola Mundo" in response.json()["mensaje"]

    def test_register_user(self, client):
        payload = {
            "username": "apitest",
            "password": "pass123",
            "first_name": "Api",
            "last_name": "Test",
            "mail": "api@test.com",
            "phone": "+51999888777",
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201
        assert "registrado" in response.json()["message"].lower()

    def test_register_duplicate_user(self, client):
        payload = {
            "username": "duptest",
            "password": "pass123",
            "first_name": "Dup",
            "last_name": "Test",
            "mail": "dup@test.com",
        }
        client.post("/auth/register", json=payload)
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409

    def test_login_success(self, client):
        client.post("/auth/register", json={
            "username": "logintest", "password": "pass123",
            "first_name": "Login", "last_name": "Test", "mail": "login@test.com",
        })
        response = client.post("/auth/login", json={
            "username": "logintest", "password": "pass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/auth/register", json={
            "username": "wrongpw", "password": "correct",
            "first_name": "W", "last_name": "P", "mail": "w@test.com",
        })
        response = client.post("/auth/login", json={
            "username": "wrongpw", "password": "incorrect",
        })
        assert response.status_code == 401

    def test_login_user_not_found(self, client):
        response = client.post("/auth/login", json={
            "username": "noexiste", "password": "whatever",
        })
        assert response.status_code == 401

    def test_super_admin_register_and_login(self, client):
        secret = SuperAdmins.generate_secret_key()
        register_resp = client.post("/auth/super-admin/register", json={
            "id_person": 10, "secret_key": secret,
        })
        assert register_resp.status_code == 201

        login_resp = client.post("/auth/super-admin/login", json={
            "secret_key": secret,
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

    def test_super_admin_login_wrong_key(self, client):
        response = client.post("/auth/super-admin/login", json={
            "secret_key": "clave-que-no-existe",
        })
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_logout(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 200


class TestSmoke:
    def test_app_starts(self, client):
        assert client is not None

    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/auth/login" in schema["paths"]
        assert "/auth/register" in schema["paths"]
        assert "/auth/super-admin/login" in schema["paths"]
