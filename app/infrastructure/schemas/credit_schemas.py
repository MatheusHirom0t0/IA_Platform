"""Pydantic schemas for credit limit and limit increase operations."""
from typing import Dict
from pydantic import BaseModel, Field


class CreditLimitResponse(BaseModel):
    """Response model for retrieving a client's current credit limit."""
    limit: float
    reply: str


class CreditIncreaseRequest(BaseModel):
    """Request model for submitting a credit limit increase attempt."""
    cpf: str
    requested_limit: float = Field(gt=0)


class CreditIncreaseResponse(BaseModel):
    """Response model containing the evaluation result and LLM-generated explanation."""
    data: Dict[str, str]
    reply: str
