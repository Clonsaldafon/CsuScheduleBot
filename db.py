from redis.asyncio import StrictRedis


redis_client = StrictRedis.from_url(
    "redis://localhost:6379",
    db=0,
    encoding="utf-8",
    decode_responses=True
)