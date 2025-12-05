"""Routes for running the credit interview and generating score explanations."""

from fastapi import APIRouter

from app.controllers.interview_controller import InterviewController
from app.infrastructure.schemas.interview_schemas import (
    CreditInterviewRequest,
    CreditInterviewResponse,
)

router = APIRouter(prefix="/interview", tags=["interview"])

controller = InterviewController()


@router.post("", response_model=CreditInterviewResponse)
def run_credit_interview(payload: CreditInterviewRequest) -> CreditInterviewResponse:
    """Executes the credit interview, computes the score, and returns an LLM-generated explanation."""
    result = controller.run_interview(
        cpf=payload.cpf,
        monthly_income=payload.monthly_income,
        monthly_expenses=payload.monthly_expenses,
        job_type=payload.job_type,
        dependents_count=payload.dependents_count,
        has_debt=payload.has_debt,
    )
    return CreditInterviewResponse(**result)
