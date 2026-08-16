"""Comandos de gestion ejecutables desde consola."""
import sys
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext

from backend.infrastructure.db.postgres.connection import session_local
from backend.infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository
from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository
from backend.infrastructure.db.postgres.repositories.person_repository import PersonRepository
from backend.domain.value_objects.users import UsersValidate
from backend.domain.value_objects.persons import PersonsValidate
from backend.domain.entities.users import Users
from backend.domain.entities.persons import Person
from backend.domain.entities.super_admins import SuperAdmins

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_super_admin():
    print("=== CREACION DE SUPER ADMINISTRADOR ===\n")
    # 1. RECIBIR DATOS DE TERMINAL
    raw_username = input("Username: ").strip()
    raw_password = input("Password: ").strip()
    # 5. RECIBIR DATOS DE PERSONA
    first_name = input("Primer nombre: ").strip()
    last_name = input("Apellido: ").strip()
    raw_phone = input("Telefono (opcional): ").strip()
    raw_mail = input("Correo electronico: ").strip()
    data={
        "username":raw_username,
        "password":raw_password,
        "first_name":first_name,
        "last_name":last_name,
        "phone":raw_phone,
        "mail":raw_mail
    }
    return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/manage.py create-super-admin")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create-super-admin":
        create_super_admin()
    else:
        print(f"Comando desconocido: {command}")
