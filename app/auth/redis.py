"""Optional Redis helpers for token blacklisting.

This module avoids hard failures when `aioredis` (or its
dependencies like distutils) are not available in the test
environment. In that case the functions become safe no-ops so
unit tests can run without a Redis instance.
"""
from app.core.config import get_settings

settings = get_settings()

try:
    import aioredis  # type: ignore
except Exception:
    aioredis = None


async def get_redis():
    """Return an aioredis Redis instance or None if unavailable."""
    if aioredis is None:
        return None

    if not hasattr(get_redis, "redis"):
        get_redis.redis = await aioredis.from_url(
            settings.REDIS_URL or "redis://localhost"
        )
    return get_redis.redis


async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the blacklist (no-op when redis unavailable)."""
    redis = await get_redis()
    if redis is None:
        return
    await redis.set(f"blacklist:{jti}", "1", ex=exp)


async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted (returns False if redis unavailable)."""
    redis = await get_redis()
    if redis is None:
        return False
    return await redis.exists(f"blacklist:{jti}")