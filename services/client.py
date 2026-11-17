"""Cached Codeforces sources shared by canonical and legacy views."""
import asyncio
import json

import httpx
from fastapi import HTTPException

from core.cache import command
from core.runtime import http_client, remaining
from core.source import source

API_URL = 'https://codeforces.com/api/'
# Time kept back from the request budget so a failed fetch can still fall back
# to stale data and write a response.
RESPONSE_RESERVE = 0.5

SLOT = """
local t=redis.call('TIME')
local now=tonumber(t[1])*1000+math.floor(tonumber(t[2])/1000)
local next=math.max(now,tonumber(redis.call('GET',KEYS[1]) or now))
if next-now>tonumber(ARGV[1]) then return -1 end
redis.call('SET',KEYS[1],next+2000,'PX',10000)
return next-now
"""


def _parse(response):
    """Map a Codeforces reply to its result, or to a controlled HTTP error."""
    try:
        data = response.json()
    except ValueError:
        data = None
    if not isinstance(data, dict):
        raise HTTPException(503 if response.status_code in (429, 503) else 502,
                            'Invalid Codeforces upstream response')
    if response.status_code == 200 and data.get('status') == 'OK' and 'result' in data:
        return data['result']
    comment = str(data.get('comment', '')).lower()
    # Codeforces answers an unknown handle with HTTP 400 and status FAILED.
    if 'not found' in comment:
        raise HTTPException(404, 'User not found')
    if response.status_code in (429, 503) or 'limit exceeded' in comment:
        raise HTTPException(503, 'Codeforces upstream busy', headers={'Retry-After': '2'})
    raise HTTPException(502, 'Codeforces upstream rejected request')


async def _fetch(method, params):
    delay = await command('eval', SLOT, 1, 'cf:upstream:slot', max(0, int((remaining() - 2) * 1000)))
    if delay is not None:
        if int(delay) < 0:
            raise HTTPException(503, 'Codeforces upstream busy', headers={'Retry-After': '2'})
        await asyncio.sleep(int(delay) / 1000)

    async def get():
        async with http_client() as client:
            return await client.get(API_URL + method, params=params, timeout=min(4, remaining()))

    # httpx timeouts are per phase, so a trickling body could outlive them.
    # This bounds the whole exchange inside the request budget.
    budget = remaining() - RESPONSE_RESERVE
    if budget <= 0:
        raise HTTPException(504, 'Codeforces upstream timed out')
    try:
        response = await asyncio.wait_for(get(), budget)
    except (asyncio.TimeoutError, httpx.TimeoutException) as exc:
        raise HTTPException(504, 'Codeforces upstream timed out') from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, 'Codeforces upstream unavailable') from exc
    return _parse(response)


async def api(method, **params):
    """One upstream call per (method, params) per request, cached with stale fallback."""
    key = 'cf:' + json.dumps([method, params], sort_keys=True)
    return await source(key, lambda: _fetch(method, params), ttl=300, stale_ttl=3600)
