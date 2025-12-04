"""TODO"""
from typing import Optional

from app.controllers.auth_controller import AuthController
from app.core.screening_flow import handle_message

class TriageAgent:
    """TODO"""

    def __init__(self, auth_controller: Optional[AuthController] = None) -> None:
        """TODO"""
        self.auth_controller = auth_controller or AuthController()

        self.cpf: Optional[str] = None
        self.birth_date: Optional[str] = None
        self.client_data: Optional[dict] = None

        self.authenticated: bool = False
        self.failed_attempts: int = 0
        self.max_attempts: int = 3
        self.stage: str = "ask_cpf"

    def _reset_credentials(self) -> None:
        """TODO"""
        self.cpf = None
        self.birth_date = None
        self.client_data = None
        self.authenticated = False
        self.stage = "ask_cpf"

    def ask(self, user_input: str) -> str:
        """TODO"""
        return handle_message(self, user_input)
