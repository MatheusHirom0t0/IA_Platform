"""Controller responsible for handling forex quotation requests."""

from typing import Dict

from fastapi import HTTPException, status

from app.services.forex_service import ForexService
from app.agents.forex_agent import ForexAgent


class ForexController:
    def __init__(self) -> None:
        self.service = ForexService()
        self.agent = ForexAgent()

    def get_quote(self, base: str, target: str, amount: float) -> Dict[str, object]:
        try:
            data = self.service.get_quote(base=base, target=target, amount=amount)
        except RuntimeError as exc:
            msg = str(exc).lower()

            if "404" in msg or "not found" in msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Par de moedas inválido ou não encontrado: {base.upper()}/{target.upper()}.",
                ) from exc

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Não foi possível consultar a cotação no momento. Tente novamente mais tarde.",
            ) from exc

        rate = data["rate"]
        converted_amount = data["converted_amount"]

        reply = self.agent.build_quote_reply(
            base_currency=base,
            target_currency=target,
            amount=amount,
            rate=rate,
            converted_amount=converted_amount,
        )

        return {
            "rate": rate,
            "converted_amount": converted_amount,
            "reply": reply,
        }
