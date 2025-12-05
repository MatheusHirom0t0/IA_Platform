"""Utility function for requesting forex quote data from the API."""

import os
from typing import Dict, Any
import requests

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL is not set.")


def get_fx_quote(base: str, target: str, amount: float) -> Dict[str, Any]:
    """Requests a forex quote from the API and returns the rate and converted amount."""
    url = f"{API_BASE_URL}/forex/quote"
    payload = {"base": base, "target": target, "amount": amount}

    try:
        response = requests.post(url, json=payload, timeout=30)
    except requests.RequestException:
        return {
            "reply": "❌ Erro ao conectar com o serviço de câmbio.",
            "rate": None,
            "converted_amount": None,
        }

    try:
        data = response.json()
    except ValueError:
        return {
            "reply": "❌ Resposta inválida do serviço de câmbio.",
            "rate": None,
            "converted_amount": None,
        }

    if response.status_code != 200:
        detail = data.get("detail") or "Erro desconhecido."
        return {
            "reply": f"❌ {detail}",
            "rate": None,
            "converted_amount": None,
        }

    return {
        "reply": data.get("reply"),
        "rate": data.get("rate"),
        "converted_amount": data.get("converted_amount"),
    }
