import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from domain.entities.users import Users
from domain.entities.persons import Person
from domain.entities.super_admins import SuperAdmins
from domain.entities.roles import Role, Permission
from domain.value_objects.permissions import Permissions, Resource, Action
from domain.errors.auth_errors import UnauthorizedError, ForbiddenError


class TestUserEntity:
    def test_create_user(self):
        user = Users(username="juan", password="hash",
                     is_email_verified=False, is_token_verified=False,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        assert user.username == "juan"
        assert user.is_active is True
        assert user.roles == []
        assert user.permissions == []

    def test_is_email_verified(self):
        user = Users(username="juan", password="hash",
                     is_email_verified=True, is_token_verified=False,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        assert user.is_user_email_verified() is True

    def test_is_user_verified_activates(self):
        user = Users(username="juan", password="hash",
                     is_email_verified=True, is_token_verified=True,
                     is_token_reset=False, is_token_expired=False, is_active=False)
        user.is_user_verified()
        assert user.is_active is True

    def test_is_user_not_verified_deactivates(self):
        user = Users(username="juan", password="hash",
                     is_email_verified=False, is_token_verified=True,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        user.is_user_verified()
        assert user.is_active is False

    def test_token_expired_check(self):
        user = Users(username="juan", password="hash",
                     is_email_verified=True, is_token_verified=True,
                     is_token_reset=False, is_token_expired=True, is_active=True)
        assert user.is_user_token_expired() is True

    def test_user_with_permissions(self):
        user = Users(username="admin", password="hash",
                     is_email_verified=True, is_token_verified=True,
                     is_token_reset=False, is_token_expired=False, is_active=True,
                     permissions=[Permissions.COURSE_CREATE, Permissions.USER_READ])
        assert Permissions.COURSE_CREATE in user.permissions
        assert len(user.permissions) == 2


class TestPersonEntity:
    def test_full_name(self):
        person = Person(first_name="Juan", last_name="Perez", mail="juan@test.com")
        assert person.extraction_full_name() == "Juan Perez"

    def test_date_of_birth_valid_past(self):
        from datetime import date
        person = Person(first_name="A", last_name="B", mail="a@b.com",
                        date_of_birth=date(1990, 1, 1))
        assert person.date_of_birth_valid() is True

    def test_date_of_birth_invalid_future(self):
        from datetime import date, timedelta
        future = date.today() + timedelta(days=1)
        person = Person(first_name="A", last_name="B", mail="a@b.com",
                        date_of_birth=future)
        assert person.date_of_birth_valid() is False


class TestSuperAdminEntity:
    def test_verify_secret_key(self):
        admin = SuperAdmins(id_person=1, is_active=True, secret_key="abc123")
        assert admin.verify_secret_key("abc123") is True
        assert admin.verify_secret_key("wrong") is False

    def test_generate_secret_key(self):
        key = SuperAdmins.generate_secret_key()
        assert isinstance(key, str)
        assert len(key) == 36
        assert "-" in key


class TestRoleEntity:
    def test_role_with_permissions(self):
        perm = Permission(id_permission=1, codename="course:create",
                          resource="course", action="create",
                          description="Crear cursos")
        role = Role(id_rol=1, name="admin", permissions=[perm])
        assert role.name == "admin"
        assert len(role.permissions) == 1
        assert role.permissions[0].codename == "course:create"


class TestErrors:
    def test_unauthorized_error(self):
        with pytest.raises(UnauthorizedError):
            raise UnauthorizedError("Token invalido")

    def test_forbidden_error(self):
        with pytest.raises(ForbiddenError):
            raise ForbiddenError("Permiso denegado")
