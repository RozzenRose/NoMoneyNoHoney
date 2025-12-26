import redis.asyncio as redis
from app.config import settings


class Redis:
    _redis = None

    @classmethod
    async def get_redis(cls):
        if cls._redis is None:
            cls._redis = redis.from_url(settings.redis_url, decode_responses=True)
        return cls._redis