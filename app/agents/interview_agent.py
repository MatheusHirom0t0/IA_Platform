import json
from typing import Dict, Any

from app.utils.llm_client import generate_text


class CreditInterviewAgent:
    def __init__(self) -> None:
        self.system_prompt = (
            "Você é o Agente de Entrevista de Crédito do Banco Ágil.\n"
            "Sua tarefa é calcular um score de crédito usando uma fórmula fixa e "
            "explicar o resultado para o cliente.\n\n"
            "FÓRMULA DO SCORE (0 a 1000):\n"
            "score = (renda_mensal / (despesas_mensais + 1)) * peso_renda "
            "+ peso_emprego + peso_dependentes + peso_dividas\n\n"
            "Pesos:\n"
            "- peso_renda = 30\n\n"
            "- peso_emprego:\n"
            "  - formal: 300\n"
            "  - autônomo: 200\n"
            "  - desempregado: 0\n\n"
            "- peso_dependentes:\n"
            "  - 0 dependentes: 100\n"
            "  - 1 dependente: 80\n"
            "  - 2 dependentes: 60\n"
            "  - 3 ou mais dependentes: 30\n\n"
            "- peso_dividas:\n"
            "  - sim: -100\n"
            "  - não: 100\n\n"
            "REGRAS IMPORTANTES:\n"
            "- Sempre aplique exatamente a fórmula acima.\n"
            "- Garanta que o score final esteja entre 0 e 1000.\n"
            "- Arredonde o score para no máximo 2 casas decimais.\n\n"
            "FORMATO DE RESPOSTA (OBRIGATÓRIO):\n"
            "- Responda SEMPRE e APENAS em JSON válido.\n"
            "- Use o formato:\n"
            "{\n"
            '  \"score\": <número entre 0 e 1000>,\n'
            '  \"reply\": \"texto curto explicando o resultado para o cliente em português do Brasil\"\n'
            "}\n\n"
            "REGRAS DO CAMPO 'reply':\n"
            "- Fale diretamente com o cliente (\"seu score\", \"você\").\n"
            "- Seja simples e direto, no máximo 5 frases.\n"
            "- Explique por que o score ficou mais forte ou mais limitado\n"
            "  com base em renda, despesas, emprego, dependentes e dívidas.\n"
            "- Não explique a fórmula, apenas o resultado.\n"
        )

    def calculate_score_and_reply(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia os dados da entrevista para o modelo e espera um JSON:
        {
          "score": <float>,
          "reply": "<texto para o cliente>"
        }
        """
        user_message = json.dumps(interview_data, ensure_ascii=False)

        raw = generate_text(self.system_prompt, user_message)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback em caso de erro no parse do JSON da IA
            return {
                "score": 500.0,
                "reply": (
                    "Não consegui recalcular seu score de forma automática agora, "
                    "então usei um valor intermediário temporário. "
                    "Tente novamente em alguns instantes."
                ),
            }
        print(raw)
        # Garantias mínimas
        score_raw = parsed.get("score", 0)
        try:
            score = float(score_raw)
        except (TypeError, ValueError):
            score = 0.0

        # Clampa entre 0 e 1000
        score = max(0.0, min(1000.0, score))

        reply = parsed.get("reply") or "Seu score foi recalculado com base no seu perfil financeiro."

        return {"score": score, "reply": str(reply)}
