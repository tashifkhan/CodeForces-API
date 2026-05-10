from pydantic import BaseModel

class SolvedProblemsCount(BaseModel):
    """Model for solved problems count."""
    handle: str
    count: int
