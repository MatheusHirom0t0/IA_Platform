from typing import Dict
from pydantic import BaseModel, Field


class CreditLimitResponse(BaseModel):
    limit: float
    reply: str


class CreditIncreaseRequest(BaseModel):
    cpf: str
    requested_limit: float = Field(gt=0)


class CreditIncreaseResponse(BaseModel):
    data: Dict[str, str]
    reply: str
