import csv
from pathlib import Path
from typing import Dict, List

from app.utils.auth_utils import clean_cpf


class InterviewService:
    def __init__(self, clients_csv_path: str) -> None:
        self._clients_csv_path = Path(clients_csv_path)

    def _load_clients(self) -> List[Dict[str, str]]:
        if not self._clients_csv_path.exists():
            raise FileNotFoundError("Clients CSV not found")

        with self._clients_csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _save_clients(self, rows: List[Dict[str, str]]) -> None:
        if not rows:
            return

        fieldnames = list(rows[0].keys())
        with self._clients_csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def update_client_score(self, cpf: str, score: float) -> Dict[str, object]:
        """
        - Localiza o cliente pelo CPF
        - Atualiza a coluna 'score' no clientes.csv
        - Retorna dados básicos do cliente + novo score
        """
        clients = self._load_clients()
        cpf_clean = clean_cpf(cpf)

        found = None
        for row in clients:
            row_cpf_clean = clean_cpf(row.get("cpf", ""))
            if row_cpf_clean == cpf_clean:
                found = row
                break

        if not found:
            raise ValueError("Client not found")

        # Atualiza o score no CSV
        found["score"] = str(score)

        self._save_clients(clients)

        return {
            "cpf": cpf_clean,
            "nome": found.get("nome"),
            "score": score,
        }
