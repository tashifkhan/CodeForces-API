from fastapi import APIRouter, HTTPException
from typing import List
from models.base import Contest, ErrorResponse
from services.codeforces_service import get_upcoming_contests

router = APIRouter()

@router.get("/contests/upcoming", response_model=List[Contest], responses={404: {"model": ErrorResponse}})
async def upcoming_contests(gym: bool = False):
    """Get upcoming contests from Codeforces."""
    contests = await get_upcoming_contests(gym)
    if contests is None:
        raise HTTPException(status_code=404, detail="Upcoming contests data not found")
    return contests
