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

    def build_increase_reply(self, data: Dict[str, str]) -> str:
        """
        data:
        {
            'cpf': '52189293871',
            'current_limit': '7000.00',
            'requested_limit': '13000.00',
            'max_allowed_limit': '15000.00',
            'status': 'approved' | 'rejected' | 'requested_below_current'
        }
        """

        cpf = data["cpf"]
        status = data["status"]
        current_limit = data["current_limit"]
        requested_limit = data["requested_limit"]
        max_allowed = data["max_allowed_limit"]

        base_description = (
            "Situação: análise de pedido de aumento de limite de crédito.\n"
            f"Dados do cliente:\n"
            f"- CPF: {cpf}\n"
            f"- Limite atual (numérico): {current_limit}\n"
            f"- Limite solicitado (numérico): {requested_limit}\n"
            f"- Limite máximo permitido pelo score (numérico): {max_allowed}\n"
            f"- Status da análise: {status}\n\n"
        )

        if status == "requested_below_current":
            extra_instruction = (
                "Explique que o valor solicitado é menor que o limite atual e que este canal "
                "serve apenas para pedir aumento, não para reduzir limite. "
                "Convide o cliente a informar um valor maior, se desejar."
            )
        elif status == "approved":
            extra_instruction = (
                "Explique de forma bem direta que o pedido foi APROVADO, informe qual era o limite atual "
                "e qual será o novo limite, e diga que a atualização será feita conforme as regras internas do banco."
            )
        else:  # rejected
            extra_instruction = (
                "Explique de forma direta que o pedido foi RECUSADO porque o valor solicitado está acima "
                "do limite máximo permitido pelo score. Sugira que ele peça um valor menor ou faça uma "
                "entrevista de crédito no futuro."
            )

        user_message = base_description + extra_instruction

        return generate_text(self.system_prompt, user_message)
