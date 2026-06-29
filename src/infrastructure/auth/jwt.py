from datetime import datetime, timedelta, timezone

import jwt

from infrastructure.auth.setting import jwt_settings


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_settings.JWT_SECRET_KEY, algorithm=jwt_settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, jwt_settings.JWT_SECRET_KEY, algorithms=[jwt_settings.JWT_ALGORITHM])
