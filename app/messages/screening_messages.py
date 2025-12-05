"""Constant messages used by the screening flow."""
CPF_PROMPT = (
    "Para continuar, envie seu CPF com 11 dígitos (somente números)."
)

BIRTHDATE_FORMAT_MSG = (
    "por favor, envie sua data de nascimento em um dos formatos:\n"
    "- YYYY-MM-DD (2000-11-30)\n"
    "- DD-MM-YYYY (30-11-2000)\n"
    "- YYYYMMDD (20001130)\n"
    "- DDMMYYYY (30112000)"
)

BIRTHDATE_INVALID_MSG = (
    "Não consegui entender a data. Use um dos formatos válidos."
)

BLOCKED_MSG = (
    "Foram várias tentativas sem sucesso. Por segurança, o atendimento foi encerrado."
)

AUTH_SUCCESS_MSG = (
    "autenticação realizada com sucesso! Como posso ajudar hoje?"
)

AUTH_ALREADY_MSG = (
    "Você já está autenticado! Como posso ajudar?"
)
