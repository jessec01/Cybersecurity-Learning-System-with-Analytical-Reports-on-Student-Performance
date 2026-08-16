# test_repositories.py

## Archivos que depura
- `infrastructure/db/postgres/repositories/user_repository.py`
- `infrastructure/db/postgres/repositories/person_repository.py`
- `infrastructure/db/postgres/repositories/super_admin_repository.py`
- `infrastructure/db/postgres/models.py` (UserModel, PersonModel, SuperAdminModel)
- `domain/entities/users.py`, `domain/entities/persons.py`, `domain/entities/super_admins.py`

## Flujo que traza
Pruebas de integracion con SQLite en memoria. Cada test crea una DB fresh via fixture `db_session`, ejecuta operaciones CRUD reales con los repositorios implementados, y verifica que las entidades se persisten y recuperan correctamente.

### TestUserRepository (7 tests)
| Test | Que valida |
|------|-----------|
| `test_save_and_get_by_username` | `save()` persiste el usuario. `get_by_username()` lo recupera con todos los campos intactos |
| `test_get_by_id` | `save()` + `get_by_username()` → `id_user` autogenerado. `get_by_id(id)` retorna la misma entidad |
| `test_delete` | `save()` → `delete()` → `get_by_username()` retorna `None` |
| `test_get_by_username_not_found` | Usuario inexistente → `None` |
| `test_get_by_id_not_found` | ID inexistente → `None` |
| `test_get_all` | `save()` de 2 usuarios → `get_all()` retorna lista con ambos |
| `test_update` | `save()` → modificar atributos de la entidad → `update()` → `get_by_username()` refleja cambios |

### TestPersonRepository (3 tests)
| Test | Que valida |
|------|-----------|
| `test_save_and_get_by_email` | `save()` → `get_by_email()` retorna la persona con nombre y apellido correctos |
| `test_get_by_user_id` | `save()` con `id_users=42` → `get_by_user_id(42)` retorna la persona vinculada |
| `test_get_by_user_id_not_found` | `get_by_user_id(99999)` → `None` |

### TestSuperAdminRepository (2 tests)
| Test | Que valida |
|------|-----------|
| `test_save_and_get_by_secret_key` | `save()` → `get_by_secret_key()` retorna el admin con `id_person` y `secret_key` correctos |
| `test_get_by_secret_key_not_found` | Secret key inexistente → `None` |

## Resultado esperado
12/12 tests pasan.

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_save_and_get_by_username` | Verificar que `UserRepository.save()` hace `self._db.commit()`. Revisar mapeo de columnas en `models.py` (que `username` sea `unique=True`). |
| `test_get_by_id` | `UserModel.id_user` debe ser `autoincrement=True`. El `_to_entity` debe incluir `id_user`. |
| `test_delete` | `delete()` debe llamar `self._db.delete(model)` y `commit()`. |
| `test_update` | `update()` busca via `filter(UserModel.username == user.username)`. Si el username no cambia, funciona. Si se quiere soportar cambios de username, buscar por `id_user`. |
| `test_save_and_get_by_email` | `PersonModel` debe tener `created_at` (agregado al contrato). Si dice "no column created_at", revisar `models.py` y `schema_contracts.py`. |
| `test_save_and_get_by_secret_key` | `SuperAdminModel` debe tener `secret_key = Column(...)`. `_to_entity` debe incluir `secret_key`. |
