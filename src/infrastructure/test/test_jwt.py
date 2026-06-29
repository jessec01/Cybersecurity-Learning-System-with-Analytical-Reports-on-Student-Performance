import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from infrastructure.auth.jwt import create_access_token, decode_access_token
from infrastructure.auth.setting import jwt_settings


class TestJWT:
    def test_create_and_decode_token(self):
        data = {"sub": "42", "type": "user"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 20

        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert payload["type"] == "user"
        assert "exp" in payload

    def test_expired_token(self):
        import time
        from datetime import datetime, timedelta, timezone
        import jwt as pyjwt

        expired_data = {
            "sub": 1,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
        }
        token = pyjwt.encode(expired_data, jwt_settings.JWT_SECRET_KEY, algorithm=jwt_settings.JWT_ALGORITHM)
        with pytest.raises(pyjwt.exceptions.ExpiredSignatureError):
            decode_access_token(token)

    def test_invalid_token(self):
        import jwt as pyjwt
        with pytest.raises(pyjwt.exceptions.DecodeError):
            decode_access_token("not.a.valid.token")
