"""Service layer for credit interview score calculation and client score updates."""

import csv
from pathlib import Path
from typing import Dict, List

from app.utils.auth_utils import clean_cpf


class InterviewService:
    """Handles credit score computation and persistence for interview-related operations."""

    def __init__(self, clients_csv_path: str) -> None:
        self._clients_csv_path = Path(clients_csv_path)

    def _load_clients(self) -> List[Dict[str, str]]:
        if not self._clients_csv_path.exists():
            raise FileNotFoundError("Clients CSV not found")

        with self._clients_csv_path.open("r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _save_clients(self, rows: List[Dict[str, str]]) -> None:
        if not rows:
            return

        fields = list(rows[0].keys())

        with self._clients_csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def calculate_score(
        self,
        monthly_income: float,
        monthly_expenses: float,
        job_type: str,
        dependents_count: int,
        has_debt: bool,
    ) -> float:
        """Calculates a credit score based on income, expenses, employment type, dependents, and debts."""
        income_weight = 30

        employment_weight = {
            "formal": 300,
            "autônomo": 200,
            "autonomo": 200,
            "desempregado": 0,
        }.get(job_type.lower(), 0)

        if dependents_count <= 0:
            dependents_weight = 100
        elif dependents_count == 1:
            dependents_weight = 80
        elif dependents_count == 2:
            dependents_weight = 60
        else:
            dependents_weight = 30

        debt_weight = -100 if has_debt else 100

        base = (monthly_income / (monthly_expenses + 1)) * income_weight

        score = base + employment_weight + dependents_weight + debt_weight

        return round(max(0, min(1000, score)), 2)

    def update_client_score(self, cpf: str, score: float) -> Dict[str, object]:
        """Updates the client's score and returns a summary with CPF, name, and new score."""
        clients = self._load_clients()
        cpf_clean = clean_cpf(cpf)

        found = None
        for row in clients:
            if clean_cpf(row.get("cpf", "")) == cpf_clean:
                found = row
                break

        if not found:
            raise ValueError("Client not found")

        found["score"] = str(score)
        self._save_clients(clients)

        return {
            "cpf": cpf_clean,
            "nome": found.get("nome"),
            "score": score,
        }
