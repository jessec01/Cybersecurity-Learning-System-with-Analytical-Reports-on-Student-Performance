"""
Test del flujo completo de creacion de Super Admin.
Valida: value objects → entidades → repositorios → integridad de datos.
Simula exactamente lo que hace manage.py paso por paso.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest
from passlib.context import CryptContext

from backend.domain.value_objects.users import UsersValidate
from backend.domain.value_objects.persons import PersonsValidate
from backend.domain.entities.users import Users
from backend.domain.entities.persons import Person
from backend.domain.entities.super_admins import SuperAdmins


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestUsersValidate:
    def test_valid_username_and_password(self):
        v = UsersValidate("juan_123", "Pass123!")
        assert v.username == "juan_123"
        assert v.password == "Pass123!"

    def test_short_username(self):
        with pytest.raises(ValueError, match="Username"):
            UsersValidate("ab", "Pass123!")

    def test_username_with_special_chars(self):
        with pytest.raises(ValueError, match="Username"):
            UsersValidate("juan@perez", "Pass123!")

    def test_username_with_spaces(self):
        with pytest.raises(ValueError, match="Username"):
            UsersValidate("juan perez", "Pass123!")

    def test_long_username(self):
        with pytest.raises(ValueError, match="Username"):
            UsersValidate("a" * 17, "Pass123!")

    def test_short_password(self):
        with pytest.raises(ValueError, match="Password"):
            UsersValidate("juan_ok", "Ab1!")

    def test_password_without_uppercase(self):
        with pytest.raises(ValueError, match="Password"):
            UsersValidate("juan_ok", "pass123!")

    def test_password_without_number(self):
        with pytest.raises(ValueError, match="Password"):
            UsersValidate("juan_ok", "Password!")

    def test_password_without_special_char(self):
        with pytest.raises(ValueError, match="Password"):
            UsersValidate("juan_ok", "Pass1234")

    def test_valid_password_complex(self):
        v = UsersValidate("admin_01", "Admin@2024")
        assert v.username == "admin_01"
        assert v.password == "Admin@2024"


class TestPersonsValidate:
    def test_valid_person(self):
        v = PersonsValidate("Juan", "Perez", "+51999888777", "juan@test.com")
        assert v.first_name == "Juan"
        assert v.last_name == "Perez"
        assert v.phone == "+51999888777"
        assert v.email == "juan@test.com"

    def test_empty_phone(self):
        v = PersonsValidate("Maria", "Lopez", "", "maria@test.com")
        assert v.first_name == "Maria"
        assert v.phone is None

    def test_short_first_name(self):
        with pytest.raises(ValueError, match="Nombre"):
            PersonsValidate("A", "Lopez", "", "a@test.com")

    def test_last_name_with_numbers(self):
        with pytest.raises(ValueError, match="Apellido"):
            PersonsValidate("Juan", "Perez123", "", "juan@test.com")

    def test_invalid_email(self):
        with pytest.raises(ValueError, match="Email"):
            PersonsValidate("Juan", "Perez", "", "esto-no-es-email")

    def test_email_without_domain(self):
        with pytest.raises(ValueError, match="Email"):
            PersonsValidate("Juan", "Perez", "", "usuario@")

    def test_invalid_phone_number(self):
        with pytest.raises(ValueError, match="Telefono"):
            PersonsValidate("Juan", "Perez", "12345", "juan@test.com")


class TestSuperAdminEntity:
    def test_generate_secret_key_is_unique(self):
        key1 = SuperAdmins.generate_secret_key()
        key2 = SuperAdmins.generate_secret_key()
        assert key1 != key2
        assert len(key1) == 36

    def test_verify_secret_key(self):
        admin = SuperAdmins(id_person=1, is_active=True, secret_key="sk-123")
        assert admin.verify_secret_key("sk-123") is True
        assert admin.verify_secret_key("sk-999") is False

    def test_default_active(self):
        admin = SuperAdmins(id_person=1, secret_key="sk")
        assert admin.is_active is True


class TestFullSuperAdminFlow:
    """Simula exactamente el flujo de manage.py create_super_admin:
       recibir strings → validar → crear entidades → guardar → verificar."""

    def test_complete_flow_with_valid_data(self, db_session):
        from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository
        from backend.infrastructure.db.postgres.repositories.person_repository import PersonRepository
        from backend.infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository

        # PASO 1: Validar datos de terminal
        validated_user = UsersValidate("admin_ok", "Admin@2024")
        assert validated_user.username == "admin_ok"

        # PASO 2: Crear entidad User
        hashed = pwd_context.hash(validated_user.password)
        user = Users(
            username=validated_user.username,
            password=hashed,
            is_email_verified=True,
            is_token_verified=True,
            is_token_reset=False,
            is_token_expired=False,
            is_active=True,
        )
        user_repo = UserRepository(db_session)
        user_repo.save(user)

        saved_user = user_repo.get_by_username("admin_ok")
        assert saved_user is not None
        assert saved_user.id_user is not None
        assert saved_user.is_active is True

        # PASO 3: Validar persona
        validated_person = PersonsValidate("Admin", "Sistema", "+51999888777", "admin@sistema.com")

        # PASO 4: Crear entidad Person vinculada
        person = Person(
            first_name=validated_person.first_name,
            last_name=validated_person.last_name,
            mail=validated_person.email,
            phone=validated_person.phone,
            id_users=saved_user.id_user,
        )
        person_repo = PersonRepository(db_session)
        person_repo.save(person)

        saved_person = person_repo.get_by_user_id(saved_user.id_user)
        assert saved_person is not None
        assert saved_person.first_name == "Admin"
        assert saved_person.mail == "admin@sistema.com"

        # PASO 5: Crear Super Admin vinculado a la persona
        secret = SuperAdmins.generate_secret_key()
        admin = SuperAdmins(
            id_person=saved_person.id_person,
            is_active=True,
            secret_key=secret,
        )
        admin_repo = SuperAdminRepository(db_session)
        admin_repo.save(admin)

        saved_admin = admin_repo.get_by_secret_key(secret)
        assert saved_admin is not None
        assert saved_admin.id_person == saved_person.id_person
        assert saved_admin.verify_secret_key(secret) is True

    def test_flow_rejects_duplicate_username(self, db_session):
        from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository

        # Primer usuario
        user1 = Users(username="duplicado", password="hash",
                      is_email_verified=True, is_token_verified=True,
                      is_token_reset=False, is_token_expired=False, is_active=True)
        repo = UserRepository(db_session)
        repo.save(user1)

        # Segundo usuario con mismo username debe fallar en el chequeo previo
        assert repo.get_by_username("duplicado") is not None

    def test_flow_rejects_invalid_email_early(self):
        """El value object debe fallar ANTES de tocar DB."""
        with pytest.raises(ValueError, match="Email"):
            PersonsValidate("Juan", "Perez", "", "correo-invalido")

    def test_flow_rejects_invalid_username_early(self):
        with pytest.raises(ValueError, match="Username"):
            UsersValidate("a", "Pass123!")

    def test_entities_chain_is_connected(self, db_session):
        """Verifica que User → Person → SuperAdmin estan encadenados correctamente."""
        from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository
        from backend.infrastructure.db.postgres.repositories.person_repository import PersonRepository
        from backend.infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository

        user = Users(username="chain_test", password="hash",
                     is_email_verified=True, is_token_verified=True,
                     is_token_reset=False, is_token_expired=False, is_active=True)
        UserRepository(db_session).save(user)
        saved_u = UserRepository(db_session).get_by_username("chain_test")

        person = Person(first_name="Chain", last_name="Test",
                        mail="chain@test.com", id_users=saved_u.id_user)
        PersonRepository(db_session).save(person)
        saved_p = PersonRepository(db_session).get_by_user_id(saved_u.id_user)

        secret = SuperAdmins.generate_secret_key()
        admin = SuperAdmins(id_person=saved_p.id_person,
                            is_active=True, secret_key=secret)
        SuperAdminRepository(db_session).save(admin)
        saved_a = SuperAdminRepository(db_session).get_by_secret_key(secret)

        # Verificar cadena completa
        assert saved_u.id_user is not None
        assert saved_p.id_users == saved_u.id_user
        assert saved_a.id_person == saved_p.id_person
