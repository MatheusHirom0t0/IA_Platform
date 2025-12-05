"""TODO"""
import csv
from pathlib import Path
from typing import Dict, List

from app.utils.auth_utils import clean_cpf


class InterviewService:
    """TODO"""
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
        renda_mensal: float,
        despesas_mensais: float,
        tipo_emprego: str,
        numero_dependentes: int,
        tem_dividas: bool,
    ) -> float:
        """TODO"""

        peso_renda = 30

        peso_emprego = {
            "formal": 300,
            "autônomo": 200,
            "autonomo": 200,
            "desempregado": 0,
        }.get(tipo_emprego.lower(), 0)

        if numero_dependentes <= 0:
            peso_dependentes = 100
        elif numero_dependentes == 1:
            peso_dependentes = 80
        elif numero_dependentes == 2:
            peso_dependentes = 60
        else:
            peso_dependentes = 30

        peso_dividas = -100 if tem_dividas else 100

        base = (renda_mensal / (despesas_mensais + 1)) * peso_renda

        score = base + peso_emprego + peso_dependentes + peso_dividas

        return round(max(0, min(1000, score)), 2)


    def update_client_score(self, cpf: str, score: float) -> Dict[str, object]:
        """TODO"""
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
