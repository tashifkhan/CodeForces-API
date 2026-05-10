from pydantic import BaseModel

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
