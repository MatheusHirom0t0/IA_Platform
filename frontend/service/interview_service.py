"""TODO"""
from typing import Dict, Any
import requests

from frontend.config import API_BASE_URL

def run_credit_interview(
    cpf: str,
    renda_mensal: float,
    despesas_mensais: float,
    tipo_emprego: str,
    numero_dependentes: int,
    tem_dividas: bool,
) -> Dict[str, Any]:
    """TODO"""
    url = f"{API_BASE_URL}/interview"
    payload = {
        "cpf": cpf,
        "renda_mensal": renda_mensal,
        "despesas_mensais": despesas_mensais,
        "tipo_emprego": tipo_emprego,
        "numero_dependentes": numero_dependentes,
        "tem_dividas": tem_dividas,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de entrevista de crédito: {exc}",
            "score": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de entrevista de crédito ({response.status_code}): {detail}",
            "score": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de entrevista de crédito.",
        ),
        "score": data.get("score"),
    }
