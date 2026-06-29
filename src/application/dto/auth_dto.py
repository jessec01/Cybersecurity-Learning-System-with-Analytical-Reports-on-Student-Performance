# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr
# pyrefly: ignore [missing-import]


class LoginInput(BaseModel):
    username: str
    password: str


class RegisterInput(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    mail: EmailStr
    phone: str | None = None


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SuperAdminLoginInput(BaseModel):
    secret_key: str


class SuperAdminRegisterInput(BaseModel):
    id_person: int
    secret_key: str


class UserOutput(BaseModel):
    id_user: int | None = None
    username: str
    is_active: bool
    roles: list[str] = []
    permissions: list[str] = []


class PersonOutput(BaseModel):
    id_person: int | None = None
    first_name: str
    last_name: str
    mail: str
    phone: str | None = None
