"""TODO"""
import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000"


def send_message_to_triage(message: str) -> str:
    """TODO"""
    url = f"{API_BASE_URL}/triage/chat"

    try:
        response = requests.post(url, json={"message": message}, timeout=30)
    except requests.RequestException as exc:
        return f"❌ Erro ao conectar com a API: {exc}"

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text

        return f"❌ Erro da API ({response.status_code}): {detail}"

    data = response.json()
    return data.get("reply", "❌ Resposta inesperada da API.")


def init_session_state():
    """TODO"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "started" not in st.session_state:
        st.session_state.started = False


def main():
    """TODO"""
    st.set_page_config(page_title="Banco Ágil - Agente de Triagem")
    st.title("Banco Ágil - Agente de Triagem")
    st.caption("Simulador de atendimento bancário com IA (triagem).")

    init_session_state()

    if not st.session_state.started:
        welcome = (
            "Olá! Eu sou o Agente de Triagem do Banco Ágil. "
            "Vou te ajudar com seu atendimento. "
            "Para começar, por favor, me informe apenas o seu CPF (somente números). 😊"
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": welcome}
        )
        st.session_state.started = True

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    user_input = st.chat_input("Digite sua mensagem...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        reply = send_message_to_triage(user_input)

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.markdown(reply)


if __name__ == "__main__":
    main()
