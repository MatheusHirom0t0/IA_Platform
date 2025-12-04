from fastapi import HTTPException
from app.agents.credit_agent import CreditAgent
from app.controllers.auth_controller import AuthController


class CreditController:
    def __init__(self):
        self.auth = AuthController()
        self.agent = CreditAgent()

    def chat(self, cpf: str, message: str) -> str:
        client = self.auth.find_client_by_cpf(cpf)

        if not client:
            raise HTTPException(status_code=404, detail="Cliente não encontrado.")

        # Se for a primeira interação do cliente, inicia fluxo
        if self.agent.stage == "idle":
            reply = self.agent.start(client)
            return reply

        # Se o fluxo já começou, continua
        reply = self.agent.handle_message(client, message)
        return reply
