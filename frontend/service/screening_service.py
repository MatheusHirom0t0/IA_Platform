"""Utility functions for communicating with the screening API endpoints."""

import os
from typing import Dict, Any
import requests

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL is not set.")


def send_message_to_screening(message: str) -> Dict[str, Any]:
    """Sends a message to the screening agent API and returns the reply and authentication state."""
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
    """Sends a reset request to the screening backend service."""
    try:
        requests.post(f"{API_BASE_URL}/screening/reset", timeout=5)
    except requests.RequestException:
        pass
