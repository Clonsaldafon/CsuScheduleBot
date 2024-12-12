import os

from dotenv import load_dotenv
from redis.asyncio import StrictRedis


load_dotenv()

redis_client = StrictRedis.from_url(
    url=f"redis://{os.getenv("REDIS_HOST")}:6379",
    db=0,
    encoding="utf-8",
    decode_responses=True
)
