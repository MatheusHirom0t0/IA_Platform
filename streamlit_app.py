"""Streamlit UI para o Banco Ágil - Agente de Screening."""
from typing import Dict, List, Optional

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


def get_credit_limit_from_api(cpf: str) -> dict:
    url = f"{API_BASE_URL}/credit/limit/{cpf}"

    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de crédito: {exc}",
            "limit": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de crédito ({response.status_code}): {detail}",
            "limit": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de crédito ao consultar limite.",
        ),
        "limit": data.get("limit"),
    }


def request_credit_increase_from_api(cpf: str, requested_limit: float) -> dict:
    """
    POST /credit/increase
    body: { "cpf": "...", "requested_limit": 1234.56 }
    """
    url = f"{API_BASE_URL}/credit/increase"
    payload = {"cpf": cpf, "requested_limit": requested_limit}

    try:
        response = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de crédito: {exc}",
            "data": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de crédito ({response.status_code}): {detail}",
            "data": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de crédito ao solicitar aumento.",
        ),
        "data": data.get("data"),
    }


def reset_screening_backend() -> None:
    try:
        requests.post(f"{API_BASE_URL}/screening/reset", timeout=5)
    except requests.RequestException:
        pass


# -------------------- ESTADO E HELPERS --------------------


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "started" not in st.session_state:
        st.session_state.started = False
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = "screening"
    if "cpf" not in st.session_state:
        st.session_state.cpf: Optional[str] = None
    if "awaiting_increase_value" not in st.session_state:
        st.session_state.awaiting_increase_value = False


def build_menu_text() -> str:
    lines: List[str] = ["**Selecione uma das opções:**", ""]
    for num, label in ACTIONS.items():
        lines.append(f"- **{num}** {label}")
    return "\n".join(lines)


def detect_authenticated(reply: str, explicit_flag: bool) -> bool:
    if explicit_flag:
        return True

    text = reply.lower()
    if "autenticação realizada com sucesso" in text:
        return True
    if "você já está autenticado" in text:
        return True

    return False



def maybe_store_cpf_from_input(user_input: str) -> None:
    digits = "".join(ch for ch in user_input if ch.isdigit())
    if len(digits) == 11:
        st.session_state.cpf = digits


def parse_brl_amount(raw: str) -> Optional[float]:
    """
    Converte strings tipo:
    - "5000"
    - "5.000"
    - "5.000,50"
    - "5000,50"
    em float (5000.0, 5000.5, etc).
    """
    text = raw.strip().replace("R$", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        value = float(text)
        if value <= 0:
            return None
        return value
    except ValueError:
        return None


# -------------------- MAIN APP --------------------


def main() -> None:
    st.set_page_config(page_title="Banco Ágil - Agente de Screening")
    st.title("Banco Ágil - Agente de Screening")
    st.caption("Simulador de atendimento bancário com IA.")

    init_session_state()

    if not st.session_state.started:
        welcome = (
            "Olá! Eu sou o Agente de Screening do Banco Ágil. "
            "Vou te ajudar com seu atendimento. "
            "Para começar, por favor, me informe apenas o seu CPF."
        )
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        st.session_state.started = True

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.divider()

    user_input = st.chat_input("Digite sua mensagem...")

    if not user_input:
        return

    original_input = user_input.strip()

    if not st.session_state.authenticated:
        maybe_store_cpf_from_input(original_input)

    # ---------------- TRATAMENTO DE VALOR PARA AUMENTO DE LIMITE ----------------
    if st.session_state.authenticated and st.session_state.awaiting_increase_value:
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        amount = parse_brl_amount(original_input)
        if amount is None:
            error_msg = (
                "Não consegui entender o valor informado. "
                "Por favor, digite apenas o número, por exemplo: `5000` ou `5.000,50`."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.rerun()
            return

        if not st.session_state.cpf:
            error_msg = (
                "❌ Não consegui identificar seu CPF na sessão. "
                "Por favor, finalize a conversa e inicie novamente."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.session_state.awaiting_increase_value = False
            st.rerun()
            return

        result = request_credit_increase_from_api(st.session_state.cpf, amount)
        reply = result["reply"]

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.awaiting_increase_value = False
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # ---------------- OPCÕES NUMÉRICAS PÓS-AUTENTICAÇÃO ----------------

    # 5 → encerra conversa e volta pro início
    if st.session_state.authenticated and original_input == "5":
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        goodbye = "Sessão encerrada. Vamos começar de novo? Informe seu CPF. 👋"
        st.session_state.messages.append({"role": "assistant", "content": goodbye})
        with st.chat_message("assistant"):
            st.markdown(goodbye)

        reset_screening_backend()
        st.session_state.clear()
        st.rerun()
        return

    # 1 → consultar limite
    if st.session_state.authenticated and original_input == "1":
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        if not st.session_state.cpf:
            error_msg = (
                "❌ Não consegui identificar seu CPF na sessão. "
                "Por favor, finalize a conversa e inicie novamente."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg}
            )
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.rerun()
            return

        result = get_credit_limit_from_api(st.session_state.cpf)
        credit_reply = result["reply"]

        st.session_state.messages.append(
            {"role": "assistant", "content": credit_reply}
        )
        with st.chat_message("assistant"):
            st.markdown(credit_reply)

        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # 2 → solicitar aumento de limite
    if st.session_state.authenticated and original_input == "2":
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        ask_value = (
            "Claro! Vamos solicitar um aumento de limite. 💳\n\n"
            "Por favor, me informe o **novo valor de limite** que você deseja, "
            "por exemplo: `5000` ou `7.500,00`."
        )
        st.session_state.messages.append({"role": "assistant", "content": ask_value})
        with st.chat_message("assistant"):
            st.markdown(ask_value)

        st.session_state.awaiting_increase_value = True
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # 3, 4 ainda não implementados
    if st.session_state.authenticated and original_input in {"3", "4"}:
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        reply = (
            "Essa opção ainda não foi implementada no front deste protótipo. 😉\n\n"
            "No backend, teremos rotas específicas para entrevista de crédito e cotação de moeda."
        )
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        st.rerun()
        return

    # ---------------- FLUXO NORMAL (SCREENING) ----------------

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

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()


if __name__ == "__main__":
    main()
