"""TODO"""
from fastapi import HTTPException
from app.utils.auth_utils import extract_digits, normalize_date
from app.messages.screening_messages import (
    CPF_PROMPT,
    BIRTHDATE_FORMAT_MSG,
    BIRTHDATE_INVALID_MSG,
    BLOCKED_MSG,
    AUTH_SUCCESS_MSG,
    AUTH_ALREADY_MSG,
)


def _fail(agent) -> bool:
    """TODO"""
    agent.failed_attempts += 1
    if agent.failed_attempts >= agent.max_attempts:
        agent.stage = "blocked"
        return True
    return False


def _handle_ask_cpf(agent, text: str) -> str:
    """TODO"""
    cpf = extract_digits(text)

    if len(cpf) != 11:
        return CPF_PROMPT

    client = agent.auth.find_client_by_cpf(cpf)
    if not client:
        if _fail(agent):
            return BLOCKED_MSG
        return "CPF não encontrado. Tente novamente enviando apenas os números."

    agent.cpf = cpf
    agent.client = client
    agent.stage = "ask_birth_date"

    name = client.get("nome", "")
    prefix = f"{name}, " if name else ""

    return prefix + BIRTHDATE_FORMAT_MSG


def _handle_ask_birth_date(agent, text: str) -> str:
    """TODO"""
    try:
        normalized = normalize_date(text)
    except TypeError:
        return BIRTHDATE_INVALID_MSG

    agent.birth_date = normalized
    return _authenticate(agent)


def _authenticate(agent) -> str:
    """TODO"""
    try:
        result = agent.auth.login(agent.cpf, agent.birth_date)
        agent.authenticated = True
        agent.client = result["client"]
        agent.stage = "authenticated"

        name = agent.client.get("nome", "")
        prefix = f"{name}, " if name else ""

        return prefix + AUTH_SUCCESS_MSG

    except HTTPException:
        if _fail(agent):
            return BLOCKED_MSG
        agent.reset()
        return "Dados incorretos. Vamos tentar novamente. Envie seu CPF."


def handle_message(agent, text: str) -> str:
    """TODO"""
    if agent.stage == "blocked":
        return BLOCKED_MSG

    if agent.stage == "ask_cpf":
        return _handle_ask_cpf(agent, text)

    if agent.stage == "ask_birth_date":
        return _handle_ask_birth_date(agent, text)

    if agent.stage == "authenticated":
        return AUTH_ALREADY_MSG

    agent.reset()
    return "Vamos começar de novo? Envie seu CPF."
