"""Streamlit UI para o Banco Ágil - Agente de Screening."""
from typing import Dict, List

import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"

# Mapeamento fixo de opções exibidas no menu
ACTIONS: Dict[str, str] = {
    "1": "Consultar limite de crédito",
    "2": "Solicitar aumento de limite",
    "3": "Iniciar entrevista de crédito",
    "4": "Consultar cotação de moeda",
    "5": "Encerrar conversa",
}


# -------------------- CHAMADAS DE API --------------------


def send_message_to_screening(message: str) -> dict:
    """
    Envia mensagem para o agente de screening e retorna:
    {
        "reply": str,
        "authenticated": bool
    }
    """
    url = f"{API_BASE_URL}/screening/chat"

    try:
        response = requests.post(url, json={"message": message}, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de screening: {exc}",
            "authenticated": False,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de screening ({response.status_code}): {detail}",
            "authenticated": False,
        }

    data = response.json()
    return {
        "reply": data.get("reply", "❌ Resposta inesperada da API de screening."),
        "authenticated": data.get("authenticated", False),
    }


def send_message_to_credit(message: str) -> dict:
    """
    Envia mensagem para o agente de crédito e retorna:
    {
        "reply": str
    }

    Espera uma rota POST /credit/chat com body:
    { "message": "..." }
    e resposta:
    { "reply": "..." }
    """
    url = f"{API_BASE_URL}/credit/chat"

    try:
        response = requests.post(url, json={"message": message}, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de crédito: {exc}",
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de crédito ({response.status_code}): {detail}",
        }

    data = response.json()
    return {
        "reply": data.get("reply", "❌ Resposta inesperada da API de crédito."),
    }


def reset_screening_backend() -> None:
    """
    Chama o endpoint de reset do agente de triagem.
    Ignora erros de conexão para não quebrar o front.
    """
    try:
        requests.post(f"{API_BASE_URL}/screening/reset", timeout=5)
    except requests.RequestException:
        pass


# -------------------- ESTADO E HELPERS --------------------


def init_session_state() -> None:
    """Inicializa o estado da sessão do Streamlit."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "started" not in st.session_state:
        st.session_state.started = False
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_agent" not in st.session_state:
        # screening, menu, credit, etc (se quiser expandir depois)
        st.session_state.current_agent = "screening"


def build_menu_text() -> str:
    """
    Monta o menu com cada opção em UMA LINHA,
    usando lista em markdown.
    """
    lines: List[str] = ["**Selecione uma das opções:**", ""]
    for num, label in ACTIONS.items():
        lines.append(f"- **{num}** {label}")
    return "\n".join(lines)


def detect_authenticated(reply: str, explicit_flag: bool) -> bool:
    """
    Detecta se está autenticado:
    - Usa o flag explícito da API se vier;
    - OU tenta detectar por texto da resposta.
    """
    if explicit_flag:
        return True

    text = reply.lower()
    if "autenticação realizada com sucesso" in text:
        return True
    if "você já está autenticado" in text:
        return True

    return False


# -------------------- MAIN APP --------------------


def main() -> None:
    """Aplicação Streamlit principal."""
    st.set_page_config(page_title="Banco Ágil - Agente de Screening")
    st.title("Banco Ágil - Agente de Screening")
    st.caption("Simulador de atendimento bancário com IA.")

    init_session_state()

    # Mensagem inicial
    if not st.session_state.started:
        welcome = (
            "Olá! Eu sou o Agente de Screening do Banco Ágil. "
            "Vou te ajudar com seu atendimento. "
            "Para começar, por favor, me informe apenas o seu CPF."
        )
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        st.session_state.started = True

    # Renderizar histórico
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.divider()

    # Input do usuário
    user_input = st.chat_input("Digite sua mensagem...")

    if not user_input:
        return

    original_input = user_input.strip()

    # ---------------- OPCÕES NUMÉRICAS PÓS-AUTENTICAÇÃO ----------------
    # 5 → encerra conversa e volta pro início (CPF)
    if st.session_state.authenticated and original_input == "5":
        # Mostra o que o usuário digitou
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        # Opcional: pode mostrar uma mensagem de encerramento antes de resetar
        goodbye = "Sessão encerrada. Vamos começar de novo? Informe seu CPF. 👋"
        st.session_state.messages.append({"role": "assistant", "content": goodbye})
        with st.chat_message("assistant"):
            st.markdown(goodbye)

        # Reset backend (agente volta para ask_cpf)
        reset_screening_backend()

        # Reset frontend (limpa tudo e recomeça)
        st.session_state.clear()
        st.rerun()
        return

    # 1 → chama agente de crédito (consultar limite)
    if st.session_state.authenticated and original_input == "1":
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        # Aqui você pode mudar a mensagem de comando que será enviada ao agente de crédito
        credit_result = send_message_to_credit("consultar limite de crédito")
        credit_reply = credit_result["reply"]

        st.session_state.messages.append(
            {"role": "assistant", "content": credit_reply}
        )
        with st.chat_message("assistant"):
            st.markdown(credit_reply)

        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # 2, 3, 4 ainda não implementados → placeholder
    if st.session_state.authenticated and original_input in {"2", "3", "4"}:
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        reply = "Essa opção ainda não foi implementada neste protótipo. 😉"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        st.rerun()
        return

    # ---------------- FLUXO NORMAL (SCREENING) ----------------
    # Se ainda não autenticou ou está enviando texto livre
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = send_message_to_screening(user_input)
    reply = result["reply"]

    # Se autenticou agora → responde com mensagem + menu junto
    if not st.session_state.authenticated and detect_authenticated(
        reply, result.get("authenticated", False)
    ):
        st.session_state.authenticated = True
        st.session_state.current_agent = "menu"

        menu_text = build_menu_text()
        full_message = f"{reply}\n\n{menu_text}"

        st.session_state.messages.append(
            {"role": "assistant", "content": full_message}
        )
        with st.chat_message("assistant"):
            st.markdown(full_message)

        st.rerun()
        return

    # Caso normal (não autenticou ainda ou já estava autenticado e mandou texto livre)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()


if __name__ == "__main__":
    main()
