from fastapi import APIRouter, Path, Query

from models.canonical import make_envelope
from services import canonical_mapper


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}/heatmap")
async def get_heatmap(
    userid: str = Path(..., description="Codeforces handle"),
    view: str = Query("all", description="all | last_365 | year"),
    year: int | None = Query(None, description="Required when view=year"),
):
    return make_envelope(userid, await canonical_mapper.build_heatmap(userid, view, year))
