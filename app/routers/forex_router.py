"""TODO"""
from fastapi import APIRouter

from app.controllers.forex_controller import ForexController
from app.infrastructure.schemas.forex_schemas import FxQuoteRequest, FxQuoteResponse

router = APIRouter(prefix="/forex", tags=["forex"])

controller = ForexController()


@router.post("/quote", response_model=FxQuoteResponse)
def get_fx_quote(payload: FxQuoteRequest) -> FxQuoteResponse:
    """TODO"""
    result = controller.get_quote(
        base=payload.base,
        target=payload.target,
        amount=payload.amount,
    )
    return FxQuoteResponse(**result)
