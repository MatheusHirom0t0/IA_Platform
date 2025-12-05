"""LLM-based agent responsible for generating forex quotation messages."""
from app.utils.llm_client import generate_text


class ForexAgent:
    """Generates automated responses for forex quotation requests."""
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
        base_currency: str,
        target_currency: str,
        amount: float,
        rate: float,
        converted_amount: float,
    ) -> str:
        """Generates an LLM response explaining the exchange rate and converted amount."""
        user_message = (
            "Situação: o cliente consultou cotação de moeda.\n"
            f"Moeda de origem: {base_currency}\n"
            f"Moeda de destino: {target_currency}\n"
            f"Quantidade na origem: {amount}\n"
            f"Taxa de câmbio (1 {base_currency} em {target_currency}): {rate}\n"
            f"Valor convertido: {converted_amount} {target_currency}\n\n"
            "Explique de forma simples qual é a taxa de câmbio e quanto o cliente receberia "
            "na moeda de destino. Termine com uma frase amigável encerrando o atendimento "
            "de cotação."
        )

        return generate_text(self.system_prompt, user_message)
