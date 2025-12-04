"""TODO"""
import os
from typing import Dict

from fastapi import HTTPException, status

from app.services.credit_service import CreditService
from app.agents.credit_agent import CreditAgent


class CreditController:
    """TODO"""
    def __init__(self) -> None:
        clients_csv = os.getenv("CLIENTS_CSV_PATH", "data/clientes.csv")
        score_limits_csv = os.getenv("SCORE_LIMITS_CSV_PATH", "data/score_limite.csv")
        requests_csv = os.getenv(
            "CREDIT_REQUESTS_CSV_PATH",
            "data/solicitacoes_aumento_limite.csv",
        )

        self.service = CreditService(
            clients_csv_path=clients_csv,
            score_limits_csv_path=score_limits_csv,
            requests_csv_path=requests_csv,
        )

        self.agent = CreditAgent()

    def get_limit(self, cpf: str) -> Dict[str, object]:
        """TODO"""
        try:
            limit_value = self.service.get_current_limit(cpf)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        reply = self.agent.build_limit_reply(cpf, limit_value)
        return {"limit": limit_value, "reply": reply}

    def request_increase(self, cpf: str, requested_limit: float) -> Dict[str, object]:
        """TODO"""
        try:
            result = self.service.evaluate_increase_request(cpf, requested_limit)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        reply = self.agent.build_increase_reply(result)
        return {"data": result, "reply": reply}
