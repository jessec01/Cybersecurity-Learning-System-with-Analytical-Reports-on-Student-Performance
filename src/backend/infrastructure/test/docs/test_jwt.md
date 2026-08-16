# test_jwt.py

## Archivos que depura
- `infrastructure/auth/jwt.py` → `create_access_token()`, `decode_access_token()`
- `infrastructure/auth/setting.py` → `JWTSettings` / `jwt_settings`

## Flujo que traza
Pruebas unitarias del ciclo completo de JWT: creacion, decodificacion y rechazo de tokens invalidos/expirados. Sin DB, sin Redis.

### TestJWT (3 tests)
| Test | Que valida |
|------|-----------|
| `test_create_and_decode_token` | `create_access_token({"sub": "42"})` genera un JWT. `decode_access_token()` recupera `sub`, `type`, `exp`. El `exp` existe en el payload. |
| `test_expired_token` | Token con `exp` en el pasado → `decode_access_token()` lanza `ExpiredSignatureError` |
| `test_invalid_token` | String malformado `"not.a.valid.token"` → `PyJWT.DecodeError` |

## Resultado esperado
3/3 tests pasan.

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_create_and_decode_token` | Verificar que `sub` se pasa como string (PyJWT exige `sub: str`). Si pasas `int`, lanza `InvalidSubjectError`. Tambien verificar `.env` tiene `JWT_SECRET_KEY` y `JWT_ALGORITHM=HS256`. |
| `test_expired_token` | `jwt.decode()` debe validar `exp`. Si no valida, revisar version de `pyjwt` y que no se pase `options={"verify_exp": False}`. |
| `test_invalid_token` | Asegurar que no hay try/except que se coma `DecodeError` dentro de `decode_access_token()`. |
| Warning: HMAC key corta | `JWT_SECRET_KEY` en `.env` debe tener 32+ bytes. Cambia de `change-me-in-production` a una key de 32+ caracteres aleatorios. |
