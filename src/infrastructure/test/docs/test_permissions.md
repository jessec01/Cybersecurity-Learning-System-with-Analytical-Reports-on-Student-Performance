# test_permissions.py

## Archivos que depura
- `domain/value_objects/permissions.py` → `Permissions`, `Resource`, `Action`, `permission()`
- `infrastructure/auth/dependencies.py` → `require_permission()` (indirectamente, via logica pura)

## Flujo que traza
Pruebas unitarias del sistema de permisos: constantes, formato `resource:action` y logica de chequeo de permisos en listas. No requiere DB ni FastAPI.

### TestPermissionValueObjects (5 tests)
| Test | Que valida |
|------|-----------|
| `test_permission_format` | `permission("course", "create")` produce `"course:create"` |
| `test_resource_constants` | `Resource.COURSE`, `Resource.REPORT`, `Resource.BRANDING` tienen los valores correctos |
| `test_action_constants` | `Action.CREATE`, `Action.APPROVE`, `Action.EXPORT` tienen los valores correctos |
| `test_permissions_class_all_valid` | Todas las constantes de la clase `Permissions` tienen el formato `resource:action` esperado |
| `test_permission_string_in_list_check` | El operador `in` funciona sobre listas de strings de permisos |

### TestRequirePermissionLogic (2 tests)
| Test | Que valida |
|------|-----------|
| `test_permission_found` | `"course:create" in user_perms` → True con `user_perms = ["course:create", "user:read"]` |
| `test_permission_not_found` | `"course:delete" not in user_perms` → True con `user_perms = ["user:read"]` |

## Resultado esperado
7/7 tests pasan.

## Casos criticos si falla
| Test que falla | Que reparar |
|----------------|-------------|
| `test_permission_format` | `permission()` debe usar `f"{resource}:{action}"` exactamente |
| `test_resource_constants` | Verificar que las constantes de `Resource` heredan de `str` y tienen valores literales correctos |
| `test_permissions_class_all_valid` | Si falla una constante, revisar que usa `Resource.*` y `Action.*` correctos, no strings sueltos |
| `test_permission_string_in_list_check` | Si `in` no funciona, verificar que las constantes son `str`, no objetos custom |
