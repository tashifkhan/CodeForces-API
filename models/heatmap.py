from pydantic import BaseModel, Field

class HeatmapDay(BaseModel):
    """Model for one day of user activity."""
    date: str
    submissions: int
    accepted: int

class UserActivityHeatmap(BaseModel):
    """Model for daily activity heatmap data."""
    handle: str
    mode: str = Field(..., description="Heatmap range mode: trailing_days or calendar_year")
    timezone: str = Field("UTC", description="Timezone used for daily buckets")
    days: int = Field(..., description="Number of days included in the heatmap")
    year: int | None = None
    start_date: str
    end_date: str
    available_years: list[int]
    total_submissions: int
    total_accepted: int
    active_days: int
    current_streak: int
    longest_streak: int
    heatmap: list[HeatmapDay]
