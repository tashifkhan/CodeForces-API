from fastapi import APIRouter, HTTPException, Path

from models.canonical import make_envelope
from services import canonical_mapper
from services.users import get_user_info


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}/profile")
async def get_profile(userid: str = Path(..., description="Codeforces handle")):
    info = await get_user_info([userid])
    if not info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    return make_envelope(userid, canonical_mapper.profile_from(info[0], userid))
