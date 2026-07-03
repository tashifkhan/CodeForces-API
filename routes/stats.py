from fastapi import APIRouter, Path

from models.canonical import make_envelope
from services import canonical_mapper


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}/stats")
async def get_stats(userid: str = Path(..., description="Codeforces handle")):
    return make_envelope(userid, await canonical_mapper.build_stats(userid))
