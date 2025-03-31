from pydantic import BaseModel, Field
from typing import Optional, List

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str

class UserInfo(BaseModel):
    """Model for user information from Codeforces."""
    handle: str
    rating: Optional[int] = None
    maxRating: Optional[int] = None
    rank: Optional[str] = None
    maxRank: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[str] = None
    contribution: Optional[int] = None
    registrationTimeSeconds: Optional[int] = None
    friendOfCount: Optional[int] = None
    titlePhoto: Optional[str] = None
    avatar: Optional[str] = None

class RatingChangeContest(BaseModel):
    """Model for contest in a rating change."""
    id: int
    name: str

class RatingHistory(BaseModel):
    """Model for rating change history."""
    contestId: int
    contestName: str
    handle: str
    rank: int
    ratingUpdateTimeSeconds: int
    oldRating: int
    newRating: int

class SolvedProblemsCount(BaseModel):
    """Model for solved problems count."""
    handle: str
    count: int

class Contest(BaseModel):
    """Model for a contest."""
    id: int
    name: str
    type: str
    phase: str
    frozen: bool
    durationSeconds: int
    startTimeSeconds: int
    relativeTimeSeconds: Optional[int] = None
    preparedBy: Optional[str] = None
    websiteUrl: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    kind: Optional[str] = None
    icpcRegion: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    season: Optional[str] = None

class UserAllStats(UserInfo):
    """Model for comprehensive user statistics."""
    contests_count: int = Field(0, description="Number of contests participated in")
    solved_problems_count: int = Field(0, description="Number of problems solved")
    rating_history: Optional[List[RatingHistory]] = Field(None, description="History of rating changes")
