import json

import extensions

TTL_TREKS_ALL = 5 * 60
TTL_TREK_ONE = 10 * 60
TTL_ADMIN_STATS = 60


def cache_get(key: str):
    try:
        data = extensions.redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass  # INFO: jussst tereatd as cache miss
    return None


def cache_set(key: str, value, ttl: int):
    try:
        extensions.redis_client.setex(name=key, time=ttl, value=json.dumps(value))
    except Exception:
        pass


def cache_delete(*keys: str):
    try:
        if keys:
            extensions.redis_client.delete(*keys)
    except Exception:
        pass  # eventlly ttl will remove it only
