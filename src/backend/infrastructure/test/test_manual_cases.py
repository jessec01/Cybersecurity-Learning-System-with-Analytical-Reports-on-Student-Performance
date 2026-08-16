"""
CASOS DE PRUEBA MANUALES - Flujos Complejos
============================================
Ejecutar con el servidor corriendo: uvicorn main:app

1. FLUJO COMPLETO DE ROLES
   Proposito: Verificar que roles y permisos se consultan correctamente via DB.
   La creacion de roles/permisos se hace directo en DB por ahora (seed data).

   Pasos:
   a) Insertar un role en DB:   INSERT INTO roles (name, is_active) VALUES ('teacher', true);
   b) Insertar un permiso:      INSERT INTO permissions (codename, resource, action, description, is_active)
                                 VALUES ('course:create', 'course', 'create', 'Crear cursos', true);
   c) Asignar permiso a rol:    INSERT INTO rol_permissions (id_rol, id_permission, is_active) VALUES (1, 1, true);
   d) Asignar rol a persona:    INSERT INTO rol_persons (id_person, id_rol, is_active) VALUES (1, 1, true);
   e) Loguearse y verificar que get_current_user carga los permisos.
   Resultado esperado: user.permissions contiene ['course:create'].

2. FLUJO DE REDIS + TOKEN
   Proposito: Verificar que la sesion se cachea y se recupera de Redis.

   Pasos:
   a) Asegurar que Redis este corriendo.
   b) Loguearse → obtener token.
   c) Verificar sesion en Redis: redis-cli GET "session:{user_id}"
   d) Loguearse de nuevo → Redis debe devolver la sesion sin tocar DB.
   e) Invalidar sesion: redis-cli DEL "session:{user_id}"
   f) Loguearse de nuevo → debe pegarle a DB de nuevo.
   Resultado esperado: la cache funciona, el TTL se respeta.

3. FLUJO DE get_current_user
   Proposito: Verificar que la dependency carga usuario + persona + roles + permisos.

   Pasos:
   a) Crear usuario + persona + rol + permisos (manual via DB).
   b) Loguearse y guardar el token.
   c) Llamar a un endpoint protegido con el token.
   d) Verificar que el endpoint retorna datos del usuario (no 401 ni 403).
   e) Llamar al mismo endpoint SIN token → debe retornar 401.
   f) Llamar a un endpoint que requiera un permiso que el usuario NO tiene → 403.
   Resultado esperado: 200 con token valido + permisos correctos, 401 sin token, 403 sin permiso.

4. PRUEBA DE SANIDAD (SMOKE)
   Proposito: Verificar que el sistema levanta y los endpoints responden.

   Pasos:
   a) Levantar servidor.
   b) GET / → 200.
   c) GET /docs → 200.
   d) GET /openapi.json → 200, contiene /auth/login.
   Resultado esperado: todo 200.

5. PRUEBA EXPLORATORIA (AD-HOC)
   Proposito: Romper el sistema con inputs inesperados.

   Pasos:
   a) POST /auth/login con body vacio → 422 (validation error).
   b) POST /auth/register con email invalido → 422.
   c) POST /auth/login con token expirado → 401.
   d) POST /auth/super-admin/login con secret_key vacio → 401.
   Resultado esperado: el sistema no crashea, devuelve errores HTTP apropiados.

6. ANALISIS DE LOGS REACTIVO
   Proposito: Verificar que los errores se registran.

   Pasos:
   a) Provocar un 401 intencional.
   b) Revisar logs del servidor.
   c) Verificar que el log contiene el intento fallido.
   Resultado esperado: logs contienen detalles del error, no exponen secretos ni passwords.
"""

# ---------------------------------------------------------------------------
# Tests automatizados para los flujos complejos (requieren DB + Redis real)
# ---------------------------------------------------------------------------

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import pytest


@pytest.mark.integration
class TestComplexFlows:
    """
    Estos tests asumen que hay una DB real con datos seed.
    Se marcan con @pytest.mark.integration para filtrarlos.
    Ejecutar con: pytest -m integration
    """

    @pytest.mark.skip(reason="Requiere DB real con seed data de roles y permisos")
    def test_role_based_access_flow(self):
        pass

    @pytest.mark.skip(reason="Requiere Redis corriendo")
    def test_redis_session_cache_flow(self):
        pass

    @pytest.mark.skip(reason="Requiere servidor corriendo y seed data")
    def test_get_current_user_full_flow(self):
        pass
