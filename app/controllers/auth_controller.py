"""Authentication controller responsible for validating CPF and birth date against stored client data."""
from typing import Optional, Dict, List
from fastapi import HTTPException, status
from app.utils.auth_utils import read_csv, clean_cpf


class AuthController:
    """Provides methods to locate and authenticate clients based on CPF and birth date."""
    def __init__(self) -> None:
        self._clients: List[Dict[str, str]] = read_csv()

    def find_client_by_cpf(self, cpf: str) -> Optional[Dict[str, str]]:
        """Returns the client record matching the given CPF, or None if not found."""
        target = clean_cpf(cpf)
        for row in self._clients:
            if clean_cpf(row["cpf"]) == target:
                return row
        return None

    def login(self, cpf: str, birth_date: str) -> Dict[str, Dict[str, str]]:
        """Validates CPF and birth date, returning the client data if correct; raises 401 otherwise."""
        cleaned = clean_cpf(cpf)
        for row in self._clients:
            if clean_cpf(row["cpf"]) == cleaned and row["data_nascimento"] == birth_date:
                return {"client": row}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CPF or birth date."
        )
