# test_api.py

## Archivos que depura
- `infrastructure/server/setting.py` → FastAPI app
- `infrastructure/server/server.py` → `create_application()`
- `presentation/urls.py` → routers
- `presentation/endpoints/auth.py` → todos los endpoints de auth
- `infrastructure/errors/auth.py` → handlers de excepciones
- `domain/errors/auth_errors.py` → `UnauthorizedError`, `ForbiddenError`

## Flujo que traza
Pruebas de API de punta a punta usando `TestClient` de FastAPI. Levanta la aplicacion real y verifica que los endpoints HTTP responden con los codigos de estado y cuerpos esperados. **Requiere base de datos PostgreSQL real corriendo.**

### TestAuthAPI (10 tests)
| Test | Que valida |
|------|-----------|
| `test_root_endpoint` | `GET /` → 200 con `"Hola Mundo"` |
| `test_register_user` | `POST /auth/register` → 201, cuerpo contiene `"registrado"` |
| `test_register_duplicate_user` | Segundo `POST /auth/register` mismo username → 409 |
| `test_login_success` | Register → login con credenciales correctas → 200 + `access_token` + `token_type=bearer` |
| `test_login_wrong_password` | Login con password incorrecta → 401 |
| `test_login_user_not_found` | Login con usuario inexistente → 401 |
| `test_super_admin_register_and_login` | `POST /auth/super-admin/register` → 201. Login con secret key correcta → 200 + token. |
| `test_super_admin_login_wrong_key` | Login con secret key inexistente → 401 |
| `test_protected_endpoint_without_token` | `GET /` funciona sin token (no esta protegido) |
| `test_logout` | `POST /auth/logout` → 200 |

### TestSmoke (3 tests)
| Test | Que valida |
|------|-----------|
| `test_app_starts` | `client` fixture crea la app sin errores |
| `test_docs_available` | `GET /docs` → 200 (Swagger UI) |
| `test_openapi_schema` | `GET /openapi.json` → 200, contiene `/auth/login`, `/auth/register`, `/auth/super-admin/login` |

## Resultado esperado
13/13 tests pasan (requiere PostgreSQL corriendo).

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_root_endpoint` | Verificar `urls.py` tiene `@router.get("/")` |
| `test_register_user` | `pydantic_extra_types[phone]` instalado. Email debe ser valido. |
| `test_register_duplicate_user` | El use case debe lanzar `ValueError` y el endpoint traducirlo a 409 |
| `test_login_success` | Verificar `pwd_context.verify()` con bcrypt. Si `bcrypt>=5.0`, instalar `bcrypt==4.0.1`. |
| `test_login_wrong_password` | `LoginUseCase` debe lanzar `UnauthorizedError`. Handler en `infrastructure/errors/auth.py` debe convertir a 401. |
| `test_super_admin_register_and_login` | `SuperAdminRepository.save()` debe funcionar. `get_by_secret_key()` debe encontrar. `SuperAdminLoginUseCase` debe retornar token. |
| `test_openapi_schema` | Verificar que los routers estan incluidos en `urls.py` con `include_router()`. |
| La app no levanta | Verificar `lifespan` no falla. Si Redis/PostgreSQL no estan disponibles, mockear o desactivar. |
