# test_contract_full_flow.py

## Archivos que depura
- `infrastructure/contracts/schema_contracts.py` → contrato completo
- `infrastructure/contracts/schema_validator.py` → `build_table()`, `load_contract()`, `contract_enforce_operations()`
- `infrastructure/db/postgres/models.py` → todos los modelos ORM de auth
- `infrastructure/db/postgres/repositories/` → User, Person, Role, SuperAdmin
- `application/use_cases/auth_use_cases.py` → LoginUseCase, SuperAdminLoginUseCase
- `application/dto/auth_dto.py` → DTOs

## Flujo que traza
Es el test mas pesado e integrador. Construye TODAS las tablas del contrato real (`schema_contracts.py`) en SQLite en memoria, siembra roles + permisos, y ejecuta el flujo completo de negocio de punta a punta. Verifica que contrato, ORM, repositorios y use cases funcionan juntos.

### Fixtures
| Fixture | Scope | Proposito |
|---------|-------|-----------|
| `contract_engine` | module | Crea motor SQLite y construye todas las tablas desde el contrato con `build_table()` |
| `contract_db` | function | Sesion fresca por test sobre las tablas del contrato |

### TestContractValidation (5 tests)
| Test | Que valida |
|------|-----------|
| `test_contract_loads` | `load_contract()` carga el dict con `metadata`, `tables`, `rules`. El nombre es `cybersecurity_learning_system`. |
| `test_contract_has_required_tables` | Las 7 tablas del core de auth existen en `contract["tables"]` |
| `test_contract_rules` | `allow_new_tables=False`, `allow_delete_tables=False`, `allow_new_columns=True` |
| `test_blocked_operations` | `contract_enforce_operations()` detecta DELETE, DROP TABLE, CREATE TABLE como bloqueadas |
| `test_tables_built_in_memory` | `contract_engine` creo todas las tablas del contrato en SQLite |

### TestFullBusinessFlow (7 tests)
| Test | Que valida |
|------|-----------|
| `test_seed_roles_and_permissions` | Inserta 3 roles + 9 permisos + 10 asignaciones rol-permiso sobre tablas del contrato |
| `test_full_user_registration_and_role_assignment` | Crea User → Person → asigna rol teacher → verifica permisos via SQL pura |
| `test_repository_layer_with_contract` | UserRepo + PersonRepo funcionan sobre tablas generadas del contrato |
| `test_role_repository_with_contract` | RoleRepository consulta roles y permisos sobre tablas del contrato |
| `test_use_case_flow_with_contract` | Registro manual + LoginUseCase login exitoso + login fallido lanza UnauthorizedError |
| `test_super_admin_flow_with_contract` | SuperAdminRepo save + SuperAdminLoginUseCase login exitoso + secret key incorrecta |
| `test_permission_authorization_logic` | Estudiante tiene `course:read` pero NO `course:create`, `course:delete`, `report:export` |

### TestContractVsORM (2 tests)
| Test | Que valida |
|------|-----------|
| `test_all_contract_tables_have_orm_model` | Las 7 tablas del core auth tienen modelo ORM declarado en `models.py` |
| `test_contract_columns_in_orm` | Columnas clave (`username`, `password`, `codename`, `resource`, `action`) existen en los modelos ORM |

## Resultado esperado
14/14 tests pasan.

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_contract_loads` | `schema_contracts.py` importa correctamente. `contract_data` es un dict. |
| `test_tables_built_in_memory` | `build_table()` convierte todas las tablas. Si falta una, el contrato y el ORM estan desincronizados. |
| `test_seed_roles_and_permissions` | Los modelos ORM (`RoleModel`, `PermissionModel`, `RolPermissionModel`) deben tener las columnas `created_at` y FK correctas. Si falla `NOT NULL constraint failed: rol_permissions.created_at`, pasar `created_at` al crear las instancias. |
| `test_role_repository_with_contract` | `RoleRepository.get_roles_for_person()` debe usar JOIN correcto entre `rol_persons` y `roles`. |
| `test_use_case_flow_with_contract` | El hash bcrypt debe ser compatible. Si `bcrypt` es >= 5.0, instalar `bcrypt==4.0.1`. |
| `test_permission_authorization_logic` | Verificar que `RolPersonModel.is_active` y `RolPermissionModel.is_active` sean `True` en los JOINs. |
| `test_all_contract_tables_have_orm_model` | Si hay tablas del contrato sin modelo, agregar el modelo ORM correspondiente en `models.py`. |
