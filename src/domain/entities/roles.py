# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class Permission(BaseModel):
    id_permission: int
    codename: str
    resource: str
    action: str
    description: str
    is_active: bool = True


class Role(BaseModel):
    id_rol: int
    name: str
    is_active: bool = True
    permissions: list[Permission] = []