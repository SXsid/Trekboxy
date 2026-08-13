import json

import extensions
from logger import get_logger

logger = get_logger(__name__)

TTL_TREKS_ALL = 5 * 60
TTL_TREK_ONE = 10 * 60
TTL_ADMIN_STATS = 60


def cache_get(key: str):
    try:
        data = extensions.redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        logger.warning("Cache GET failed for key=%r — Redis may be unavailable", key)
    return None


def cache_set(key: str, value, ttl: int):
    try:
        extensions.redis_client.setex(name=key, time=ttl, value=json.dumps(value))
        logger.debug("Cache SET key=%r ttl=%ss", key, ttl)
    except Exception:
        logger.warning("Cache SET failed for key=%r — continuing without cache", key)


def cache_delete(*keys: str):
    try:
        if keys:
            extensions.redis_client.delete(*keys)
            logger.debug("Cache DELETE keys=%s", keys)
    except Exception:
        logger.warning("Cache DELETE failed for keys=%s — TTL will expire it", keys)
