import asyncio
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Set

import aiohttp

from models.heatmap import HeatmapDay, UserActivityHeatmap

async def get_user_info(handles: List[str]):
    """Fetches information about Codeforces users."""
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data["status"] == "OK":
                    return data["result"]
                return None
        except aiohttp.ClientError:
            return None

def _build_heatmap_response(
    handle: str,
    submissions: List[dict],
    start_date: date,
    end_date: date,
    mode: str,
    available_years: List[int],
    year: Optional[int] = None,
) -> UserActivityHeatmap:
    activity_by_day = defaultdict(lambda: {"submissions": 0, "accepted": 0})

    for submission in submissions:
        created_at = datetime.fromtimestamp(
            submission["creationTimeSeconds"],
            tz=timezone.utc,
        ).date()

        if created_at < start_date or created_at > end_date:
            continue

        day_key = created_at.isoformat()
        activity_by_day[day_key]["submissions"] += 1
        if submission.get("verdict") == "OK":
            activity_by_day[day_key]["accepted"] += 1

    days = (end_date - start_date).days + 1
    heatmap = []
    current_streak = 0
    longest_streak = 0
    running_streak = 0
    total_submissions = 0
    total_accepted = 0
    active_days = 0

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_key = current_date.isoformat()
        day_activity = activity_by_day[day_key]
        submissions_count = day_activity["submissions"]
        accepted = day_activity["accepted"]

        if submissions_count > 0:
            active_days += 1
            running_streak += 1
            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 0

        total_submissions += submissions_count
        total_accepted += accepted
        heatmap.append(
            HeatmapDay(
                date=day_key,
                submissions=submissions_count,
                accepted=accepted,
            )
        )

    if end_date == datetime.now(timezone.utc).date():
        for day in reversed(heatmap):
            if day.submissions == 0:
                break
            current_streak += 1

    return UserActivityHeatmap(
        handle=handle,
        mode=mode,
        days=days,
        year=year,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        available_years=available_years,
        total_submissions=total_submissions,
        total_accepted=total_accepted,
        active_days=active_days,
        current_streak=current_streak,
        longest_streak=longest_streak,
        heatmap=heatmap,
    )

async def get_user_activity_heatmap(
    handle: str,
    days: Optional[int] = 365,
    year: Optional[int] = None,
) -> Optional[UserActivityHeatmap]:
    """Builds daily submission activity for a user's heatmap.

    ``year`` restricts to a calendar year; otherwise ``days`` selects a trailing
    window, and ``days=None`` returns the full history since registration.
    """
    user_info = await get_user_info([handle])
    if not user_info:
        return None

    registered_at = user_info[0].get("registrationTimeSeconds")
    if registered_at is None:
        return None

    registration_date = datetime.fromtimestamp(registered_at, tz=timezone.utc).date()
    today = datetime.now(timezone.utc).date()
    available_years = list(range(today.year, registration_date.year - 1, -1))

    if year is not None:
        if year < registration_date.year or year > today.year:
            return None
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        if year == registration_date.year and registration_date > start_date:
            start_date = registration_date
        if year == today.year and today < end_date:
            end_date = today
        mode = "calendar_year"
    elif days is None:
        end_date = today
        start_date = registration_date
        mode = "all"
    else:
        end_date = today
        start_date = end_date - timedelta(days=days - 1)
        if start_date < registration_date:
            start_date = registration_date
        mode = "trailing_days"

    url = f"https://codeforces.com/api/user.status?handle={handle}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data["status"] != "OK":
                    return None

                return _build_heatmap_response(
                    handle=handle,
                    submissions=data["result"],
                    start_date=start_date,
                    end_date=end_date,
                    mode=mode,
                    available_years=available_years,
                    year=year,
                )
        except (aiohttp.ClientError, KeyError, TypeError, ValueError):
            return None
