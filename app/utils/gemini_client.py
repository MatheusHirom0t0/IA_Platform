import os

import google.generativeai as genai


_model = None


def get_model() -> genai.GenerativeModel:
    global _model
    if _model is not None:
        return _model

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)

    # usa um modelo estável da lib atual
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")
    _model = genai.GenerativeModel(model_name)
    return _model


def generate_text(system_instruction: str, user_message: str) -> str:
    model = get_model()
    prompt = system_instruction + "\n\n" + user_message

    try:
        result = model.generate_content(prompt)
    except Exception as exc:
        # loga o erro e deixa o caller usar o fallback
        print("ERROR CALLING GEMINI:", exc)
        return ""

    text = getattr(result, "text", None)
    if not text and getattr(result, "candidates", None):
        candidate = result.candidates[0]
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None)
        if parts:
            text = "".join(p.text for p in parts if getattr(p, "text", None))

    return (text or "").strip()
