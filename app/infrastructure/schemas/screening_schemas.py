"""TODO"""
from pydantic import BaseModel

class ScreeningRequest(BaseModel):
    """TODO"""
    message: str

class ScreeningResponse(BaseModel):
    """TODO"""
    reply: str
