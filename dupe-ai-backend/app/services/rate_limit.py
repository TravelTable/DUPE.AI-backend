import time
import redis
from app.config import settings

_redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def token_bucket(key: str, limit: int, window_sec: int) -> bool:
    """
    Simple token bucket. Return True if allowed, False if over limit.
    """
    now = int(time.time())
    pipe = _redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_sec + 1)
    _, _, count, _ = pipe.execute()
    return count <= limit
