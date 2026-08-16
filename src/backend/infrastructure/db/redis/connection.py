from redis.asyncio import Redis
from backend.infrastructure.db.redis.setting import settings

redis_client = Redis.from_url(settings.get_redis_url, decode_responses=True)





def get_redis():
    return redis_client