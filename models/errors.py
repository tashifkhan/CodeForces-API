from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
