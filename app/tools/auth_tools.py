# app/tools/auth_tool.py
from typing import Dict

from fastapi import HTTPException
from langchain.tools import tool
from app.controllers.auth_controller import AuthController

controller = AuthController()


@tool
def authenticate_client(cpf: str, birth_date: str) -> Dict:
    """
    Autentica um cliente do Banco Ágil usando CPF e data de nascimento.

    Args:
        cpf: CPF com ou sem formatação.
        birth_date: Data no formato YYYY-MM-DD ou YYYYMMDD.

    Returns:
        {
            "authenticated": bool,
            "client": { ... } ou None,
            "status_code": int,
            "error": str ou None
        }
    """
    try:
        result = controller.login(cpf=cpf, birth_date=birth_date)
        return {
            "authenticated": True,
            "client": result.get("client"),
            "status_code": 200,
            "error": None,
        }
    except HTTPException as exc:
        return {
            "authenticated": False,
            "client": None,
            "status_code": exc.status_code,
            "error": str(exc.detail),
        }
