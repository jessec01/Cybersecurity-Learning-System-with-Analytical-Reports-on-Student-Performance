# test_domain.py

## Archivos que depura
- `domain/entities/users.py` → `Users`
- `domain/entities/persons.py` → `Person`
- `domain/entities/super_admins.py` → `SuperAdmins`
- `domain/entities/roles.py` → `Role`, `Permission`
- `domain/value_objects/permissions.py` → `Permissions`, `Resource`, `Action`
- `domain/errors/auth_errors.py` → `UnauthorizedError`, `ForbiddenError`

## Flujo que traza
Pruebas unitarias puras. Cada entidad se crea en memoria sin DB ni infraestructura externa.

### TestUserEntity (6 tests)
| Test | Que valida |
|------|-----------|
| `test_create_user` | Constructor crea objeto con defaults correctos (`roles=[], permissions=[]`) |
| `test_is_email_verified` | `is_user_email_verified()` retorna el valor del campo |
| `test_is_user_verified_activates` | Si email + token verificados → `is_active=True` |
| `test_is_user_not_verified_deactivates` | Si email NO verificado → `is_active=False` |
| `test_token_expired_check` | `is_user_token_expired()` refleja el campo |
| `test_user_with_permissions` | El campo `permissions` acepta lista de constantes de dominio |

### TestPersonEntity (3 tests)
| Test | Que valida |
|------|-----------|
| `test_full_name` | `extraction_full_name()` concatena `first_name + last_name` |
| `test_date_of_birth_valid_past` | Fecha pasada → `date_of_birth_valid() == True` |
| `test_date_of_birth_invalid_future` | Fecha futura → `date_of_birth_valid() == False` |

### TestSuperAdminEntity (2 tests)
| Test | Que valida |
|------|-----------|
| `test_verify_secret_key` | `verify_secret_key()` compara correctamente |
| `test_generate_secret_key` | UUID de 36 chars con guiones |

### TestRoleEntity (1 test)
| Test | Que valida |
|------|-----------|
| `test_role_with_permissions` | Rol contiene lista de `Permission` con `codename`, `resource`, `action` |

### TestErrors (2 tests)
| Test | Que valida |
|------|-----------|
| `test_unauthorized_error` | `UnauthorizedError` se lanza y captura |
| `test_forbidden_error` | `ForbiddenError` se lanza y captura |

## Resultado esperado
14/14 tests pasan.

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_create_user` | Verificar que `Users` acepta todos los campos requeridos y defaults |
| `test_is_user_verified_*` | Revisar logica de `is_user_verified()` — debe setear `is_active` basado en verificaciones |
| `test_date_of_birth_*` | Verificar `date_of_birth_valid()` — debe comparar contra `date.today()` |
| `test_generate_secret_key` | `uuid.uuid4()` importado correctamente en `super_admins.py` |
| `test_role_with_permissions` | `Role.permissions` debe ser `list[Permission]` |
| `test_unauthorized_error` | `UnauthorizedError` debe heredar de `Exception` |
