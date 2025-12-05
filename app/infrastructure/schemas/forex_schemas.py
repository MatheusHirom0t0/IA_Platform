"""TODO"""
from pydantic import BaseModel


class FxQuoteRequest(BaseModel):
    """TODO"""
    base: str
    target: str
    amount: float


class FxQuoteResponse(BaseModel):
    """TODO"""
    rate: float
    converted_amount: float
    reply: str
