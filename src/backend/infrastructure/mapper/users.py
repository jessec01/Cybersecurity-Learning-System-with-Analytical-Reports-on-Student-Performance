from backend.domain.entities.users import User
from backend.infrastructure.db.postgres.models import UserModel

class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id_users=model.id_users,
            username=model.username,
            password=model.password,
            is_email_verified=model.is_email_verified,
            is_token_verified=model.is_token_verified,
            is_token_reset=model.is_token_reset,
            is_token_expired=model.is_token_expired,
            is_active=model.is_active,
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id_users=user.id_users,
            username=user.username,
            password=user.password,
            is_email_verified=user.is_email_verified,
            is_token_verified=user.is_token_verified,
            is_token_reset=user.is_token_reset,
            is_token_expired=user.is_token_expired,
            is_active=user.is_active,
        )   