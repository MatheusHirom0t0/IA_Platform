"""TODO"""
from typing import Optional
from app.controllers.auth_controller import AuthController
from app.agents.screening_flow import handle_message


class ScreeningAgent:
    """TODO"""
    def __init__(self, auth_controller: Optional[AuthController] = None) -> None:
        self.auth = auth_controller or AuthController()

        self.cpf: Optional[str] = None
        self.birth_date: Optional[str] = None
        self.client: Optional[dict] = None

        self.failed_attempts: int = 0
        self.max_attempts: int = 3

        self.stage: str = "ask_cpf"
        self.authenticated: bool = False

    def reset(self) -> None:
        """TODO"""
        self.cpf = None
        self.birth_date = None
        self.client = None
        self.failed_attempts = 0
        self.authenticated = False
        self.stage = "ask_cpf"

    def ask(self, message: str) -> str:
        """TODO"""
        return handle_message(self, message)
