import os
from typing import List, Dict

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Use um modelo rápido; ajuste se quiser outro
_MODEL_NAME = "gemini-1.5-flash"


def generate_reply(system_prompt: str, messages: List[Dict[str, str]]) -> str:
    """
    messages: lista de { "role": "user" | "assistant", "content": "..." }
    """
    model = genai.GenerativeModel(_MODEL_NAME)

    # Converte para o formato esperado pelo SDK
    chat = []
    if system_prompt:
        chat.append({"role": "user", "parts": [system_prompt]})
    for m in messages:
        chat.append({"role": m["role"], "parts": [m["content"]]})

    response = model.generate_content(chat)
    return response.text.strip() if response and response.text else ""
