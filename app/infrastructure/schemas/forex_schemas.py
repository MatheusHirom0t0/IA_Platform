from pydantic import BaseModel


class FxQuoteRequest(BaseModel):
    base: str
    target: str
    amount: float


class FxQuoteResponse(BaseModel):
    rate: float
    converted_amount: float
    reply: str
