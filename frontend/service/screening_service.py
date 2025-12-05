"""TODO"""
from typing import Dict, Any
import requests

from frontend.config import API_BASE_URL

def send_message_to_screening(message: str) -> Dict[str, Any]:
    """TODO"""
    url = f"{API_BASE_URL}/screening/chat"

    try:
        response = requests.post(url, json={"message": message}, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de screening: {exc}",
            "authenticated": False,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de screening ({response.status_code}): {detail}",
            "authenticated": False,
        }

    data = response.json()
    return {
        "reply": data.get("reply", "❌ Resposta inesperada da API de screening."),
        "authenticated": data.get("authenticated", False),
    }


def reset_screening_backend() -> None:
    """TODO"""
    try:
        requests.post(f"{API_BASE_URL}/screening/reset", timeout=5)
    except requests.RequestException:
        pass
