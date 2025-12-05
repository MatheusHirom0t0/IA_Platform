"""LLM Client for Groq"""
import os
from functools import lru_cache
from groq import Groq, GroqError


@lru_cache(maxsize=1)
def get_client() -> Groq:
    """Returns a cached Groq client instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    return Groq(api_key=api_key)


def generate_text(system_message: str, user_message: str) -> str:
    """Generate text using Groq LLM."""
    client = get_client()

    model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.4,
        )

        # Objeto ChatCompletionMessage
        chat_msg = response.choices[0].message

        # Conteúdo REAL da resposta
        content = chat_msg.content or ""

        return content.strip()

    except GroqError as exc:
        print("LLM ERROR:", exc)
        return (
            "Não consegui gerar uma resposta com o modelo de IA agora. "
            "Tente novamente mais tarde."
        )
