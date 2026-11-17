"""Source cache with request deduplication, owner-safe leases and stale fallback."""
import asyncio
import hashlib
import time
import uuid

from fastapi import HTTPException

from core.cache import command, get_json, redis_enabled, set_json
from core.runtime import once, state

RELEASE = "if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) end return 0"


def _mark_stale(cached):
    current = state.get()
    if current:
        current.meta['source'] = {'status': 'stale', 'updatedAt': cached['at']}


async def source(key, producer, ttl=300, stale_ttl=3600):
    key = 'source:v1:' + hashlib.sha256(key.encode()).hexdigest()

    async def load():
        cached = await get_json(key)
        if not (isinstance(cached, dict) and 'at' in cached and 'data' in cached):
            cached = None
        if cached and time.time() - cached['at'] < ttl:
            return cached['data']
        store = redis_enabled()
        owner = uuid.uuid4().hex
        # Keyword arguments: redis-py's positional order is (value, ex, px, nx).
        locked = await command('set', key + ':lease', owner, ex=10, nx=True) if store else None
        if store and not locked:
            if cached:
                _mark_stale(cached)
                return cached['data']
            # Bounded coalescing. A failed cache must not cause an unbounded wait.
            for _ in range(3):
                await asyncio.sleep(.05)
                shared = await get_json(key)
                if isinstance(shared, dict) and 'data' in shared:
                    return shared['data']
        try:
            data = await producer()
        except (HTTPException, asyncio.TimeoutError):
            if cached:
                _mark_stale(cached)
                return cached['data']
            raise
        else:
            await set_json(key, {'at': time.time(), 'data': data}, stale_ttl)
            return data
        finally:
            if locked:
                await command('eval', RELEASE, 1, key + ':lease', owner)

    return await once(key, load)
