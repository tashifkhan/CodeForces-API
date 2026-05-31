from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Dict, Any
from models.base import UserAllStats, UserInfo, RatingHistory, SolvedProblemsCount, ErrorResponse, UserActivityHeatmap
from models.unified import (
    UnifiedRating,
    UnifiedStats,
    UnifiedSummary,
    make_envelope,
)
from services import unified_mapper
from services.codeforces_service import (
    get_user_all_stats, get_user_info, get_user_rating,
    get_solved_problem_count, get_contests_participated_by_user,
    get_common_contests, get_user_activity_heatmap
)

router = APIRouter()


@router.get("/{userid}", responses={404: {"model": ErrorResponse}})
async def user_all_stats(userid: str = Path(..., description="Codeforces handle")):
    """Get comprehensive statistics for a Codeforces user."""
    stats = await get_user_all_stats(userid)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Stats not found for {userid}")
    summary = UnifiedSummary(
        totalSolved=stats.solved_problems_count,
        totalContests=stats.contests_count,
        currentRating=stats.rating,
        maxRating=stats.maxRating,
        rank=stats.rank,
    )
    return make_envelope(userid, summary, legacy=stats)


@router.get("/{userid}/basic", responses={404: {"model": ErrorResponse}}, deprecated=True)
async def user_basic_info(userid: str = Path(..., description="Codeforces handle")):
    """Get basic information about a Codeforces user. Prefer ``/{userid}/profile``."""
    user_info = await get_user_info([userid])
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    data = unified_mapper.profile_from(user_info[0], userid)
    return make_envelope(userid, data, legacy=UserInfo(**user_info[0]))


@router.get("/multi/{userids}", response_model=List[UserInfo], responses={404: {"model": ErrorResponse}})
async def users_info(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get information about multiple Codeforces users."""
    handles_list = [h.strip() for h in userids.replace(',', ';').split(';') if h.strip()]

    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    user_info = await get_user_info(handles_list)
    if not user_info:
        raise HTTPException(status_code=404, detail="User information not found")

    return user_info


@router.get("/{userid}/rating", responses={404: {"model": ErrorResponse}})
async def user_rating(userid: str = Path(..., description="Codeforces handle")):
    """Get rating history of a Codeforces user."""
    rating_history = await get_user_rating(userid)
    if rating_history is None:
        raise HTTPException(status_code=404, detail=f"Rating history not found for {userid}")
    ratings = [r.get("newRating") for r in rating_history if r.get("newRating") is not None]
    data = UnifiedRating(
        current=ratings[-1] if ratings else None,
        max=max(ratings) if ratings else None,
        history=[
            {
                "timestamp": r.get("ratingUpdateTimeSeconds"),
                "rating": r.get("newRating"),
                "contestName": r.get("contestName"),
            }
            for r in rating_history
        ],
    )
    legacy = {"ratingHistory": rating_history}
    return make_envelope(userid, data, legacy=legacy)


@router.get("/{userid}/solved", responses={404: {"model": ErrorResponse}}, deprecated=True)
async def solved_problems(userid: str = Path(..., description="Codeforces handle")):
    """Get the number of solved problems for a Codeforces user. Prefer ``/{userid}/stats``."""
    solved_count = await get_solved_problem_count(userid)
    if solved_count is None:
        raise HTTPException(status_code=404, detail=f"Solved problem count not found for {userid}")
    data = UnifiedStats(totalSolved=solved_count, byDifficulty={})
    return make_envelope(userid, data, legacy={"handle": userid, "count": solved_count})


@router.get("/{userid}/heatmap", responses={404: {"model": ErrorResponse}})
async def user_activity_heatmap(
    userid: str = Path(..., description="Codeforces handle"),
    days: int = Query(365, ge=1, le=3650, description="Number of trailing days to include"),
    year: int | None = Query(None, description="Full calendar year to include, for example 2026"),
):
    """Get daily submission activity for a Codeforces user."""
    heatmap = await get_user_activity_heatmap(userid, days, year)
    if heatmap is None:
        raise HTTPException(status_code=404, detail=f"Heatmap data not found for {userid}")
    data = unified_mapper.heatmap_from(heatmap)
    return make_envelope(userid, data, legacy=heatmap)


@router.get("/{userid}/contests", responses={404: {"model": ErrorResponse}})
async def contests_participated(userid: str = Path(..., description="Codeforces handle")):
    """Get contests participated by a Codeforces user."""
    contests = await get_contests_participated_by_user(userid)
    if not contests:
        raise HTTPException(status_code=404, detail=f"Contest participation data not found for {userid}")
    data = await unified_mapper.build_contests(userid)
    return make_envelope(userid, data, legacy={"handle": userid, "contests": list(contests)})


@router.get("/users/common-contests/{userids}", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def common_contests(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get common contests participated by multiple Codeforces users."""
    handles_list = [h.strip() for h in userids.replace(',', ';').split(';') if h.strip()]

    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    common = await get_common_contests(handles_list)
    return {"handles": handles_list, "common_contests": list(common)}
