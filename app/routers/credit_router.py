"""TODO"""
from fastapi import APIRouter

from app.controllers.credit_controller import CreditController
from app.infrastructure.schemas.credit_schemas import (
    CreditLimitResponse,
    CreditIncreaseRequest,
    CreditIncreaseResponse,
)

router = APIRouter(prefix="/credit", tags=["credit"])

controller = CreditController()


@router.get("/limit/{cpf}", response_model=CreditLimitResponse)
def get_credit_limit(cpf: str) -> CreditLimitResponse:
    """TODO"""
    result = controller.get_limit(cpf)
    return CreditLimitResponse(**result)


@router.post("/increase", response_model=CreditIncreaseResponse)
def request_credit_increase(payload: CreditIncreaseRequest) -> CreditIncreaseResponse:
    """TODO"""
    result = controller.request_increase(payload.cpf, payload.requested_limit)
    return CreditIncreaseResponse(**result)
