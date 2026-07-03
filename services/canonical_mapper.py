"""Builds the canonical cross-platform card for CodeForces from the official API.

Profile/rating/rank come from ``user.info`` + ``user.rating``; solved count and
topic analysis are aggregated from ``user.status`` submissions; the heatmap reuses
the existing activity-heatmap builder. CodeForces has no public badges, so that
section is empty. See ../CANONICAL_SCHEMA.md.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from models.canonical.badges import Badges
from models.canonical.card import Card
from models.canonical.contests import ContestHistoryItem, Contests
from models.canonical.heatmap import HeatDay, Heatmap, YearContribution
from models.canonical.profile import Profile, Social
from models.canonical.rating import RatingPoint, Rating
from models.canonical.stats import TopicCount, Stats
from models.canonical.summary import Summary
from services.contests import get_contests_participated_by_user
from services.heatmap import get_user_activity_heatmap
from services.heatmap_window import window_heatmap
from services.rating import get_user_rating
from services.stats import get_solved_problem_count, get_solved_tags
from services.users import get_user_info


def _ts_to_date(timestamp) -> Optional[str]:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


def profile_from(info: Optional[dict], handle: str) -> Profile:
    info = info or {}
    name = " ".join(p for p in [info.get("firstName"), info.get("lastName")] if p).strip()
    return Profile(
        displayName=name or info.get("handle") or handle,
        username=info.get("handle") or handle,
        avatar=info.get("titlePhoto") or info.get("avatar"),
        country=info.get("country"),
        institution=info.get("organization"),
        social=Social(),
        verified=False,
    )


def stats_from(solved_count: int, tags: List[dict]) -> Stats:
    return Stats(
        totalSolved=solved_count or 0,
        byDifficulty={},
        topicAnalysis=[TopicCount(topic=t["topic"], count=t["count"]) for t in tags],
    )


def contests_from(info: Optional[dict], rating_history, contests_count: int) -> Contests:
    info = info or {}
    history = [
        ContestHistoryItem(
            name=entry.get("contestName"),
            date=_ts_to_date(entry.get("ratingUpdateTimeSeconds")),
            timestamp=entry.get("ratingUpdateTimeSeconds"),
            rating=entry.get("newRating"),
            ranking=entry.get("rank"),
        )
        for entry in (rating_history or [])
    ]
    return Contests(
        count=contests_count or len(history),
        rating=info.get("rating"),
        maxRating=info.get("maxRating"),
        rank=info.get("rank"),
        history=history,
    )


def rating_from(info: Optional[dict], rating_history) -> Rating:
    info = info or {}
    history = [
        RatingPoint(
            timestamp=entry.get("ratingUpdateTimeSeconds"),
            rating=entry.get("newRating"),
            contestName=entry.get("contestName"),
        )
        for entry in (rating_history or [])
    ]
    return Rating(current=info.get("rating"), max=info.get("maxRating"), history=history)


def _level(count: int, max_daily: int) -> int:
    if count <= 0 or max_daily <= 0:
        return 0
    return min(4, max(1, round((count / max_daily) * 4)))


def heatmap_from(heatmap) -> Heatmap:
    if heatmap is None:
        return Heatmap()

    days = heatmap.heatmap
    max_daily = max((d.submissions for d in days), default=0)
    yearly: dict = {}
    first = last = None
    for d in days:
        if d.submissions <= 0:
            continue
        year = int(d.date[:4])
        bucket = yearly.setdefault(year, {"totalSubmissions": 0, "activeDays": 0})
        bucket["totalSubmissions"] += d.submissions
        bucket["activeDays"] += 1
        first = d.date if first is None else min(first, d.date)
        last = d.date if last is None else max(last, d.date)

    return Heatmap(
        totalSubmissions=heatmap.total_submissions,
        totalActiveDays=heatmap.active_days,
        currentStreak=heatmap.current_streak,
        longestStreak=heatmap.longest_streak,
        maxDailySubmissions=max_daily,
        firstActiveDate=first,
        lastActiveDate=last,
        dailyContributions=[
            HeatDay(date=d.date, count=d.submissions, level=_level(d.submissions, max_daily))
            for d in days
            if d.submissions > 0
        ],
        yearlyContributions=[
            YearContribution(year=y, totalSubmissions=v["totalSubmissions"], activeDays=v["activeDays"])
            for y, v in sorted(yearly.items())
        ],
    )


def summary_from(card: Card) -> Summary:
    return Summary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=0,
    )


async def build_stats(handle: str) -> Stats:
    solved, tags = await asyncio.gather(
        get_solved_problem_count(handle),
        get_solved_tags(handle),
    )
    return stats_from(solved or 0, tags)


async def build_contests(handle: str) -> Contests:
    info, rating_history, contests = await asyncio.gather(
        get_user_info([handle]),
        get_user_rating(handle),
        get_contests_participated_by_user(handle),
    )
    return contests_from(info[0] if info else None, rating_history, len(contests or []))


async def build_rating(handle: str) -> Rating:
    info, rating_history = await asyncio.gather(
        get_user_info([handle]),
        get_user_rating(handle),
    )
    return rating_from(info[0] if info else None, rating_history)


async def build_profile(handle: str) -> Profile:
    info = await get_user_info([handle])
    return profile_from(info[0] if info else None, handle)


async def build_heatmap(handle: str, view: str = "all", year: int | None = None) -> Heatmap:
    # Fetch the full history and slice locally so every view goes through the
    # same windowing path; availableYears comes from the registration date.
    heatmap = await get_user_activity_heatmap(handle, days=None, year=None)
    available_years = heatmap.available_years if heatmap else None
    return window_heatmap(heatmap_from(heatmap), view, year, available_years=available_years)


async def build_card(handle: str) -> Card:
    info, rating_history, contests, solved, tags, heatmap = await asyncio.gather(
        get_user_info([handle]),
        get_user_rating(handle),
        get_contests_participated_by_user(handle),
        get_solved_problem_count(handle),
        get_solved_tags(handle),
        get_user_activity_heatmap(handle, days=None, year=None),
    )
    info0 = info[0] if info else None
    available_years = heatmap.available_years if heatmap else None
    return Card(
        username=handle,
        profile=profile_from(info0, handle),
        stats=stats_from(solved or 0, tags),
        contests=contests_from(info0, rating_history, len(contests or [])),
        rating=rating_from(info0, rating_history),
        heatmap=window_heatmap(heatmap_from(heatmap), "all", None, available_years=available_years),
        badges=Badges(),
    )
