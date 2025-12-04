# app/routers/triage_router.py
from fastapi import APIRouter

from app.core.agent_triage import TriageAgent
from app.infrastructure.schemas.triage_schemas import TriageRequest, TriageResponse

router = APIRouter(prefix="/triage", tags=["triage"])

# Agente único em memória (igual no CLI)
triage_agent = TriageAgent()


@router.post("/chat", response_model=TriageResponse)
def triage_chat(payload: TriageRequest) -> TriageResponse:
    """
    Endpoint de chat com o Agente de Triagem.

    Exemplo de request:
    {
        "message": "Oi, quero falar sobre meu cartão"
    }
    """
    reply = triage_agent.ask(payload.message)
    return TriageResponse(reply=reply)
