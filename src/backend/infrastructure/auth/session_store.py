import json
# pyrefly: ignore [missing-import]
from backend.infrastructure.db.redis.connection import get_redis

async def cache_session(user_id: int, session_data: dict, ttl: int = 1800):
    """cachea la sesion del usuario"""
    redis = get_redis()
    await redis.setex(f"session:{user_id}", ttl, json.dumps(session_data))

async def get_cached_session(user_id: int) -> dict | None:
    """obtiene la sesion del usuario"""
    redis = get_redis()
    data = await redis.get(f"session:{user_id}")
    return json.loads(data) if data else None
async def invalidate_session(user_id: int):
    """invalida la sesion del usuario"""
    redis = get_redis()
    await redis.delete(f"session:{user_id}")