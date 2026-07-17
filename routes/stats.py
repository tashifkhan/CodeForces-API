from fastapi import APIRouter, Path, Query

from models.canonical import make_envelope
from services import canonical_mapper
from services.stats_svg import parse_exclude_list, stats_svg_response


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}/stats/svg", summary="Stats SVG card")
async def get_stats_svg(
    userid: str = Path(..., description="Codeforces handle"),
    theme: str = Query("dark", description="Card theme: dark or light"),
    exclude: str | None = Query(
        None,
        description="Comma-separated topics/tags to exclude from the topic bars",
    ),
):
    data = await canonical_mapper.build_stats(userid)
    return stats_svg_response(
        "codeforces",
        userid,
        data,
        theme=theme,
        exclude=parse_exclude_list(exclude),
    )


@router.get("/{userid}/stats")
async def get_stats(userid: str = Path(..., description="Codeforces handle")):
    return make_envelope(userid, await canonical_mapper.build_stats(userid))
