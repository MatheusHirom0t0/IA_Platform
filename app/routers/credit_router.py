from fastapi import APIRouter
from pydantic import BaseModel

from app.controllers.credit_controller import CreditController
from app.infrastructure.schemas.credit_schemas import CreditRequest,CreditResponse

router = APIRouter(prefix="/credit", tags=["credit"])

controller = CreditController()





@router.post("/chat", response_model=CreditResponse)
def credit_chat(payload: CreditRequest) -> CreditResponse:
    """TODO"""
    reply = controller.chat(payload.cpf, payload.message)
    return CreditResponse(reply=reply)
