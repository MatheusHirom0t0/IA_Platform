"""TODO"""
from app.utils.llm_client import generate_text


class ForexAgent:
    """TODO"""
    def __init__(self) -> None:
        self.system_prompt = (
            "Você é o Agente de Câmbio do Banco Ágil.\n"
            "Responda sempre em português do Brasil, de forma simples.\n\n"
            "REGRAS:\n"
            "- Responda curto (até 4 frases).\n"
            "- Não use listas, títulos ou formatação especial.\n"
            "- Use formato brasileiro de moeda (R$ 1.234,56).\n"
        )

    def build_quote_reply(
        self,
        base: str,
        target: str,
        amount: float,
        rate: float,
        converted_amount: float,
    ) -> str:
        """TODO"""
        user_message = (
            "Situação: o cliente consultou cotação de moeda.\n"
            f"Moeda de origem: {base}\n"
            f"Moeda de destino: {target}\n"
            f"Quantidade na origem: {amount}\n"
            f"Taxa de câmbio (1 {base} em {target}): {rate}\n"
            f"Valor convertido: {converted_amount} {target}\n\n"
            "Explique de forma simples qual é a taxa de câmbio e quanto o cliente receberia "
            "na moeda de destino. Termine com uma frase amigável encerrando o atendimento "
            "de cotação."
        )

        return generate_text(self.system_prompt, user_message)
