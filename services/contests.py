import asyncio
import time
from services.client import api


async def get_upcoming_contests(gym=False):
    return [c for c in await api('contest.list', gym=str(gym).lower())
            if c['phase'] == 'BEFORE' and c.get('startTimeSeconds', 0) > time.time()]


async def get_contests_participated_by_user(handle):
    return {s['contestId'] for s in await api('user.status', handle=handle) if 'contestId' in s}


async def get_common_contests(handles):
    results = await asyncio.gather(*(get_contests_participated_by_user(h) for h in handles))
    return results[0].intersection(*results[1:]) if results else set()
