"""Pydantic schemas for credit interview requests and responses."""
from pydantic import BaseModel


class CreditInterviewRequest(BaseModel):
    """Request model containing all inputs used to compute the credit score."""
    cpf: str
    monthly_income: float
    monthly_expenses: float
    job_type: str
    dependents_count: int
    has_debt: bool


class CreditInterviewResponse(BaseModel):
    """Response model containing the computed score and the LLM explanation."""
    score: float
    reply: str
