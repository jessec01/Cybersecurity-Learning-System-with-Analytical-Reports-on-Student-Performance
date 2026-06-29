# pyrefly: ignore [missing-import]
from passlib.context import CryptContext    
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from application.dto.auth_dto import LoginInput, RegisterInput, TokenOutput, SuperAdminLoginInput
from domain.entities.users import Users
from domain.entities.persons import Person
from domain.errors.auth_errors import UnauthorizedError
from infrastructure.auth.jwt import create_access_token
from infrastructure.db.postgres.repositories.user_repository import UserRepository
from infrastructure.db.postgres.repositories.person_repository import PersonRepository
from infrastructure.db.postgres.repositories.super_admin_repository import SuperAdminRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginUseCase:
    def __init__(self, db: Session):
        self._db = db

    def execute(self, input_data: LoginInput) -> TokenOutput:
        repo = UserRepository(self._db)
        user = repo.get_by_username(input_data.username)
        if not user or not pwd_context.verify(input_data.password, user.password):
            raise UnauthorizedError("Credenciales invalidas")
        if not user.is_active:
            raise UnauthorizedError("Cuenta inactiva")
        token = create_access_token(data={"sub": str(user.id_user)})
        return TokenOutput(access_token=token)


class RegisterUseCase:
    def __init__(self, db: Session):
        self._db = db

    def execute(self, input_data: RegisterInput) -> None:
        user_repo = UserRepository(self._db)
        if user_repo.get_by_username(input_data.username):
            raise ValueError("El usuario ya existe")

        user = Users(
            username=input_data.username,
            password=pwd_context.hash(input_data.password),
            is_email_verified=False,
            is_token_verified=False,
            is_token_reset=False,
            is_token_expired=False,
            is_active=True,
        )
        user_repo.save(user)
        saved = user_repo.get_by_username(input_data.username)

        person = Person(
            first_name=input_data.first_name,
            last_name=input_data.last_name,
            mail=input_data.mail,
            phone=input_data.phone,
            id_users=saved.id_user if saved else None,
        )
        PersonRepository(self._db).save(person)


class SuperAdminLoginUseCase:
    def __init__(self, db: Session):
        self._db = db

    def execute(self, input_data: SuperAdminLoginInput) -> TokenOutput:
        repo = SuperAdminRepository(self._db)
        admin = repo.get_by_secret_key(input_data.secret_key)
        if not admin:
            raise UnauthorizedError("Clave secreta invalida")
        token = create_access_token(data={"sub": str(admin.id_super_admin), "type": "super_admin"})
        return TokenOutput(access_token=token)
