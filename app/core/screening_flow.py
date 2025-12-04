from fastapi import HTTPException

from app.utils.auth_utils import normalize_birth_date
from app.utils.auth_utils import extract_cpf_digits
from app.utils.screening_utils import (
    CPF_PROMPT,
    BIRTHDATE_FORMAT_MSG,
    BIRTHDATE_INVALID_MSG,
    BLOCKED_MSG,
    INTERNAL_ERROR_MSG,
)


def _handle_blocked(agent, _: str) -> str:
    return BLOCKED_MSG


def _handle_ask_cpf(agent, user_input: str) -> str:
    cpf_digits = extract_cpf_digits(user_input)

    # valida formato (11 dígitos)
    if len(cpf_digits) != 11:
        return CPF_PROMPT

    # verifica se CPF existe na base
    client = agent.auth_controller.find_client_by_cpf(cpf_digits)
    if client is None:
        agent.failed_attempts += 1

        if agent.failed_attempts >= agent.max_attempts:
            agent.stage = "blocked"
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

    # CPF existe → guarda e vai pra data
    agent.cpf = cpf_digits
    agent.client_data = client
    agent.stage = "ask_birth_date"

    nome_prefix = ""
    if client.get("nome"):
        nome_prefix = f"{client['nome']}, "

    return f"{nome_prefix}obrigado! Agora, {BIRTHDATE_FORMAT_MSG}"


def _handle_ask_birth_date(agent, user_input: str) -> str:
    try:
        normalized_date = normalize_birth_date(user_input.strip())
    except TypeError:
        return BIRTHDATE_INVALID_MSG

    agent.birth_date = normalized_date
    return _try_authenticate(agent)


def _handle_authenticated(agent, _: str) -> str:
    return (
        "Você já está autenticado! 😄\n"
        "Me diga: você quer falar sobre limite de crédito, "
        "aumento de limite, entrevista de crédito ou câmbio?"
    )


def _try_authenticate(agent) -> str:
    try:
        result = agent.auth_controller.login(
            cpf=agent.cpf,
            birth_date=agent.birth_date,
        )
        agent.authenticated = True
        agent.client_data = result.get("client")
        agent.stage = "authenticated"

        nome_prefix = ""
        if agent.client_data and agent.client_data.get("nome"):
            nome_prefix = f"{agent.client_data['nome']}, "

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
            return _handle_auth_failed(agent)

        agent._reset_credentials()
        return INTERNAL_ERROR_MSG


def _handle_auth_failed(agent) -> str:
    agent.failed_attempts += 1

    if agent.failed_attempts >= agent.max_attempts:
        agent.stage = "blocked"
        return (
            "Não encontrei nenhum cliente com esse CPF e data de nascimento "
            "após várias tentativas. Por segurança, vou encerrar o atendimento. "
            "Se os dados estiverem corretos, por favor, procure o suporte do banco."
        )

    agent._reset_credentials()
    return (
        "❌ Não encontrei nenhum cliente com esse CPF e data de nascimento.\n"
        "Vamos tentar novamente.\n\n"
        "Por favor, envie novamente o seu CPF (apenas números)."
    )


def handle_message(agent, user_input: str) -> str:
    """
    Função única que decide qual handler chamar com base no estágio.
    Deixa a classe TriageAgent bem mais simples.
    """
    if agent.stage == "blocked":
        return _handle_blocked(agent, user_input)

    if agent.stage == "ask_cpf":
        return _handle_ask_cpf(agent, user_input)

    if agent.stage == "ask_birth_date":
        return _handle_ask_birth_date(agent, user_input)

    if agent.stage == "authenticated":
        return _handle_authenticated(agent, user_input)

    # fallback
    agent._reset_credentials()
    return (
        "Tive um problema para entender seu estado de atendimento. "
        "Vamos começar de novo? Por favor, envie seu CPF (apenas números)."
    )
