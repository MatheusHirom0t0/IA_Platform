"""Controller responsible for handling credit interview logic and generating explanations via LLM."""

import os
from fastapi import HTTPException, status

from app.services.interview_service import InterviewService
from app.agents.interview_agent import CreditInterviewAgent


class InterviewController:
    """Coordinates score calculation, client score updates, and generation of interview explanations."""

    def __init__(self) -> None:
        clients_csv = os.getenv("CLIENTS_CSV_PATH", "data/clientes.csv")

        self.service = InterviewService(clients_csv_path=clients_csv)
        self.agent = CreditInterviewAgent()

    def run_interview(
        self,
        cpf: str,
        monthly_income: float,
        monthly_expenses: float,
        job_type: str,
        dependents_count: int,
        has_debt: bool,
    ):
        """Calculates the credit score, updates the client record, and generates an LLM explanation."""
        score = self.service.calculate_score(
            monthly_income,
            monthly_expenses,
            job_type,
            dependents_count,
            has_debt,
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
            "renda_mensal": monthly_income,
            "despesas_mensais": monthly_expenses,
            "tipo_emprego": job_type,
            "numero_dependentes": dependents_count,
            "tem_dividas": has_debt,
        }

        reply_text = self.agent.build_reply(interview_result)

        return {"score": score, "reply": reply_text}
