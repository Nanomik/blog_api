import redis
import json
from app.config import settings


redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cached_post(post_id: int):
    data = redis_client.get(f"post:{post_id}")
    if data:
        return json.loads(data)
    return None


def set_cached_post(post_id: int, post_data: dict):
    redis_client.setex(
        f"post:{post_id}",
        settings.CACHE_TTL,
        json.dumps(post_data, default=str),
    )


def delete_cached_post(post_id: int):
    redis_client.delete(f"post:{post_id}")
