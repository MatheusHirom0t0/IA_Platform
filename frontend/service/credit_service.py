"""TODO"""
from typing import Dict, Any
import requests

from frontend.config import API_BASE_URL


def get_credit_limit(cpf: str) -> Dict[str, Any]:
    """TODO"""
    url = f"{API_BASE_URL}/credit/limit/{cpf}"

    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de crédito: {exc}",
            "limit": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de crédito ({response.status_code}): {detail}",
            "limit": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de crédito ao consultar limite.",
        ),
        "limit": data.get("limit"),
    }


def request_credit_increase(cpf: str, requested_limit: float) -> Dict[str, Any]:
    """TODO"""
    url = f"{API_BASE_URL}/credit/increase"
    payload = {"cpf": cpf, "requested_limit": requested_limit}

    try:
        response = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de crédito: {exc}",
            "data": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de crédito ({response.status_code}): {detail}",
            "data": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de crédito ao solicitar aumento.",
        ),
        "data": data.get("data"),
    }
