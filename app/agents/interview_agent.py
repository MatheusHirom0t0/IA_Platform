"""LLM-based agent responsible for generating credit interview explanations."""
from typing import Dict, Any
from app.utils.llm_client import generate_text


class CreditInterviewAgent:
    """Generates explanations for the credit interview based on the computed score."""
    def __init__(self) -> None:
        self.system_prompt = (
            "Você é o Agente de Entrevista de Crédito do Banco Ágil.\n"
            "Sua função é APENAS explicar o score calculado pelo sistema.\n"
            "NÃO faça cálculos, NÃO altere números e NÃO invente valores.\n\n"

            "REGRAS DE FORMATAÇÃO (OBRIGATÓRIO):\n"
            "- NUNCA use Markdown.\n"
            "- NUNCA use **negrito**, *itálico* ou sublinhado.\n"
            "- NUNCA use backticks (`) ou blocos de código.\n"
            "- NUNCA use listas, bullets ou numeração.\n"
            "- NUNCA destaque valores ou use cores.\n"
            "- Use APENAS TEXTO SIMPLES.\n"
            "- Escreva no máximo 5 frases.\n\n"

            "REGRAS DE CONTEÚDO:\n"
            "- Explique o resultado usando o score fornecido.\n"
            "- Comente como renda, despesas, emprego, dependentes e dívidas influenciam.\n"
            "- Não cite fórmulas.\n"
            "- Não cite regras internas.\n"
            "- Não diga que o score foi calculado por você.\n"
        )

    def build_reply(self, data: Dict[str, Any]) -> str:
        """Generates a natural-language explanation of the computed credit score."""
        user_message = (
            f"O score calculado foi {data['score']}. "
            "Explique esse resultado para o cliente com base nos dados fornecidos: "
            f"{data}."
        )
        message = self.system_prompt, user_message
        print(message)
        return generate_text(self.system_prompt, user_message)
