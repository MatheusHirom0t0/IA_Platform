import csv
import os
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv

from app.core.gemini_client import generate_reply

load_dotenv()

SOLICITACOES_PATH = os.getenv(
    "SOLICITACOES_PATH", "data/solicitacoes_aumento_limite.csv"
)
SCORE_LIMITES_PATH = os.getenv(
    "SCORE_LIMITES_PATH", "data/score_limite.csv"
)


class CreditAgent:
    def __init__(self) -> None:
        self.stage = "idle"
        self.requested_limit: float = 0.0

    def _ensure_solicitacoes_header(self) -> None:
        if not os.path.exists(SOLICITACOES_PATH):
            with open(SOLICITACOES_PATH, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "cpf_cliente",
                        "data_hora_solicitacao",
                        "limite_atual",
                        "novo_limite_solicitado",
                        "status_pedido",
                    ]
                )

    def _load_score_table(self) -> Dict[int, float]:
        """
        Espera um CSV score_limite.csv com colunas:
        score_min (int), score_max (int), limite_maximo (float)
        Exemplo:
        0,300,1000.0
        301,600,5000.0
        601,1000,20000.0
        """
        table = {}
        if not os.path.exists(SCORE_LIMITES_PATH):
            return table

        with open(SCORE_LIMITES_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                score_min = int(row["score_min"])
                score_max = int(row["score_max"])
                limite_maximo = float(row["limite_maximo"])
                for s in range(score_min, score_max + 1):
                    table[s] = limite_maximo
        return table

    def _decide_status(self, score: int, current_limit: float, new_limit: float) -> str:
        table = self._load_score_table()
        max_allowed = table.get(score)

        if max_allowed is None:
            # se não achar na tabela, seja conservador
            return "rejeitado"

        if new_limit <= max_allowed:
            return "aprovado"
        return "rejeitado"

    def start(self, client_row: Dict[str, str]) -> str:
        """
        Inicia a conversa de crédito após autenticação.
        client_row: linha do clientes.csv para o usuário autenticado.
        """
        self.stage = "waiting_choice"
        limit_str = client_row.get("limite_atual", "0")
        try:
            limit_val = float(limit_str.replace(",", "."))
        except ValueError:
            limit_val = 0.0

        prompt = (
            f"O cliente tem limite atual de R$ {limit_val:,.2f}. "
            "Explique de forma amigável as opções: "
            "consultar limite atual ou solicitar aumento de limite."
        )

        reply = generate_reply(
            system_prompt=(
                "Você é um agente de crédito do Banco Ágil. "
                "Seja objetivo, amigável e use português do Brasil."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        return reply

    def handle_message(self, client_row: Dict[str, str], text: str) -> str:
        """
        Continua o fluxo de crédito.
        """
        if self.stage == "waiting_choice":
            lowered = text.lower()
            if "consultar" in lowered or "ver limite" in lowered or "limite" in lowered:
                limit_str = client_row.get("limite_atual", "0")
                try:
                    limit_val = float(limit_str.replace(",", "."))
                except ValueError:
                    limit_val = 0.0

                prompt = (
                    f"O limite atual do cliente é R$ {limit_val:,.2f}. "
                    "Explique isso para ele de forma clara e curta."
                )
                return generate_reply(
                    "Você é um agente de crédito do Banco Ágil.",
                    [{"role": "user", "content": prompt}],
                )

            # assume que o cliente quer pedir aumento
            self.stage = "waiting_new_limit"
            return "Claro! Qual novo limite de crédito você deseja solicitar? (informe um valor numérico, ex: 5000)"

        if self.stage == "waiting_new_limit":
            numeric = "".join(ch for ch in text if ch.isdigit() or ch in ",.")
            if not numeric:
                return "Não consegui entender o valor. Por favor, envie apenas o número do novo limite desejado."

            try:
                self.requested_limit = float(numeric.replace(",", "."))
            except ValueError:
                return "Não consegui entender o valor. Tente novamente enviando apenas números."

            # calcula decisão
            score_str = client_row.get("score", "0")
            try:
                score_val = int(score_str)
            except ValueError:
                score_val = 0

            limit_str = client_row.get("limite_atual", "0")
            try:
                current_limit = float(limit_str.replace(",", "."))
            except ValueError:
                current_limit = 0.0

            status = self._decide_status(score_val, current_limit, self.requested_limit)

            # grava CSV
            self._ensure_solicitacoes_header()
            now_iso = datetime.utcnow().isoformat()
            cpf = client_row.get("cpf", "")

            with open(SOLICITACOES_PATH, "a", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        cpf,
                        now_iso,
                        current_limit,
                        self.requested_limit,
                        status,
                    ]
                )

            # mensagem via Gemini
            if status == "aprovado":
                decision_text = (
                    f"O cliente tem score {score_val} e limite atual R$ {current_limit:,.2f}. "
                    f"Ele pediu aumento para R$ {self.requested_limit:,.2f} e a solicitação foi APROVADA. "
                    "Explique a aprovação de forma clara e positiva."
                )
            else:
                decision_text = (
                    f"O cliente tem score {score_val} e limite atual R$ {current_limit:,.2f}. "
                    f"Ele pediu aumento para R$ {self.requested_limit:,.2f} e a solicitação foi REJEITADA. "
                    "Explique o motivo de forma empática e ofereça a possibilidade de "
                    "ser encaminhado para uma entrevista de crédito para tentar melhorar o score."
                )

            self.stage = "finished"

            return generate_reply(
                "Você é um agente de crédito do Banco Ágil.",
                [{"role": "user", "content": decision_text}],
            )

        # fallback
        return "O fluxo de crédito para esta solicitação já foi concluído."
