"""TODO"""
from typing import Optional

from fastapi import HTTPException

from app.controllers.auth_controller import AuthController
from app.utils.auth_utils import normalize_birth_date


class TriageAgent:
    """
    Agente de Triagem do Banco Ágil (versão simples, 2 perguntas):

    Fluxo:
    - Pergunta CPF
    - Pergunta data de nascimento
    - Autentica com AuthController.login
    - Se não encontrar, avisa e recomeça (até 3 tentativas)
    """

    def __init__(self) -> None:
        self.auth_controller = AuthController()

        self.cpf: Optional[str] = None
        self.birth_date: Optional[str] = None
        self.client_data: Optional[dict] = None

        self.authenticated: bool = False
        self.failed_attempts: int = 0
        self.max_attempts: int = 3

        # estágio da conversa:
        # "ask_cpf", "ask_birth_date", "authenticated", "blocked"
        self.stage: str = "ask_cpf"

    def _reset_credentials(self) -> None:
        self.cpf = None
        self.birth_date = None
        self.client_data = None
        self.authenticated = False
        self.stage = "ask_cpf"

    def _extract_cpf_digits(self, text: str) -> str:
        digits = "".join(ch for ch in text if ch.isdigit())
        return digits

    # ----------------- CORE ----------------- #

    def ask(self, user_input: str) -> str:
        """
        Recebe a mensagem do usuário e devolve a próxima resposta do agente.
        Sem IA, só regra fixa. Ideal para garantir o fluxo CPF -> data -> login.
        """

        # já bloqueado
        if self.stage == "blocked":
            return (
                "Não foi possível autenticar seus dados após várias tentativas. "
                "Por segurança, vou encerrar o atendimento. "
                "Por favor, tente novamente mais tarde."
            )

        # 1) Perguntar CPF
        if self.stage == "ask_cpf":
            cpf_digits = self._extract_cpf_digits(user_input)

            if len(cpf_digits) != 11:
                return (
                    "Para continuar, preciso do seu CPF com 11 dígitos. "
                    "Por favor, envie apenas os números do CPF."
                )

            self.cpf = cpf_digits
            self.stage = "ask_birth_date"
            return (
                "Obrigado! Agora, por favor, informe sua data de nascimento em um "
                "dos formatos abaixo:\n"
                "- YYYY-MM-DD  (ex: 2000-11-30)\n"
                "- DD-MM-YYYY  (ex: 30-11-2000)\n"
                "- YYYYMMDD    (ex: 20001130)\n"
                "- DDMMYYYY    (ex: 30112000)"
            )

        # 2) Perguntar data de nascimento
        if self.stage == "ask_birth_date":
            try:
                normalized_date = normalize_birth_date(user_input.strip())
            except TypeError:
                return (
                    "Não consegui entender a data. Use um dos formatos abaixo:\n"
                    "- YYYY-MM-DD  (ex: 2000-11-30)\n"
                    "- DD-MM-YYYY  (ex: 30-11-2000)\n"
                    "- YYYYMMDD    (ex: 20001130)\n"
                    "- DDMMYYYY    (ex: 30112000)"
                )

            self.birth_date = normalized_date

            # tenta autenticar
            try:
                result = self.auth_controller.login(
                    cpf=self.cpf,
                    birth_date=self.birth_date,
                )
                # sucesso
                self.authenticated = True
                self.client_data = result.get("client")
                self.stage = "authenticated"

                nome = ""
                if self.client_data and self.client_data.get("nome"):
                    nome = f"{self.client_data['nome']}, "

                return (
                    f"{nome}autenticação realizada com sucesso! ✅\n\n"
                    "Como posso te ajudar hoje?\n"
                    "- Consultar limite de crédito\n"
                    "- Solicitar aumento de limite\n"
                    "- Entrevista de crédito\n"
                    "- Câmbio"
                )

            except HTTPException as exc:
                # credenciais inválidas
                if exc.status_code == 401:
                    self.failed_attempts += 1

                    if self.failed_attempts >= self.max_attempts:
                        self.stage = "blocked"
                        return (
                            "Não encontrei nenhum cliente com esse CPF e data de nascimento "
                            "após várias tentativas. Por segurança, vou encerrar o atendimento. "
                            "Se os dados estiverem corretos, por favor, procure o suporte do banco."
                        )

                    # ainda pode tentar de novo
                    self._reset_credentials()
                    return (
                        "❌ Não encontrei nenhum cliente com esse CPF e data de nascimento.\n"
                        "Vamos tentar novamente.\n\n"
                        "Por favor, envie novamente o seu CPF (apenas números)."
                    )

                # outros erros (ex: erro ao ler CSV)
                self._reset_credentials()
                return (
                    "Tive um problema ao acessar seus dados agora (erro interno). "
                    "Por favor, tente novamente em alguns minutos."
                )

        # 3) Já autenticado (aqui entra o redirecionamento pra outros agentes depois)
        if self.stage == "authenticated":
            return (
                "Você já está autenticado! 😄\n"
                "Me diga: você quer falar sobre limite de crédito, "
                "aumento de limite, entrevista de crédito ou câmbio?"
            )

        # fallback inesperado
        self._reset_credentials()
        return (
            "Tive um problema para entender seu estado de atendimento. "
            "Vamos começar de novo? Por favor, envie seu CPF (apenas números)."
        )
