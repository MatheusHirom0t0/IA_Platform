"""Streamlit UI para o Banco Ágil - Agente de Screening."""
from typing import Dict, List, Optional

import re
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


def run_credit_interview_from_api(
    cpf: str,
    renda_mensal: float,
    despesas_mensais: float,
    tipo_emprego: str,
    numero_dependentes: int,
    tem_dividas: bool,
) -> dict:
    """
    POST /interview
    body:
    {
        "cpf": "...",
        "renda_mensal": ...,
        "despesas_mensais": ...,
        "tipo_emprego": "...",
        "numero_dependentes": ...,
        "tem_dividas": true/false
    }
    """
    url = f"{API_BASE_URL}/interview"
    payload = {
        "cpf": cpf,
        "renda_mensal": renda_mensal,
        "despesas_mensais": despesas_mensais,
        "tipo_emprego": tipo_emprego,
        "numero_dependentes": numero_dependentes,
        "tem_dividas": tem_dividas,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de entrevista de crédito: {exc}",
            "score": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de entrevista de crédito ({response.status_code}): {detail}",
            "score": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de entrevista de crédito.",
        ),
        "score": data.get("score"),
    }


def get_fx_quote_from_api(base: str, target: str, amount: float) -> dict:
    """
    POST /forex/quote
    body: { "base": "USD", "target": "BRL", "amount": 100.0 }
    """
    url = f"{API_BASE_URL}/forex/quote"
    payload = {"base": base, "target": target, "amount": amount}

    try:
        response = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as exc:
        return {
            "reply": f"❌ Erro ao conectar com a API de câmbio: {exc}",
            "rate": None,
            "converted_amount": None,
        }

    if response.status_code != 200:
        try:
            data = response.json()
            detail = data.get("detail") or data
        except Exception:
            detail = response.text
        return {
            "reply": f"❌ Erro da API de câmbio ({response.status_code}): {detail}",
            "rate": None,
            "converted_amount": None,
        }

    data = response.json()
    return {
        "reply": data.get(
            "reply",
            "❌ Resposta inesperada da API de câmbio.",
        ),
        "rate": data.get("rate"),
        "converted_amount": data.get("converted_amount"),
    }


def reset_screening_backend() -> None:
    try:
        requests.post(f"{API_BASE_URL}/screening/reset", timeout=5)
    except requests.RequestException:
        pass


# -------------------- ESTADO, HELPERS E SANITIZAÇÃO --------------------


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
    if "interview_stage" not in st.session_state:
        st.session_state.interview_stage: Optional[str] = None
    if "interview_data" not in st.session_state:
        st.session_state.interview_data = {}
    if "awaiting_fx_params" not in st.session_state:
        st.session_state.awaiting_fx_params = False


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


