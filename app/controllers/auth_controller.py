"""TODO"""
from typing import Optional, Dict, List

from fastapi import HTTPException, status

from app.utils.auth_utils import read_csv, clean_cpf


class AuthController:
    """TODO"""
    def __init__(self) -> None:

        self._clients: List[Dict[str, str]] = read_csv()

    def find_client_by_cpf(self, cpf: str) -> Optional[Dict[str, str]]:
        """TODO"""
        cleaned_cpf = clean_cpf(cpf)

        for row in self._clients:
            if clean_cpf(row["cpf"]) == cleaned_cpf:
                return row

        return None

    def login(self, cpf: str, birth_date: str) -> Dict[str, Dict[str, str]]:
        """TODO"""
        cleaned_cpf = clean_cpf(cpf)

        for row in self._clients:
            if (
                clean_cpf(row["cpf"]) == cleaned_cpf
                and row["data_nascimento"] == birth_date
            ):
                return {"client": row}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CPF or birth date.",
        )
