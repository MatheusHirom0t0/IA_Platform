from typing import Dict

from app.utils.llm_client import generate_text


class CreditAgent:
    def __init__(self) -> None:
        self.system_prompt = (
            "Você é o Agente de Crédito do Banco Ágil.\n"
            "Sempre responda em português do Brasil, em TOM SIMPLES e DIRETO.\n\n"
            "REGRAS DE RESPOSTA:\n"
            "- Responda CURTO: no máximo 4 frases ou 500 caracteres.\n"
            "- Use no máximo 2 parágrafos.\n"
            "- NÃO use títulos, cabeçalhos, listas grandes nem assinatura.\n"
            "- NÃO use negrito, itálico ou sublinhado. Apenas texto simples.\n"
            "- Não junte palavras sem espaço. Garanta espaçamento normal.\n"
            "- Ao falar de dinheiro, use formato brasileiro, por exemplo: R$ 13.150,00.\n"
            "- Não quebre a linha no meio de valores monetários.\n"
            "- Cite cada valor (limite atual, solicitado, máximo permitido) no máximo uma vez.\n"
        )

    # ----------------- CONSULTA DE LIMITE -----------------

    def build_limit_reply(self, cpf: str, limit_value: float) -> str:
        user_message = (
            "Situação: o cliente está consultando o limite de crédito atual.\n"
            f"Dados:\n- CPF: {cpf}\n- Limite atual (numérico): {limit_value}\n\n"
            "Explique de forma rápida qual é o limite de crédito dele e diga que, "
            "se ele quiser, pode solicitar um aumento de limite ou uma entrevista de crédito."
        )

        return generate_text(self.system_prompt, user_message)

    # ----------------- PEDIDO DE AUMENTO DE LIMITE -----------------

    def build_increase_reply(self,data: Dict[str, str]) -> str:
        """
        A IA não recebe NENHUM número.
        Ela só recebe instruções sobre COMO responder.
        """
        status = data["status"]

        base_instruction = (
            "Você é um analista de crédito. "
            "Você NÃO deve incluir números. "
            "Você NÃO deve tentar adivinhar valores. "
            "Você apenas explica o motivo da decisão."
        )

        if status == "requested_below_current":
            instruction = (
                "Explique que o pedido foi recusado porque o cliente solicitou um limite menor "
                "que o limite atual, e este canal só serve para aumentos. "
                "Convide o cliente a informar um valor maior."
            )

        elif status == "approved":
            instruction = (
                "Explique que o pedido foi aprovado e forneça uma razão curta. "
                "Nunca inclua números."

            )

        else:
            instruction = (
                "Explique que o pedido foi recusado porque ultrapassa o limite permitido pelo score. "
                "Sugira pedir um valor menor ou tentar entrevista de crédito."
            )
        user_message = base_instruction + "\n\n" + instruction

        return generate_text(self.system_prompt,user_message)