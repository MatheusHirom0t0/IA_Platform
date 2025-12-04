"""Agente de triagem do Banco Ágil usando LLM para as respostas."""

from typing import Optional, Dict, Any

from app.controllers.auth_controller import AuthController
from app.utils.auth_utils import extract_cpf_digits, normalize_birth_date
from app.utils.llm_client import generate_text


class ScreeningAgent:
    """TODO"""
    def __init__(self, auth_controller: Optional[AuthController] = None) -> None:
        self.auth = auth_controller or AuthController()
        self.max_attempts: int = 3
        self.reset()

    def reset(self) -> None:
        """TODO"""
        self.cpf: Optional[str] = None
        self.birth_date: Optional[str] = None
        self.client: Optional[Dict[str, str]] = None

        self.failed_attempts: int = 0
        self.stage: str = "ask_cpf"
        self.authenticated: bool = False


    @property
    def _system_prompt(self) -> str:
        return (
            "Você é o Agente de Triagem do Banco Ágil.\n"
            "Sempre responda em português do Brasil, de forma educada, simples e direta.\n\n"
            "IMPORTANTE:\n"
            "- Você NÃO valida CPF nem datas. O servidor já fez todas as validações.\n"
            "- Você só sabe o que aconteceu através do campo 'evento' enviado pelo sistema.\n"
            "- NÃO invente regras de formato de data ou CPF. Só fale que está incorreto "
            "quando o evento enviado indicar isso.\n"
            "- Quando o evento for 'ask_cpf', peça educadamente o CPF.\n"
            "- Quando o evento for 'cpf_invalid_format' ou 'cpf_not_found', explique o problema "
            "e peça o CPF novamente.\n"
            "- Quando o evento for 'ask_birthdate', peça a data de nascimento, mas sem impor um "
            "formato específico. Apenas diga para ele informar a data de nascimento.\n"
            "- Quando o evento for 'birthdate_invalid_format', explique que o formato da data digitada "
            "não é aceito e peça para tentar novamente.\n"
            "- Quando o evento for 'birthdate_mismatch', explique que a data não confere com o cadastro.\n"
            "- Quando o evento for 'authenticated', dê as boas-vindas usando o nome do cliente (se enviado) "
            "e inclua literalmente a frase 'autenticação realizada com sucesso'.\n"
            "- Quando o evento for 'already_authenticated', diga que ele já está autenticado e que pode "
            "escolher uma das opções do menu.\n"
            "- Quando o evento for 'blocked', informe que ele excedeu o número de tentativas e que não será "
            "possível continuar o atendimento agora.\n"
        )

    def _build_llm_message(self, context: Dict[str, Any]) -> str:
        """TODO"""
        state = context["state"]
        user_input = context["user_input"]
        event = context["event"]
        failed_attempts = context["failed_attempts"]
        max_attempts = context["max_attempts"]
        authenticated = context["authenticated"]
        client = context.get("client")

        client_name = client["nome"] if client and "nome" in client else None

        base = [
            f"Estado atual da triagem: {state}",
            f"Entrada digitada pelo usuário: {user_input!r}",
            f"Evento gerado pelo sistema: {event}",
            f"Tentativas falhas: {failed_attempts} de {max_attempts}",
            f"Usuário autenticado? {authenticated}",
        ]

        if client_name:
            base.append(f"Nome do cliente encontrado no cadastro: {client_name}")

        description = "\n".join(base)

        instructions = (
            "Com base nessas informações, gere UMA resposta curta e clara para o cliente.\n"
            "- Use no máximo 3 frases.\n"
            "- Não use listas, títulos ou assinatura.\n"
            "- Fale como um atendente humano de banco.\n"
        )

        return description + "\n\n" + instructions

    def _reply_with_llm(self, context: Dict[str, Any]) -> str:
        user_message = self._build_llm_message(context)
        return generate_text(self._system_prompt, user_message)

    def _increment_failed(self) -> bool:
        self.failed_attempts += 1
        if self.failed_attempts >= self.max_attempts:
            self.stage = "blocked"
            return True
        return False

    def ask(self, user_input: str) -> str:
        """TODO"""
        raw_input = user_input.strip()

        if self.stage == "blocked":
            context = {
                "state": self.stage,
                "user_input": raw_input,
                "event": "blocked",
                "failed_attempts": self.failed_attempts,
                "max_attempts": self.max_attempts,
                "authenticated": self.authenticated,
                "client": self.client,
            }
            return self._reply_with_llm(context)

        if self.authenticated and self.stage == "authenticated":
            context = {
                "state": self.stage,
                "user_input": raw_input,
                "event": "already_authenticated",
                "failed_attempts": self.failed_attempts,
                "max_attempts": self.max_attempts,
                "authenticated": self.authenticated,
                "client": self.client,
            }
            return self._reply_with_llm(context)

        if self.stage == "ask_cpf":

            if raw_input == "":
                context = {
                    "state": self.stage,
                    "user_input": raw_input,
                    "event": "ask_cpf",
                    "failed_attempts": self.failed_attempts,
                    "max_attempts": self.max_attempts,
                    "authenticated": self.authenticated,
                    "client": None,
                }
                return self._reply_with_llm(context)

            cpf_digits = extract_cpf_digits(raw_input)

            if len(cpf_digits) != 11:
                blocked = self._increment_failed()
                event = "cpf_invalid_format" if not blocked else "blocked"

                context = {
                    "state": self.stage,
                    "user_input": raw_input,
                    "event": event,
                    "failed_attempts": self.failed_attempts,
                    "max_attempts": self.max_attempts,
                    "authenticated": self.authenticated,
                    "client": None,
                }
                return self._reply_with_llm(context)

            client = self.auth.find_client_by_cpf(cpf_digits)
            if client is None:
                blocked = self._increment_failed()
                event = "cpf_not_found" if not blocked else "blocked"

                context = {
                    "state": self.stage,
                    "user_input": raw_input,
                    "event": event,
                    "failed_attempts": self.failed_attempts,
                    "max_attempts": self.max_attempts,
                    "authenticated": self.authenticated,
                    "client": None,
                }
                return self._reply_with_llm(context)

            self.cpf = cpf_digits
            self.client = client
            self.stage = "ask_birthdate"

            context = {
                "state": self.stage,
                "user_input": raw_input,
                "event": "ask_birthdate",
                "failed_attempts": self.failed_attempts,
                "max_attempts": self.max_attempts,
                "authenticated": self.authenticated,
                "client": self.client,
            }
            return self._reply_with_llm(context)

        if self.stage == "ask_birthdate":

            if raw_input == "":
                context = {
                    "state": self.stage,
                    "user_input": raw_input,
                    "event": "ask_birthdate",
                    "failed_attempts": self.failed_attempts,
                    "max_attempts": self.max_attempts,
                    "authenticated": self.authenticated,
                    "client": self.client,
                }
                return self._reply_with_llm(context)

            try:
                normalized = normalize_birth_date(raw_input)
            except TypeError:
                blocked = self._increment_failed()
                event = "birthdate_invalid_format" if not blocked else "blocked"

                context = {
                    "state": self.stage,
                    "user_input": raw_input,
                    "event": event,
                    "failed_attempts": self.failed_attempts,
                    "max_attempts": self.max_attempts,
                    "authenticated": self.authenticated,
                    "client": self.client,
                }
                return self._reply_with_llm(context)

            expected = (self.client or {}).get("data_nascimento")
            if expected and normalized != expected:
                blocked = self._increment_failed()
                event = "birthdate_mismatch" if not blocked else "blocked"

                context = {
                    "state": self.stage,
                    "user_input": raw_input,
                    "event": event,
                    "failed_attempts": self.failed_attempts,
                    "max_attempts": self.max_attempts,
                    "authenticated": self.authenticated,
                    "client": self.client,
                }
                return self._reply_with_llm(context)

            self.birth_date = normalized
            self.authenticated = True
            self.stage = "authenticated"

            context = {
                "state": self.stage,
                "user_input": raw_input,
                "event": "authenticated",
                "failed_attempts": self.failed_attempts,
                "max_attempts": self.max_attempts,
                "authenticated": self.authenticated,
                "client": self.client,
            }
            return self._reply_with_llm(context)

        context = {
            "state": self.stage,
            "user_input": raw_input,
            "event": "unexpected_state",
            "failed_attempts": self.failed_attempts,
            "max_attempts": self.max_attempts,
            "authenticated": self.authenticated,
            "client": self.client,
        }
        return self._reply_with_llm(context)
