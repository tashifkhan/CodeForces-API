from fastapi import APIRouter, HTTPException, Path
from typing import Any, Dict, List

from models.contests import Contest
from models.errors import ErrorResponse
from models.canonical import Stats, make_envelope
from models.users import UserInfo
from services import canonical_mapper
from services.contests import get_common_contests, get_upcoming_contests
from services.stats import get_solved_problem_count
from services.users import get_user_info


router = APIRouter(tags=["Legacy"])


@router.get("/{userid}/basic", responses={404: {"model": ErrorResponse}}, deprecated=True)
async def legacy_basic(userid: str = Path(..., description="Codeforces handle")):
    user_info = await get_user_info([userid])
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    data = canonical_mapper.profile_from(user_info[0], userid)
    return make_envelope(userid, data, legacy=UserInfo(**user_info[0]))


@router.get("/multi/{userids}", response_model=List[UserInfo], responses={404: {"model": ErrorResponse}}, deprecated=True)
async def legacy_users_info(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    handles_list = [h.strip() for h in userids.replace(",", ";").split(";") if h.strip()]
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    user_info = await get_user_info(handles_list)
    if not user_info:
        raise HTTPException(status_code=404, detail="User information not found")
    return user_info


@router.get("/{userid}/solved", responses={404: {"model": ErrorResponse}}, deprecated=True)
async def legacy_solved(userid: str = Path(..., description="Codeforces handle")):
    solved_count = await get_solved_problem_count(userid)
    if solved_count is None:
        raise HTTPException(status_code=404, detail=f"Solved problem count not found for {userid}")
    data = Stats(totalSolved=solved_count, byDifficulty={})
    return make_envelope(userid, data, legacy={"handle": userid, "count": solved_count})


@router.get("/users/common-contests/{userids}", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}}, deprecated=True)
async def legacy_common_contests(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    handles_list = [h.strip() for h in userids.replace(",", ";").split(";") if h.strip()]
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    common = await get_common_contests(handles_list)
    return {"handles": handles_list, "common_contests": list(common)}


@router.get("/contests/upcoming", response_model=List[Contest], responses={404: {"model": ErrorResponse}}, deprecated=True)
async def legacy_upcoming_contests(gym: bool = False):
    return await get_upcoming_contests(gym)
