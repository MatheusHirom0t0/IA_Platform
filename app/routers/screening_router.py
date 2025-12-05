"""Routes for handling screening chat interactions and agent state management."""

from fastapi import APIRouter

from app.agents.screening_agent import ScreeningAgent
from app.infrastructure.schemas.screening_schemas import (
    ScreeningRequest,
    ScreeningResponse,
)

router = APIRouter(prefix="/screening", tags=["screening"])

agent = ScreeningAgent()


@router.post("/chat", response_model=ScreeningResponse)
def chat(payload: ScreeningRequest) -> ScreeningResponse:
    """Processes a user message through the screening agent and returns the generated reply."""
    reply = agent.ask(payload.message)
    return ScreeningResponse(reply=reply, authenticated=agent.authenticated)


@router.post("/reset")
def reset() -> dict:
    """Resets the internal state of the screening agent, clearing authentication and attempts."""
    agent.reset()
    return {"message": "Screening agent reset successfully."}
