"""Utility function for sending credit interview data to the API."""

import os
from typing import Dict, Any
import requests

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL is not set.")


def run_credit_interview(
    cpf: str,
    monthly_income: float,
    monthly_expenses: float,
    job_type: str,
    dependents_count: int,
    has_debt: bool,
) -> Dict[str, Any]:
    """Sends credit interview data to the API and returns the score and response message."""
    url = f"{API_BASE_URL}/interview"
    payload = {
        "cpf": cpf,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "job_type": job_type,
        "dependents_count": dependents_count,
        "has_debt": has_debt,
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
