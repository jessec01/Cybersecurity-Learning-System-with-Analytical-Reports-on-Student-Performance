import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from datetime import datetime, timezone

from domain.entities.users import Users
from domain.entities.persons import Person
from domain.entities.super_admins import SuperAdmins
from infrastructure.db.postgres.repositories.user_repository import UserRepository
from infrastructure.db.postgres.repositories.person_repository import PersonRepository
from infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository


class TestUserRepository:
    def test_save_and_get_by_username(self, db_session):
        repo = UserRepository(db_session)
        user = Users(username="juan", password="hashed123",
                     is_email_verified=True, is_token_verified=False,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        repo.save(user)

        fetched = repo.get_by_username("juan")
        assert fetched is not None
        assert fetched.username == "juan"
        assert fetched.password == "hashed123"
        assert fetched.is_active is True

    def test_get_by_id(self, db_session):
        repo = UserRepository(db_session)
        user = Users(username="maria", password="hash",
                     is_email_verified=True, is_token_verified=True,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        repo.save(user)
        fetched = repo.get_by_username("maria")
        by_id = repo.get_by_id(fetched.id_user)
        assert by_id is not None
        assert by_id.username == "maria"

    def test_delete(self, db_session):
        repo = UserRepository(db_session)
        user = Users(username="todelete", password="x",
                     is_email_verified=False, is_token_verified=False,
                     is_token_reset=False, is_token_expired=False, is_active=False)
        repo.save(user)
        repo.delete(user)
        assert repo.get_by_username("todelete") is None

    def test_get_by_username_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert repo.get_by_username("noexiste") is None

    def test_get_by_id_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert repo.get_by_id(99999) is None

    def test_get_all(self, db_session):
        repo = UserRepository(db_session)
        u1 = Users(username="user1", password="a",
                   is_email_verified=True, is_token_verified=True,
                   is_token_reset=False, is_token_expired=False, is_active=True)
        u2 = Users(username="user2", password="b",
                   is_email_verified=True, is_token_verified=True,
                   is_token_reset=False, is_token_expired=False, is_active=True)
        repo.save(u1)
        repo.save(u2)
        all_users = repo.get_all()
        assert len(all_users) >= 2
        usernames = [u.username for u in all_users]
        assert "user1" in usernames
        assert "user2" in usernames

    def test_update(self, db_session):
        repo = UserRepository(db_session)
        user = Users(username="updateme", password="old",
                     is_email_verified=False, is_token_verified=False,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        repo.save(user)
        user.is_active = False
        user.password = "newhash"
        repo.update(user)
        fetched = repo.get_by_username("updateme")
        assert fetched.is_active is False
        assert fetched.password == "newhash"


class TestPersonRepository:
    def test_save_and_get_by_email(self, db_session):
        repo = PersonRepository(db_session)
        person = Person(first_name="Ana", last_name="Lopez", mail="ana@test.com", id_users=1)
        repo.save(person)

        fetched = repo.get_by_email("ana@test.com")
        assert fetched is not None
        assert fetched.first_name == "Ana"
        assert fetched.last_name == "Lopez"

    def test_get_by_user_id(self, db_session):
        repo = PersonRepository(db_session)
        person = Person(first_name="Carlos", last_name="Gomez", mail="carlos@test.com", id_users=42)
        repo.save(person)

        fetched = repo.get_by_user_id(42)
        assert fetched is not None
        assert fetched.first_name == "Carlos"

    def test_get_by_user_id_not_found(self, db_session):
        repo = PersonRepository(db_session)
        assert repo.get_by_user_id(99999) is None


class TestSuperAdminRepository:
    def test_save_and_get_by_secret_key(self, db_session):
        repo = SuperAdminRepository(db_session)
        admin = SuperAdmins(id_person=1, is_active=True, secret_key="sk-abc")
        repo.save(admin)

        fetched = repo.get_by_secret_key("sk-abc")
        assert fetched is not None
        assert fetched.id_person == 1
        assert fetched.verify_secret_key("sk-abc") is True

    def test_get_by_secret_key_not_found(self, db_session):
        repo = SuperAdminRepository(db_session)
        assert repo.get_by_secret_key("no-existe") is None
