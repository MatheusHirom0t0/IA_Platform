from fastapi import APIRouter

from app.agents.screening_agent import ScreeningAgent
from app.infrastructure.schemas.screening_schemas import ScreeningRequest, ScreeningResponse

router = APIRouter(prefix="/screening", tags=["screening"])

agent = ScreeningAgent()


@router.post("/chat", response_model=ScreeningResponse)
def chat(payload: ScreeningRequest) -> ScreeningResponse:
    reply = agent.ask(payload.message)
    return ScreeningResponse(reply=reply, authenticated=agent.authenticated)


@router.post("/reset")
def reset() -> dict:
    agent.reset()
    return {"message": "Screening agent reset successfully."}
