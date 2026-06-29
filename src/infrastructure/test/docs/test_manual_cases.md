# test_manual_cases.py

## Archivos que depura
- `infrastructure/auth/dependencies.py` → `get_current_user`, `require_permission`
- `infrastructure/auth/session_store.py` → Redis cache
- `infrastructure/db/postgres/repositories/role_repository.py`
- Todo el sistema en modo integrado

## Flujo que traza
Documenta **casos de prueba manuales** para flujos que no se pueden automatizar facilmente (requieren DB real con seed data, Redis corriendo, o interaccion humana). Los tests automatizados estan marcados `@pytest.mark.skip` y requieren infraestructura real.

### Casos manuales documentados

#### 1. Flujo completo de roles
| Paso | Accion |
|------|--------|
| 1 | Insertar rol: `INSERT INTO roles (name, is_active) VALUES ('teacher', true)` |
| 2 | Insertar permiso: `INSERT INTO permissions (codename, resource, action, description, is_active) VALUES ('course:create', 'course', 'create', 'Crear cursos', true)` |
| 3 | Asignar permiso a rol: `INSERT INTO rol_permissions (id_rol, id_permission, is_active) VALUES (1, 1, true)` |
| 4 | Asignar rol a persona: `INSERT INTO rol_persons (id_person, id_rol, is_active) VALUES (1, 1, true)` |
| 5 | Login → verificar `user.permissions` contiene `course:create` |
| **Esperado** | `get_current_user()` carga permisos del rol via DB |

#### 2. Flujo de Redis + token
| Paso | Accion |
|------|--------|
| 1 | Asegurar Redis corriendo |
| 2 | Login → obtener access_token |
| 3 | Verificar sesion en Redis: `redis-cli GET "session:{user_id}"` |
| 4 | Segundo login → Redis cache hit, sin consulta a DB |
| 5 | Invalidar sesion: `redis-cli DEL "session:{user_id}"` |
| 6 | Tercer login → cache miss, consulta DB de nuevo |
| **Esperado** | Cache funciona, TTL se respeta |

#### 3. Flujo de get_current_user
| Paso | Accion |
|------|--------|
| 1 | Crear usuario + persona + rol + permisos (seed data) |
| 2 | Login → obtener token |
| 3 | Llamar endpoint protegido con token → 200 |
| 4 | Llamar endpoint protegido SIN token → 401 |
| 5 | Llamar endpoint que requiere permiso que el usuario NO tiene → 403 |
| **Esperado** | 200 con token valido + permisos, 401 sin token, 403 sin permiso |

#### 4. Prueba de sanidad (smoke)
| Paso | Accion |
|------|--------|
| 1 | Levantar servidor |
| 2 | `GET /` → 200 |
| 3 | `GET /docs` → 200 |
| 4 | `GET /openapi.json` → 200, contiene `/auth/login` |
| **Esperado** | Todo 200 |

#### 5. Prueba exploratoria (ad-hoc)
| Paso | Accion |
|------|--------|
| 1 | `POST /auth/login` con body vacio → 422 |
| 2 | `POST /auth/register` con email invalido → 422 |
| 3 | `POST /auth/login` con token expirado → 401 |
| 4 | `POST /auth/super-admin/login` con secret_key vacio → 401 |
| **Esperado** | El sistema no crashea, devuelve errores HTTP apropiados |

### Tests automatizados (skip)
| Test | Razón del skip |
|------|---------------|
| `test_role_based_access_flow` | Requiere DB real con seed data de roles y permisos |
| `test_redis_session_cache_flow` | Requiere Redis corriendo |
| `test_get_current_user_full_flow` | Requiere servidor corriendo y seed data |

## Casos criticos si falla
| Flujo manual que falla | Que investigar |
|------------------------|---------------|
| Roles no cargan permisos | `RoleRepository.get_permissions_for_person()` — revisar JOINs y filtros `is_active` |
| Redis no cachea | Verificar `session_store.cache_session()` se llama en login. Verificar Redis esta corriendo. |
| Endpoint protegido no da 401 sin token | `oauth2_scheme` no configurado en el router. `Depends(get_current_user)` faltante. |
| Endpoint protegido no da 403 sin permiso | `require_permission()` no lanza `ForbiddenError` o el handler no lo captura. |
