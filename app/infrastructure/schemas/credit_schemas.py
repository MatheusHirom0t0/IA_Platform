"""TODO"""
from typing import Dict
from pydantic import BaseModel, Field


class CreditLimitResponse(BaseModel):
    """TODO"""
    limit: float
    reply: str


class CreditIncreaseRequest(BaseModel):
    """TODO"""
    cpf: str
    requested_limit: float = Field(gt=0)


class CreditIncreaseResponse(BaseModel):
    """TODO"""
    data: Dict[str, str]
    reply: str
