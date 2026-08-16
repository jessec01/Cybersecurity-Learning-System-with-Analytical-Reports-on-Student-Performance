import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from sqlalchemy import text
from backend.infrastructure.db.postgres.setting import settings as postgres_settings
from backend.infrastructure.db.redis.setting import settings as redis_settings
from backend.infrastructure.db.postgres.connection import engine
from backend.infrastructure.db.redis.connection import redis_client
import pytest

def test_configuracion():
    print("\n--- 🔍 Verificando Variables de Entorno ---")
    print(f"Postgres Host: {postgres_settings.POSTGRES_HOST} | Puerto: {postgres_settings.POSTGRES_PORT} | BD: {postgres_settings.POSTGRES_DB}")
    print(f"Redis Host:    {redis_settings.REDIS_HOST} | Puerto: {redis_settings.REDIS_PORT}")
    print("-------------------------------------------\n")

def test_postgres():
    print("⏳ Probando conexión a PostgreSQL...")
    try:
        # Intentamos abrir una conexión real y ejecutar un query muy simple
        with engine.connect() as conexion:
            resultado = conexion.execute(text("SELECT version();"))
            version = resultado.scalar()
            print("✅ PostgreSQL: ¡Conectado exitosamente!")
            print(f"   ℹ️  Detalles: {version[:50]}...\n")
    except Exception as e:
        print("❌ PostgreSQL: Error en la conexión.")
        print(f"   ⚠️  Detalle del error: {e}\n")

@pytest.mark.asyncio
async def test_redis():
    print("⏳ Probando conexión a Redis...")
    try:
        # Enviamos un PING asíncrono al servidor de Redis
        respuesta = await redis_client.ping()
        if respuesta:
            print("✅ Redis: ¡Conectado exitosamente! (PONG recibido)\n")
    except Exception as e:
        print("❌ Redis: Error en la conexión.")
        print(f"   ⚠️  Detalle del error: {e}\n")

async def main():
    test_configuracion()
    test_postgres()
    await test_redis()

if __name__ == "__main__":
    # Necesitamos asyncio.run() porque Redis se configuró de forma asíncrona
    asyncio.run(main())