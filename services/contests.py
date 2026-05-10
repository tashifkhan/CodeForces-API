import asyncio
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Set

import aiohttp


async def get_upcoming_contests(gym: bool = False):
    """Fetches a list of upcoming contests."""
    url = f"https://codeforces.com/api/contest.list?gym={str(gym).lower()}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data["status"] == "OK":
                    current_time = time.time()
                    return [c for c in data["result"] 
                           if c["phase"] == "BEFORE" and c["startTimeSeconds"] > current_time]
                return None
        except aiohttp.ClientError:
            return None

async def get_contests_participated_by_user(handle: str) -> Set[int]:
    """Gets contests participated in by a user."""
    await asyncio.sleep(2)  # Rate limit
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data["status"] == "OK":
                    return {s["contestId"] for s in data["result"] if "contestId" in s}
                return set()
        except aiohttp.ClientError:
            return set()

async def get_common_contests(handles: List[str]) -> Set[int]:
    """Gets common contests for multiple users."""
    if not handles:
        return set()

    all_contests = []
    for handle in handles:
        contests = await get_contests_participated_by_user(handle)
        if not contests:
            return set()
        all_contests.append(contests)

    return all_contests[0].intersection(*all_contests[1:])
