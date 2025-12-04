import os
from typing import Dict

from fastapi import HTTPException, status

from app.services.interview_service import InterviewService
from app.agents.interview_agent import CreditInterviewAgent


class InterviewController:
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
    ) -> Dict[str, object]:
        # 1) Monta os dados de entrada para a IA
        interview_data = {
            "cpf": cpf,
            "renda_mensal": renda_mensal,
            "despesas_mensais": despesas_mensais,
            "tipo_emprego": tipo_emprego,
            "numero_dependentes": numero_dependentes,
            "tem_dividas": "sim" if tem_dividas else "não",
        }

        # 2) IA calcula score + texto
        ai_result = self.agent.calculate_score_and_reply(interview_data)
        score = ai_result["score"]
        reply_text = ai_result["reply"]

        # 3) Atualiza o CSV com o novo score
        try:
            updated = self.service.update_client_score(cpf, score)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Clients CSV not found",
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        # 4) Monta resposta final da API
        final_reply = (
            f"{reply_text}\n\n"
            "Seu score foi atualizado e será considerado nas próximas análises de crédito."
        )

        return {
            "score": updated["score"],
            "reply": final_reply,
        }
