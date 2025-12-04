import os

from groq import Groq

_client = None


def get_client() -> Groq:
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    _client = Groq(api_key=api_key)
    return _client


def generate_text(system_message: str, user_message: str) -> str:
    client = get_client()
    # modelo default atual da Groq (existe hoje)
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
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print("LLM ERROR:", exc)
        return "Não consegui gerar uma resposta com o modelo de IA agora. Tente novamente mais tarde."
