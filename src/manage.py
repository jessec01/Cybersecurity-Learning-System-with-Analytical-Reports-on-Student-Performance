"""Comandos de gestion ejecutables desde consola."""
import sys
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext

from infrastructure.db.postgres.connection import session_local
from infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository
from infrastructure.db.postgres.repositories.user_repository import UserRepository
from infrastructure.db.postgres.repositories.person_repository import PersonRepository
from domain.value_objects.users import UsersValidate
from domain.value_objects.persons import PersonsValidate
from domain.entities.users import Users
from domain.entities.persons import Person
from domain.entities.super_admins import SuperAdmins

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_super_admin():
    db = session_local()

    try:
        print("=== CREACION DE SUPER ADMINISTRADOR ===\n")

        # 1. RECIBIR DATOS DE TERMINAL
        raw_username = input("Username: ").strip()
        raw_password = input("Password: ").strip()

        # 2. VALIDAR CON VALUE OBJECT
        validated = UsersValidate(raw_username, raw_password)

        # 3. CREAR ENTIDAD DE DOMINIO
        user = Users(
            username=validated.username,
            password=pwd_context.hash(validated.password),
            is_email_verified=True,
            is_token_verified=True,
            is_token_reset=False,
            is_token_expired=False,
            is_active=True,
        )

        # 4. GUARDAR USUARIO EN DB
        user_repo = UserRepository(db)
        if user_repo.get_by_username(validated.username):
            print(f"\nError: El username '{validated.username}' ya existe.")
            return
        user_repo.save(user)
        saved_user = user_repo.get_by_username(validated.username)
        print(f"Usuario '{saved_user.username}' creado (id={saved_user.id_user}).")

        # 5. RECIBIR DATOS DE PERSONA
        first_name = input("Primer nombre: ").strip()
        last_name = input("Apellido: ").strip()
        raw_phone = input("Telefono (opcional): ").strip()
        raw_mail = input("Correo electronico: ").strip()

        # 6. VALIDAR PERSONA
        person_v = PersonsValidate(first_name, last_name, raw_phone, raw_mail)

        # 7. CREAR ENTIDAD PERSONA
        person = Person(
            first_name=person_v.name,
            last_name=person_v.last_name,
            mail=person_v.email,
            phone=person_v.phone if person_v.phone else None,
            id_users=saved_user.id_user,
        )

        # 8. GUARDAR PERSONA
        PersonRepository(db).save(person)
        print(f"Persona '{person_v.name} {person_v.last_name}' creada.")

        # 9. CREAR SUPER ADMIN
        secret = SuperAdmins.generate_secret_key()
        admin = SuperAdmins(
            id_person=person.id_person if person.id_person else saved_user.id_user,
            is_active=True,
            secret_key=secret,
        )
        SuperAdminRepository(db).save(admin)
        massage_welcom="\nSuper admin creado exitosamente."
        print(f"{massage_welcom}")
        massage_secret_key="GUARDA ESTA SECRET KEY:"
        print(f"{massage_secret_key}")
        massage_secret_key_value=f"    {secret}\n"
        print(f"{massage_secret_key_value}")

    except ValueError :
        massage_error="Error de validacion"
        print(f"{massage_error}")
        db.rollback()
    except Exception:
        massage_error="Error inesperado"
        print(f"{massage_error}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/manage.py create-super-admin")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create-super-admin":
        create_super_admin()
    else:
        print(f"Comando desconocido: {command}")
