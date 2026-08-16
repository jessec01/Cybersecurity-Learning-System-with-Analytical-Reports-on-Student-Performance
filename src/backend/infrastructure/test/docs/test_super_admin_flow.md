# test_super_admin_flow.py

## Archivos que depura
- `domain/value_objects/users.py` → `UsersValidate`
- `domain/value_objects/persons.py` → `PersonsValidate`
- `domain/entities/users.py` → `Users`
- `domain/entities/persons.py` → `Person`
- `domain/entities/super_admins.py` → `SuperAdmins`
- `infrastructure/db/postgres/repositories/` → UserRepo, PersonRepo, SuperAdminRepo
- `src/manage.py` → flujo `create_super_admin()` (indirectamente)

## Flujo que traza
Simula exactamente lo que hace `manage.py create_super_admin` paso por paso: recibe strings crudos → valida con value objects → crea entidades de dominio → persiste via repositorios → verifica integridad de la cadena User → Person → SuperAdmin.

### TestUsersValidate (10 tests)
| Test | Que valida |
|------|-----------|
| `test_valid_username_and_password` | `"juan_123"` + `"Pass123!"` pasan validacion |
| `test_short_username` | Username de 2 chars → `ValueError("Username...")` |
| `test_username_with_special_chars` | `"juan@perez"` → `ValueError` |
| `test_username_with_spaces` | `"juan perez"` → `ValueError` |
| `test_long_username` | 17 chars → `ValueError` |
| `test_short_password` | `"Ab1!"` (4 chars) → `ValueError("Password...")` |
| `test_password_without_uppercase` | `"pass123!"` (sin mayuscula) → `ValueError` |
| `test_password_without_number` | `"Password!"` (sin numero) → `ValueError` |
| `test_password_without_special_char` | `"Pass1234"` (sin caracter especial) → `ValueError` |
| `test_valid_password_complex` | `"Admin@2024"` pasa validacion completa |

### TestPersonsValidate (7 tests)
| Test | Que valida |
|------|-----------|
| `test_valid_person` | Todos los campos validos → objeto creado |
| `test_empty_phone` | Phone vacio → `None` (no falla) |
| `test_short_first_name` | 1 char → `ValueError("Nombre...")` |
| `test_last_name_with_numbers` | Apellido con numeros → `ValueError("Apellido...")` |
| `test_invalid_email` | `"esto-no-es-email"` → `ValueError("Email...")` |
| `test_email_without_domain` | `"usuario@"` → `ValueError` |
| `test_invalid_phone_number` | `"12345"` → `ValueError("Telefono...")` |

### TestSuperAdminEntity (3 tests)
| Test | Que valida |
|------|-----------|
| `test_generate_secret_key_is_unique` | Dos llamadas consecutivas generan keys diferentes |
| `test_verify_secret_key` | `verify_secret_key()` devuelve True/False correctamente |
| `test_default_active` | `is_active` es `True` por defecto |

### TestFullSuperAdminFlow (5 tests)
| Test | Que valida |
|------|-----------|
| `test_complete_flow_with_valid_data` | Flujo completo: UsersValidate → Users → UserRepo.save → PersonsValidate → Person → PersonRepo.save → SuperAdmin → SuperAdminRepo.save → get_by_secret_key verifica todo |
| `test_flow_rejects_duplicate_username` | Segundo usuario con mismo username es detectado |
| `test_flow_rejects_invalid_email_early` | Email invalido en PersonsValidate CORTA antes de tocar DB |
| `test_flow_rejects_invalid_username_early` | Username invalido en UsersValidate CORTA antes de tocar DB |
| `test_entities_chain_is_connected` | User.id_user → Person.id_users → SuperAdmin.id_person encadenados |

## Resultado esperado
25/25 tests pasan.

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_valid_username_and_password` | Revisar regex en `UsersValidate._check_username()`: `^[a-zA-Z0-9_]{3,16}$` |
| `test_short_password` | Regex de password: minimo 8 chars, requiere mayuscula, numero, caracter especial |
| `test_empty_phone` | `PersonsValidate._check_phone()` debe retornar `None` si recibe string vacio |
| `test_invalid_phone_number` | `phonenumbers.parse(phone, None)` debe lanzar `NumberParseException`. Asegurar que `phonenumbers` esta instalado. |
| `test_complete_flow_with_valid_data` | Si falla: revisar que `UserRepository.save()` hace commit, que `get_by_username()` retorna entidad con `id_user`, que `PersonRepository` acepta `id_users` como FK |
| `test_entities_chain_is_connected` | Verificar que `Person.id_users` y `SuperAdmin.id_person` se setean correctamente desde los repos |
