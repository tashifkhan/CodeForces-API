"""Builds the unified cross-platform card for CodeForces from the official API.

Profile/rating/rank come from ``user.info`` + ``user.rating``; solved count and
topic analysis are aggregated from ``user.status`` submissions; the heatmap reuses
the existing activity-heatmap builder. CodeForces has no public badges, so that
section is empty. See ../UNIFIED_SCHEMA.md.
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

from models.unified import (
    ContestHistoryItem,
    HeatDay,
    RatingPoint,
    TopicCount,
    UnifiedBadges,
    UnifiedCard,
    UnifiedContests,
    UnifiedHeatmap,
    UnifiedProfile,
    UnifiedRating,
    UnifiedSocial,
    UnifiedStats,
    UnifiedSummary,
    YearContribution,
)
from services import codeforces_service as cf


def _ts_to_date(timestamp) -> Optional[str]:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


def profile_from(info: Optional[dict], handle: str) -> UnifiedProfile:
    info = info or {}
    name = " ".join(p for p in [info.get("firstName"), info.get("lastName")] if p).strip()
    return UnifiedProfile(
        displayName=name or info.get("handle") or handle,
        username=info.get("handle") or handle,
        avatar=info.get("titlePhoto") or info.get("avatar"),
        country=info.get("country"),
        institution=info.get("organization"),
        social=UnifiedSocial(),
        verified=False,
    )


def stats_from(solved_count: int, tags: List[dict]) -> UnifiedStats:
    return UnifiedStats(
        totalSolved=solved_count or 0,
        byDifficulty={},
        topicAnalysis=[TopicCount(topic=t["topic"], count=t["count"]) for t in tags],
    )


def contests_from(info: Optional[dict], rating_history, contests_count: int) -> UnifiedContests:
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
    return UnifiedContests(
        count=contests_count or len(history),
        rating=info.get("rating"),
        maxRating=info.get("maxRating"),
        rank=info.get("rank"),
        history=history,
    )


def rating_from(info: Optional[dict], rating_history) -> UnifiedRating:
    info = info or {}
    history = [
        RatingPoint(
            timestamp=entry.get("ratingUpdateTimeSeconds"),
            rating=entry.get("newRating"),
            contestName=entry.get("contestName"),
        )
        for entry in (rating_history or [])
    ]
    return UnifiedRating(current=info.get("rating"), max=info.get("maxRating"), history=history)


def _level(count: int, max_daily: int) -> int:
    if count <= 0 or max_daily <= 0:
        return 0
    return min(4, max(1, round((count / max_daily) * 4)))


def heatmap_from(heatmap) -> UnifiedHeatmap:
    if heatmap is None:
        return UnifiedHeatmap()

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

    return UnifiedHeatmap(
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


def summary_from(card: UnifiedCard) -> UnifiedSummary:
    return UnifiedSummary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=0,
    )


async def build_stats(handle: str) -> UnifiedStats:
    solved, tags = await asyncio.gather(
        cf.get_solved_problem_count(handle),
        cf.get_solved_tags(handle),
    )
    return stats_from(solved or 0, tags)


async def build_contests(handle: str) -> UnifiedContests:
    info, rating_history, contests = await asyncio.gather(
        cf.get_user_info([handle]),
        cf.get_user_rating(handle),
        cf.get_contests_participated_by_user(handle),
    )
    return contests_from(info[0] if info else None, rating_history, len(contests or []))


async def build_rating(handle: str) -> UnifiedRating:
    info, rating_history = await asyncio.gather(
        cf.get_user_info([handle]),
        cf.get_user_rating(handle),
    )
    return rating_from(info[0] if info else None, rating_history)


async def build_profile(handle: str) -> UnifiedProfile:
    info = await cf.get_user_info([handle])
    return profile_from(info[0] if info else None, handle)


async def build_heatmap(handle: str) -> UnifiedHeatmap:
    heatmap = await cf.get_user_activity_heatmap(handle, 365, None)
    return heatmap_from(heatmap)


async def build_card(handle: str) -> UnifiedCard:
    info, rating_history, contests, solved, tags, heatmap = await asyncio.gather(
        cf.get_user_info([handle]),
        cf.get_user_rating(handle),
        cf.get_contests_participated_by_user(handle),
        cf.get_solved_problem_count(handle),
        cf.get_solved_tags(handle),
        cf.get_user_activity_heatmap(handle, 365, None),
    )
    info0 = info[0] if info else None
    return UnifiedCard(
        username=handle,
        profile=profile_from(info0, handle),
        stats=stats_from(solved or 0, tags),
        contests=contests_from(info0, rating_history, len(contests or [])),
        rating=rating_from(info0, rating_history),
        heatmap=heatmap_from(heatmap),
        badges=UnifiedBadges(),
    )
