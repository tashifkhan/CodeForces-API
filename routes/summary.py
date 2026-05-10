from fastapi import APIRouter, HTTPException, Path

from models.canonical import Summary, make_envelope
from services.users import get_user_all_stats


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}")
async def get_summary(userid: str = Path(..., description="Codeforces handle")):
    stats = await get_user_all_stats(userid)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Stats not found for {userid}")
    summary = Summary(
        totalSolved=stats.solved_problems_count,
        totalContests=stats.contests_count,
        currentRating=stats.rating,
        maxRating=stats.maxRating,
        rank=stats.rank,
    )
    return make_envelope(userid, summary, legacy=stats)
