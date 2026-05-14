import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from infrastructure.db.postgres.connection import engine
from infrastructure.db.redis.connection import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - verificar conexión
    logging.info("🚀 Iniciando aplicación...")
    
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logging.info("✅ PostgreSQL conectado correctamente")
    
    await redis_client.ping()
    logging.info("✅ Redis conectado correctamente")
    
    app.state.db = engine
    app.state.redis = redis_client
    
    logging.info("🎉 Servidor listo para recibir peticiones")
    
    yield
    
    # Shutdown
    logging.info("🛑 Cerrando conexiones...")
    engine.dispose()
    await redis_client.aclose()
    logging.info("✅ Conexiones cerradas correctamente")