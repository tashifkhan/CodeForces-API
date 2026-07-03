from fastapi import APIRouter, Path

from models.canonical import Badges, make_envelope


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}/badges")
async def get_badges(userid: str = Path(..., description="Codeforces handle")):
    return make_envelope(userid, Badges())
