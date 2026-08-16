from datetime import datetime, timezone

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from backend.domain.entities.users import Users
from backend.domain.repositories.repositorieusers import RepositeorieUser
from backend.infrastructure.db.postgres.models import UserModel


class UserRepository(RepositeorieUser):

    def __init__(self, db: Session):
        self._db = db

    def save(self, user: Users) -> None:
        model = UserModel(
            username=user.username,
            password=user.password,
            is_email_verified=user.is_email_verified,
            is_token_verified=user.is_token_verified,
            is_token_reset=user.is_token_reset,
            is_token_expired=user.is_token_expired,
            is_active=user.is_active,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()

    def update(self, user: Users) -> None:
        model = self._db.query(UserModel).filter(UserModel.username == user.username).first()
        if model:
            model.password = user.password
            model.is_email_verified = user.is_email_verified
            model.is_token_verified = user.is_token_verified
            model.is_token_reset = user.is_token_reset
            model.is_token_expired = user.is_token_expired
            model.is_active = user.is_active
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()

    def delete(self, user: Users) -> None:
        model = self._db.query(UserModel).filter(UserModel.username == user.username).first()
        if model:
            self._db.delete(model)
            self._db.commit()

    def get_by_id(self, user_id: int) -> Users | None:
        model = self._db.query(UserModel).filter(UserModel.id_user == user_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_by_username(self, username: str) -> Users | None:
        model = self._db.query(UserModel).filter(UserModel.username == username).first()
        if not model:
            return None
        return self._to_entity(model)

    def get_all(self) -> list[Users]:
        models = self._db.query(UserModel).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: UserModel) -> Users:
        return Users(
            id_user=model.id_user,
            username=model.username,
            password=model.password,
            is_email_verified=model.is_email_verified,
            is_token_verified=model.is_token_verified,
            is_token_reset=model.is_token_reset,
            is_token_expired=model.is_token_expired,
            is_active=model.is_active,
        )
