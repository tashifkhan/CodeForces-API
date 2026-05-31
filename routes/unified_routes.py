"""Canonical unified endpoints shared across all stats services.

Adds the cross-platform endpoints CodeForces did not previously expose under the
unified naming: ``/{userid}/profile``, ``/{userid}/stats``, ``/{userid}/badges``
and the aggregated ``/{userid}/card``. The existing ``/{userid}``, ``/{userid}/basic``,
``/{userid}/solved``, ``/{userid}/rating``, ``/{userid}/heatmap`` and
``/{userid}/contests`` routes already carry the unified envelope additively.
See ../UNIFIED_SCHEMA.md.
"""

from fastapi import APIRouter, HTTPException, Path

from models.unified import UnifiedBadges, make_envelope
from services import unified_mapper
from services.codeforces_service import get_user_info

router = APIRouter()


@router.get("/{userid}/profile")
async def unified_profile(userid: str = Path(..., description="Codeforces handle")):
    info = await get_user_info([userid])
    if not info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    return make_envelope(userid, unified_mapper.profile_from(info[0], userid))


@router.get("/{userid}/stats")
async def unified_stats(userid: str = Path(..., description="Codeforces handle")):
    return make_envelope(userid, await unified_mapper.build_stats(userid))


@router.get("/{userid}/badges")
async def unified_badges(userid: str = Path(..., description="Codeforces handle")):
    return make_envelope(userid, UnifiedBadges())


@router.get("/{userid}/card")
async def unified_card(userid: str = Path(..., description="Codeforces handle")):
    return make_envelope(userid, await unified_mapper.build_card(userid))
