from pydantic import BaseModel, Field

from .rating import RatingHistory


class UserInfo(BaseModel):
    """Model for user information from Codeforces."""

    handle: str
    rating: int | None = None
    maxRating: int | None = None
    rank: str | None = None
    maxRank: str | None = None
    country: str | None = None
    city: str | None = None
    organization: str | None = None
    contribution: int | None = None
    registrationTimeSeconds: int | None = None
    friendOfCount: int | None = None
    titlePhoto: str | None = None
    avatar: str | None = None


class UserAllStats(UserInfo):
    """Model for comprehensive user statistics."""

    contests_count: int = Field(0, description="Number of contests participated in")
    solved_problems_count: int = Field(0, description="Number of problems solved")
    rating_history: list[list[RatingHistory]] | None = Field(
        None, description="History of rating changes"
    )
