"""Routes for forex quotation operations."""
from fastapi import APIRouter

from app.controllers.forex_controller import ForexController
from app.infrastructure.schemas.forex_schemas import FxQuoteRequest, FxQuoteResponse

router = APIRouter(prefix="/forex", tags=["forex"])

controller = ForexController()


@router.post("/quote", response_model=FxQuoteResponse)
def get_fx_quote(payload: FxQuoteRequest) -> FxQuoteResponse:
    """Returns the exchange rate, converted amount, and an LLM-generated explanation for the forex quote."""
    result = controller.get_quote(
        base=payload.base,
        target=payload.target,
        amount=payload.amount,
    )
    return FxQuoteResponse(**result)
