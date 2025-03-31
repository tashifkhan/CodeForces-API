from fastapi import APIRouter, HTTPException, Path
from typing import List, Dict, Any
from models.base import UserAllStats, UserInfo, RatingHistory, SolvedProblemsCount, ErrorResponse
from services.codeforces_service import (
    get_user_all_stats, get_user_info, get_user_rating,
    get_solved_problem_count, get_contests_participated_by_user,
    get_common_contests
)

router = APIRouter()


@router.get("/{userid}", response_model=UserAllStats, responses={404: {"model": ErrorResponse}})
async def user_all_stats(userid: str = Path(..., description="Codeforces handle")):
    """Get comprehensive statistics for a Codeforces user."""
    stats = await get_user_all_stats(userid)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Stats not found for {userid}")
    return stats


@router.get("/{userid}/basic", response_model=UserInfo, responses={404: {"model": ErrorResponse}})
async def user_basic_info(userid: str = Path(..., description="Codeforces handle")):
    """Get basic information about a Codeforces user."""
    user_info = await get_user_info([userid])
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    return user_info[0]


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



@router.get("/{userid}/rating", response_model=List[RatingHistory], responses={404: {"model": ErrorResponse}})
async def user_rating(userid: str = Path(..., description="Codeforces handle")):
    """Get rating history of a Codeforces user."""
    rating_history = await get_user_rating(userid)
    if rating_history is None:
        raise HTTPException(status_code=404, detail=f"Rating history not found for {userid}")
    return rating_history



@router.get("/{userid}/solved", response_model=SolvedProblemsCount, responses={404: {"model": ErrorResponse}})
async def solved_problems(userid: str = Path(..., description="Codeforces handle")):
    """Get the number of solved problems for a Codeforces user."""
    solved_count = await get_solved_problem_count(userid)
    if solved_count is None:
        raise HTTPException(status_code=404, detail=f"Solved problem count not found for {userid}")
    return {"handle": userid, "count": solved_count}



@router.get("/{userid}/contests", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def contests_participated(userid: str = Path(..., description="Codeforces handle")):
    """Get contests participated by a Codeforces user."""
    contests = await get_contests_participated_by_user(userid)
    if not contests:
        raise HTTPException(status_code=404, detail=f"Contest participation data not found for {userid}")
    return {"handle": userid, "contests": list(contests)}


@router.get("/users/common-contests/{userids}", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def common_contests(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get common contests participated by multiple Codeforces users."""
    handles_list = [h.strip() for h in userids.replace(',', ';').split(';') if h.strip()]
    
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    common = await get_common_contests(handles_list)
    return {"handles": handles_list, "common_contests": list(common)}
