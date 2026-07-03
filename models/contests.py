from typing import Any, Dict, List, Optional
from pydantic import BaseModel

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
