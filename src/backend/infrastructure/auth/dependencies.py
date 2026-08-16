# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from backend.infrastructure.auth.jwt import decode_access_token
from backend.infrastructure.db.postgres.connection import get_db
from backend.infrastructure.db.postgres.repositories.user_repository import UserRepository
from backend.infrastructure.db.postgres.repositories.person_repository import PersonRepository
from backend.infrastructure.db.postgres.repositories.role_repository import RoleRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    person_repo = PersonRepository(db)
    person = person_repo.get_by_user_id(user_id)

    role_repo = RoleRepository(db)
    if person:
        user.roles = role_repo.get_roles_for_person(person.id_person)
        user.permissions = role_repo.get_permissions_for_person(person.id_person)
    else:
        user.roles = []
        user.permissions = []

    return user


def require_permission(permission: str):
    async def verifier(user=Depends(get_current_user)):
        if permission not in user.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso denegado")
        return user
    return verifier
