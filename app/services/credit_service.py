"""Service layer for credit operations such as limits, scores, and increase requests."""

import csv
import datetime
from pathlib import Path
from typing import Dict, List


class CreditService:
    """Provides credit-related business logic based on CSV-stored client, score, and request data."""

    def __init__(
        self,
        clients_csv_path: str,
        score_limits_csv_path: str,
        requests_csv_path: str,
    ) -> None:
        self.clients_csv_path = Path(clients_csv_path)
        self.score_limits_csv_path = Path(score_limits_csv_path)
        self.requests_csv_path = Path(requests_csv_path)

    def read_clients(self) -> List[Dict[str, str]]:
        """Reads and returns all client records from the clients CSV file."""
        with self.clients_csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def read_score_limits(self) -> List[Dict[str, str]]:
        """Reads and returns all score-to-limit rules from the score limits CSV file."""
        with self.score_limits_csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def normalize_cpf(self, cpf: str) -> str:
        """Removes all non-digit characters from a CPF string."""
        return "".join(ch for ch in cpf if ch.isdigit())

    def get_client_by_cpf(self, cpf: str) -> Dict[str, str]:
        """Finds and returns a client record by CPF, raising ValueError if not found."""
        target = self.normalize_cpf(cpf)
        clients = self.read_clients()
        for row in clients:
            row_cpf = self.normalize_cpf(row.get("cpf", ""))
            if row_cpf == target:
                return row
        raise ValueError("Client not found")

    def get_current_limit(self, cpf: str) -> float:
        """Returns the client's current credit limit as a float, raising if missing."""
        client = self.get_client_by_cpf(cpf)

        if "limite_atual" not in client or client["limite_atual"] in (None, ""):
            raise ValueError(f"Missing 'limite_atual' for client: {client}")

        raw = str(client["limite_atual"]).replace(",", ".")
        return float(raw)

    def get_current_score(self, cpf: str) -> float:
        """Returns the client's current score as a float, raising if missing."""
        client = self.get_client_by_cpf(cpf)

        if "score" not in client or client["score"] in (None, ""):
            raise ValueError(f"Missing 'score' for client: {client}")

        raw = str(client["score"]).replace(",", ".")
        return float(raw)

    def get_max_allowed_limit(self, score: float) -> float:
        """Determines the maximum credit limit allowed for the given score based on score rules."""
        rows = self.read_score_limits()

        for row in rows:
            min_score = float(row.get("score_min", 0))
            max_score = float(row.get("score_max", 0))
            max_limit = float(row.get("limite_maximo", 0))

            if min_score <= score <= max_score:
                return max_limit

        return 0.0

    def append_request(
        self,
        cpf: str,
        current_limit: float,
        requested_limit: float,
        status: str,
    ) -> None:
        """Appends a credit limit increase request record to the requests CSV file."""
        fieldnames = [
            "cpf_cliente",
            "data_hora_solicitacao",
            "limite_atual",
            "novo_limite_solicitado",
            "status_pedido",
        ]

        exists = self.requests_csv_path.exists()
        with self.requests_csv_path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not exists:
                writer.writeheader()
            writer.writerow(
                {
                    "cpf_cliente": cpf,
                    "data_hora_solicitacao": datetime.datetime.utcnow().isoformat(),
                    "limite_atual": current_limit,
                    "novo_limite_solicitado": requested_limit,
                    "status_pedido": status,
                }
            )

    def evaluate_increase_request(
        self, cpf: str, requested_limit: float
    ) -> Dict[str, str]:
        """Evaluates a credit limit increase request and returns a summary including status and limits."""
        current_limit = self.get_current_limit(cpf)

        if requested_limit < current_limit:
            status = "requested_below_current"
            max_allowed = current_limit

            self.append_request(cpf, current_limit, requested_limit, status)

            return {
                "cpf": cpf,
                "current_limit": f"{current_limit:.2f}",
                "requested_limit": f"{requested_limit:.2f}",
                "max_allowed_limit": f"{max_allowed:.2f}",
                "status": status,
            }

        score = self.get_current_score(cpf)
        max_allowed = self.get_max_allowed_limit(score)

        status = "rejected"
        if requested_limit <= max_allowed:
            status = "approved"

        self.append_request(cpf, current_limit, requested_limit, status)

        if status == "approved":
            self.update_client_limit(cpf, requested_limit)

        return {
            "cpf": cpf,
            "current_limit": f"{current_limit:.2f}",
            "requested_limit": f"{requested_limit:.2f}",
            "max_allowed_limit": f"{max_allowed:.2f}",
            "status": status,
        }

    def update_client_limit(self, cpf: str, new_limit: float) -> None:
        """Updates the client's current limit in the clients, raising if client is not found."""
        clients = self.read_clients()
        target = self.normalize_cpf(cpf)

        updated = False
        for row in clients:
            row_cpf = self.normalize_cpf(row.get("cpf", ""))
            if row_cpf == target:
                row["limite_atual"] = f"{new_limit:.2f}"
                updated = True
                break

        if not updated:
            raise ValueError("Client not found when trying to update limit")

        fieldnames = list(clients[0].keys())
        with self.clients_csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clients)
