"""TODO"""
from typing import Dict

from fastapi import HTTPException, status

from app.services.forex_service import ForexService
from app.agents.forex_agent import ForexAgent


class ForexController:
    """TODO"""
    def __init__(self) -> None:
        self.service = ForexService()
        self.agent = ForexAgent()

    def get_quote(self, base: str, target: str, amount: float) -> Dict[str, object]:
        """TODO"""
        try:
            data = self.service.get_quote(base=base, target=target, amount=amount)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            )

        rate = data["rate"]
        converted_amount = data["converted_amount"]

        reply = self.agent.build_quote_reply(
            base=base,
            target=target,
            amount=amount,
            rate=rate,
            converted_amount=converted_amount,
        )

        return {
            "rate": rate,
            "converted_amount": converted_amount,
            "reply": reply,
        }
