"""TODO"""

CPF_PROMPT = (
    "Para continuar, preciso do seu CPF com 11 dígitos. "
    "Por favor, envie apenas os números do CPF."
)

BIRTHDATE_FORMAT_MSG = (
    "Por favor, informe sua data de nascimento em um dos formatos abaixo:\n"
    "- YYYY-MM-DD  (ex: 2000-11-30)\n"
    "- DD-MM-YYYY  (ex: 30-11-2000)\n"
    "- YYYYMMDD    (ex: 20001130)\n"
    "- DDMMYYYY    (ex: 30112000)"
)

BIRTHDATE_INVALID_MSG = (
    "Não consegui entender a data. Use um dos formatos abaixo:\n"
    "- YYYY-MM-DD  (ex: 2000-11-30)\n"
    "- DD-MM-YYYY  (ex: 30-11-2000)\n"
    "- YYYYMMDD    (ex: 20001130)\n"
    "- DDMMYYYY    (ex: 30112000)"
)

BLOCKED_MSG = (
    "Não foi possível autenticar seus dados após várias tentativas. "
    "Por segurança, vou encerrar o atendimento. "
    "Por favor, tente novamente mais tarde."
)

INTERNAL_ERROR_MSG = (
    "Tive um problema ao acessar seus dados agora (erro interno). "
    "Por favor, tente novamente em alguns minutos."
)
