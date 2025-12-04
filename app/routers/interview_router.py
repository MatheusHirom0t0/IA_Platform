# app/routers/interview_router.py
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
    result = controller.run_interview(
        cpf=payload.cpf,
        renda_mensal=payload.renda_mensal,
        despesas_mensais=payload.despesas_mensais,
        tipo_emprego=payload.tipo_emprego,
        numero_dependentes=payload.numero_dependentes,
        tem_dividas=payload.tem_dividas,
    )
    return CreditInterviewResponse(**result)
