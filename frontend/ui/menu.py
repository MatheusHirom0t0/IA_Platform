"""TODO"""
from typing import Dict, List

ACTIONS: Dict[str, str] = {
    "1": "Consultar limite de crédito",
    "2": "Solicitar aumento de limite",
    "3": "Iniciar entrevista de crédito",
    "4": "Consultar cotação de moeda",
    "5": "Encerrar conversa",
}


def build_menu_text() -> str:
    """TODO"""
    lines: List[str] = ["**Selecione uma das opções:**", ""]
    for num, label in ACTIONS.items():
        lines.append(f"- **{num}** {label}")
    return "\n".join(lines)