def sanitize_ai_reply(text: str) -> str:
    """
    Remove formatação Markdown básica da resposta da IA
    para evitar texto destacado como código/negrito/etc.
    """
    if not isinstance(text, str):
        return str(text)

    # remove backticks
    text = text.replace("`", "")

    # remove **negrito** e *itálico*
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # remove bullets no começo da linha (- algo, * algo)
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s*[-*]\s+", "", line)
        lines.append(line)
    text = "\n".join(lines)

    # espaços duplicados
    text = re.sub(r"[ ]{2,}", " ", text)

    return text.strip()


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

    # render histórico
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
                "Por favor, digite apenas o número, por exemplo: 5000 ou 5.000,50."
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
        reply = sanitize_ai_reply(result["reply"])
        menu_text = build_menu_text()

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.text(reply)

        st.session_state.messages.append({"role": "assistant", "content": menu_text})
        with st.chat_message("assistant"):
            st.markdown(menu_text)

        st.session_state.awaiting_increase_value = False
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # ---------------- FLUXO DE ENTREVISTA DE CRÉDITO ----------------
    if st.session_state.authenticated and st.session_state.interview_stage is not None:
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        stage = st.session_state.interview_stage
        data = st.session_state.interview_data

        # 1) Renda mensal
        if stage == "ask_renda":
            renda = parse_brl_amount(original_input)
            if renda is None:
                msg = (
                    "Não consegui entender sua renda. "
                    "Digite apenas o valor, por exemplo: 5000 ou 5.000,00."
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg}
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.rerun()
                return

            data["renda_mensal"] = renda
            st.session_state.interview_stage = "ask_despesas"

            ask = (
                "Obrigado! Agora me informe o total aproximado das suas despesas mensais "
                "(contas fixas, aluguel, etc). Digite apenas o valor, por exemplo: "
                "2500 ou 2.500,00."
            )
            st.session_state.messages.append({"role": "assistant", "content": ask})
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        # 2) Despesas mensais
        if stage == "ask_despesas":
            despesas = parse_brl_amount(original_input)
            if despesas is None:
                msg = (
                    "Não consegui entender suas despesas. "
                    "Digite apenas o valor, por exemplo: 2500 ou 2.500,00."
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg}
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.rerun()
                return

            data["despesas_mensais"] = despesas
            st.session_state.interview_stage = "ask_emprego"

            ask = (
                "Certo! Qual é o seu tipo de emprego? "
                "Responda com uma das opções: formal, autônomo ou desempregado."
            )
            st.session_state.messages.append({"role": "assistant", "content": ask})
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        # 3) Tipo de emprego
        if stage == "ask_emprego":
            emprego = original_input.strip().lower()
            if emprego not in {"formal", "autônomo", "autonomo", "desempregado"}:
                msg = (
                    "Não reconheci esse tipo de emprego. "
                    "Por favor, responda apenas: formal, autônomo ou desempregado."
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg}
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.rerun()
                return

            data["tipo_emprego"] = emprego
            st.session_state.interview_stage = "ask_dependentes"

            ask = "Quantos dependentes você possui? (Se não tiver, responda 0)."
            st.session_state.messages.append({"role": "assistant", "content": ask})
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        # 4) Número de dependentes
        if stage == "ask_dependentes":
            try:
                dependentes = int(original_input.strip())
                if dependentes < 0:
                    raise ValueError
            except ValueError:
                msg = "Por favor, informe apenas um número inteiro maior ou igual a 0."
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg}
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.rerun()
                return

            data["numero_dependentes"] = dependentes
            st.session_state.interview_stage = "ask_dividas"

            ask = (
                "Você possui dívidas ativas (em outros bancos ou cartões)? "
                "Responda apenas sim ou não."
            )
            st.session_state.messages.append({"role": "assistant", "content": ask})
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        # 5) Dívidas ativas
        if stage == "ask_dividas":
            answer = original_input.strip().lower()
            if answer in {"sim", "s"}:
                tem_dividas = True
            elif answer in {"não", "nao", "n"}:
                tem_dividas = False
            else:
                msg = "Por favor, responda apenas sim ou não."
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg}
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.rerun()
                return

            data["tem_dividas"] = tem_dividas

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
                st.session_state.interview_stage = None
                st.session_state.interview_data = {}
                st.rerun()
                return

            result = run_credit_interview_from_api(
                cpf=st.session_state.cpf,
                renda_mensal=data["renda_mensal"],
                despesas_mensais=data["despesas_mensais"],
                tipo_emprego=data["tipo_emprego"],
                numero_dependentes=data["numero_dependentes"],
                tem_dividas=data["tem_dividas"],
            )
            reply = sanitize_ai_reply(result["reply"])
            menu_text = build_menu_text()

            # 1) resposta da IA - TEXTO PURO
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
            with st.chat_message("assistant"):
                st.text(reply)

            # 2) menu - MARKDOWN
            st.session_state.messages.append(
                {"role": "assistant", "content": menu_text}
            )
            with st.chat_message("assistant"):
                st.markdown(menu_text)

            st.session_state.interview_stage = None
            st.session_state.interview_data = {}
            st.session_state.current_agent = "credit"
            st.rerun()
            return

    # ---------------- FLUXO DE COTAÇÃO DE MOEDA ----------------
    if st.session_state.authenticated and st.session_state.awaiting_fx_params:
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        # Espera algo como: "USD BRL 100" ou "eur brl 2500"
        parts = original_input.split()
        if len(parts) != 3:
            msg = (
                "Não consegui entender. Informe no formato: USD BRL 100 "
                "(moeda de origem, moeda de destino e valor)."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": msg}
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.rerun()
            return

        base, target, amount_str = parts[0].upper(), parts[1].upper(), parts[2]
        amount = parse_brl_amount(amount_str)
        if amount is None:
            msg = (
                "Não consegui entender o valor. "
                "Use algo como: USD BRL 100 ou USD BRL 1500,00."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": msg}
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.rerun()
            return

        result = get_fx_quote_from_api(base, target, amount)
        reply = sanitize_ai_reply(result["reply"])
        menu_text = build_menu_text()

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.text(reply)

        st.session_state.messages.append({"role": "assistant", "content": menu_text})
        with st.chat_message("assistant"):
            st.markdown(menu_text)


        st.session_state.awaiting_fx_params = False
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
        credit_reply = sanitize_ai_reply(result["reply"])
        menu_text = build_menu_text()

        st.session_state.messages.append(
            {"role": "assistant", "content": credit_reply}
        )
        with st.chat_message("assistant"):
            st.text(credit_reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": menu_text}
        )
        with st.chat_message("assistant"):
            st.markdown(menu_text)

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
            "Por favor, me informe o novo valor de limite que você deseja, "
            "por exemplo: 5000 ou 7.500,00."
        )
        st.session_state.messages.append({"role": "assistant", "content": ask_value})
        with st.chat_message("assistant"):
            st.markdown(ask_value)

        st.session_state.awaiting_increase_value = True
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # 3 → entrevista de crédito
    if st.session_state.authenticated and original_input == "3":
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        st.session_state.interview_stage = "ask_renda"
        st.session_state.interview_data = {}

        msg = (
            "Vamos iniciar sua entrevista de crédito. 📝\n\n"
            "Para começar, me informe sua renda mensal aproximada, "
            "por exemplo: 5000 ou 5.000,00."
        )
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant"):
            st.markdown(msg)

        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # 4 → cotação de moeda
    if st.session_state.authenticated and original_input == "4":
        st.session_state.messages.append({"role": "user", "content": original_input})
        with st.chat_message("user"):
            st.markdown(original_input)

        msg = (
            "Vamos consultar a cotação. 💱\n\n"
            "Informe a moeda de origem, a moeda de destino e o valor, "
            "no formato: USD BRL 100 ou EUR BRL 2500."
        )
        st.session_state.messages.append({"role": "assistant", "content": msg})
        with st.chat_message("assistant"):
            st.markdown(msg)

        st.session_state.awaiting_fx_params = True
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    # ---------------- FLUXO NORMAL (SCREENING) ----------------

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    result = send_message_to_screening(user_input)
    reply = sanitize_ai_reply(result["reply"])

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


if __name__ == "__main__":
    main()
