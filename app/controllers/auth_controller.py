""""TODO"""
from typing import Dict

from fastapi import HTTPException

from app.utils.auth_utils import (
    read_csv,
    clean_cpf,
    normalize_birth_date,
)


class AuthController:
    """TODO"""
    def login(self, cpf: str, birth_date: str) -> Dict:
        """TODO"""
        try:
            normalized_birth_date = normalize_birth_date(birth_date)
        except TypeError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        try:
            rows = read_csv()
        except (FileNotFoundError, RuntimeError) as exc:
            raise HTTPException(status_code=500, detail=str(exc))

        cleaned_cpf = clean_cpf(cpf)

        for row in rows:
            row_cpf = clean_cpf(row.get("cpf", ""))
            row_birth = row.get("data_nascimento", "")

            if row_cpf == cleaned_cpf and row_birth == normalized_birth_date:
                client = {
                    "cpf": row_cpf,
                    "data_nascimento": row_birth,
                    "nome": row.get("nome", ""),
                }
                return {"message": "logado", "client": client}

        raise HTTPException(status_code=401, detail="Invalid credentials")
