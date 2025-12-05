"""Pydantic schemas for forex quotation operations."""
from pydantic import BaseModel


class FxQuoteRequest(BaseModel):
    """Request model for obtaining a forex quote."""
    base: str
    target: str
    amount: float


class FxQuoteResponse(BaseModel):
    """Response model containing the exchange rate, converted amount, and LLM explanation."""
    rate: float
    converted_amount: float
    reply: str
