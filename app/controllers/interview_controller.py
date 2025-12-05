"""TODO"""
import os
from fastapi import HTTPException, status

from app.services.interview_service import InterviewService
from app.agents.interview_agent import CreditInterviewAgent


class InterviewController:
    """TODO"""
    def __init__(self) -> None:
        clients_csv = os.getenv("CLIENTS_CSV_PATH", "data/clientes.csv")

        self.service = InterviewService(clients_csv_path=clients_csv)
        self.agent = CreditInterviewAgent()

    def run_interview(
        self,
        cpf: str,
        renda_mensal: float,
        despesas_mensais: float,
        tipo_emprego: str,
        numero_dependentes: int,
        tem_dividas: bool,
    ):
        """TODO"""
        score = self.service.calculate_score(
            renda_mensal,
            despesas_mensais,
            tipo_emprego,
            numero_dependentes,
            tem_dividas,
        )

        try:
            updated = self.service.update_client_score(cpf, score)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Clients CSV not found",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            ) from exc

        interview_result = {
            "cpf": updated["cpf"],
            "nome": updated["nome"],
            "score": updated["score"],
            "renda_mensal": renda_mensal,
            "despesas_mensais": despesas_mensais,
            "tipo_emprego": tipo_emprego,
            "numero_dependentes": numero_dependentes,
            "tem_dividas": tem_dividas,
        }

        reply_text = self.agent.build_reply(interview_result)

        return {"score": score, "reply": reply_text}
