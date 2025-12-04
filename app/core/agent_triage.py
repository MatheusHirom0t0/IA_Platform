"""TODO"""
from typing import Optional

from fastapi import HTTPException

from app.controllers.auth_controller import AuthController
from app.utils.auth_utils import normalize_birth_date
from app.utils.auth_utils import extract_cpf_digits
from app.utils.screening_utils import (
    CPF_PROMPT,
    BIRTHDATE_FORMAT_MSG,
    BIRTHDATE_INVALID_MSG,
    BLOCKED_MSG,
    INTERNAL_ERROR_MSG,
)

class TriageAgent:
    """TODO"""
    def __init__(self, auth_controller: Optional[AuthController] = None) -> None:
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

    def _handle_blocked(self) -> str:
        """TODO"""
        return BLOCKED_MSG

    def _handle_ask_cpf(self, user_input: str) -> str:
        """TODO"""
        cpf_digits = extract_cpf_digits(user_input)

        if len(cpf_digits) != 11:
            return CPF_PROMPT

        client = self.auth_controller.find_client_by_cpf(cpf_digits)
        if client is None:
            self.failed_attempts += 1

            if self.failed_attempts >= self.max_attempts:
                self.stage = "blocked"
                return (
                    "Não encontrei nenhum cliente com esse CPF após várias tentativas. "
                    "Por segurança, vou encerrar o atendimento. "
                    "Se os dados estiverem corretos, por favor, procure o suporte do banco."
                )

            return (
                "❌ Não encontrei nenhum cliente com esse CPF.\n"
                "Vamos tentar novamente.\n\n"
                "Por favor, envie novamente o seu CPF (apenas números)."
            )

        self.cpf = cpf_digits
        self.client_data = client
        self.stage = "ask_birth_date"

        nome_prefix = ""
        if client.get("nome"):
            nome_prefix = f"{client['nome']}, "

        return f"{nome_prefix}obrigado! Agora, {BIRTHDATE_FORMAT_MSG}"

    def _handle_ask_birth_date(self, user_input: str) -> str:
        """TODO"""
        try:
            normalized_date = normalize_birth_date(user_input.strip())
        except TypeError:
            return BIRTHDATE_INVALID_MSG

        self.birth_date = normalized_date
        return self._try_authenticate()

    def _handle_authenticated(self, _: str) -> str:
        """TODO"""
        return (
            "Você já está autenticado! 😄\n"
            "Me diga: você quer falar sobre limite de crédito, "
            "aumento de limite, entrevista de crédito ou câmbio?"
        )
    
    def _try_authenticate(self) -> str:
        """TODO"""
        try:
            result = self.auth_controller.login(
                cpf=self.cpf,
                birth_date=self.birth_date,
            )
            self.authenticated = True
            self.client_data = result.get("client")
            self.stage = "authenticated"

            nome_prefix = ""
            if self.client_data and self.client_data.get("nome"):
                nome_prefix = f"{self.client_data['nome']}, "

            return (
                f"{nome_prefix}autenticação realizada com sucesso! ✅\n\n"
                "Como posso te ajudar hoje?\n"
                "- Consultar limite de crédito\n"
                "- Solicitar aumento de limite\n"
                "- Entrevista de crédito\n"
                "- Câmbio"
            )

        except HTTPException as exc:
            if exc.status_code == 401:
                return self._handle_auth_failed()

            self._reset_credentials()
            return INTERNAL_ERROR_MSG

    def _handle_auth_failed(self) -> str:
        """TODO"""
        self.failed_attempts += 1

        if self.failed_attempts >= self.max_attempts:
            self.stage = "blocked"
            return (
                "Não encontrei nenhum cliente com esse CPF e data de nascimento "
                "após várias tentativas. Por segurança, vou encerrar o atendimento. "
                "Se os dados estiverem corretos, por favor, procure o suporte do banco."
            )

        self._reset_credentials()
        return (
            "❌ Não encontrei nenhum cliente com esse CPF e data de nascimento.\n"
            "Vamos tentar novamente.\n\n"
            "Por favor, envie novamente o seu CPF (apenas números)."
        )

    def ask(self, user_input: str) -> str:
        """TODO"""
        if self.stage == "blocked":
            return self._handle_blocked()

        if self.stage == "ask_cpf":
            return self._handle_ask_cpf(user_input)

        if self.stage == "ask_birth_date":
            return self._handle_ask_birth_date(user_input)

        if self.stage == "authenticated":
            return self._handle_authenticated(user_input)

        self._reset_credentials()
        return (
            "Tive um problema para entender seu estado de atendimento. "
            "Vamos começar de novo? Por favor, envie seu CPF (apenas números)."
        )
