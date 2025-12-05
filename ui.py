"""TODO"""
import streamlit as st

from frontend.service.screening_service import (
    send_message_to_screening,
    reset_screening_backend,
)
from frontend.service.credit_service import (
    get_credit_limit,
    request_credit_increase,
)
from frontend.service.interview_service import run_credit_interview
from frontend.service.forex_service import get_fx_quote

from frontend.state.session import init_session_state, maybe_store_cpf_from_input
from frontend.ui.formatting import parse_brl_amount, sanitize_ai_reply
from frontend.ui.menu import build_menu_text


def main() -> None:
    """TODO"""
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
        st.session_state.messages.append(
            {"role": "assistant", "content": welcome, "mode": "markdown"}
        )
        st.session_state.started = True

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            mode = msg.get("mode", "markdown")
            if mode == "text":
                st.text(msg["content"])
            else:
                st.markdown(msg["content"])

    st.divider()
    user_input = st.chat_input("Digite sua mensagem...")

    if not user_input:
        return

    original_input = user_input.strip()

    if not st.session_state.authenticated:
        maybe_store_cpf_from_input(original_input)

    if st.session_state.authenticated and st.session_state.awaiting_increase_value:
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        amount = parse_brl_amount(original_input)
        if amount is None:
            error_msg = (
                "Não consegui entender o valor informado. "
                "Por favor, digite apenas o número, por exemplo: 5000 ou 5.000,50."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg, "mode": "markdown"}
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
                {"role": "assistant", "content": error_msg, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.session_state.awaiting_increase_value = False
            st.rerun()
            return

        result = request_credit_increase(st.session_state.cpf, amount)
        reply = sanitize_ai_reply(result["reply"])
        menu_text = build_menu_text()

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "mode": "text"}
        )
        with st.chat_message("assistant"):
            st.text(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": menu_text, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(menu_text)

        st.session_state.awaiting_increase_value = False
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    if st.session_state.authenticated and st.session_state.interview_stage is not None:
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        stage = st.session_state.interview_stage
        data = st.session_state.interview_data

        if stage == "ask_renda":
            renda = parse_brl_amount(original_input)
            if renda is None:
                msg = (
                    "Não consegui entender sua renda. "
                    "Digite apenas o valor, por exemplo: 5000 ou 5.000,00."
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg, "mode": "markdown"}
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
            st.session_state.messages.append(
                {"role": "assistant", "content": ask, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        if stage == "ask_despesas":
            despesas = parse_brl_amount(original_input)
            if despesas is None:
                msg = (
                    "Não consegui entender suas despesas. "
                    "Digite apenas o valor, por exemplo: 2500 ou 2.500,00."
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg, "mode": "markdown"}
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
            st.session_state.messages.append(
                {"role": "assistant", "content": ask, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        if stage == "ask_emprego":
            emprego = original_input.strip().lower()
            if emprego not in {"formal", "autônomo", "autonomo", "desempregado"}:
                msg = (
                    "Não reconheci esse tipo de emprego. "
                    "Por favor, responda apenas: formal, autônomo ou desempregado."
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg, "mode": "markdown"}
                )
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.rerun()
                return

            data["tipo_emprego"] = emprego
            st.session_state.interview_stage = "ask_dependentes"

            ask = "Quantos dependentes você possui? (Se não tiver, responda 0)."
            st.session_state.messages.append(
                {"role": "assistant", "content": ask, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        if stage == "ask_dependentes":
            try:
                dependentes = int(original_input.strip())
                if dependentes < 0:
                    raise ValueError
            except ValueError:
                msg = "Por favor, informe apenas um número inteiro maior ou igual a 0."
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg, "mode": "markdown"}
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
            st.session_state.messages.append(
                {"role": "assistant", "content": ask, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(ask)
            st.rerun()
            return

        if stage == "ask_dividas":
            answer = original_input.strip().lower()
            if answer in {"sim", "s"}:
                tem_dividas = True
            elif answer in {"não", "nao", "n"}:
                tem_dividas = False
            else:
                msg = "Por favor, responda apenas sim ou não."
                st.session_state.messages.append(
                    {"role": "assistant", "content": msg, "mode": "markdown"}
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
                    {"role": "assistant", "content": error_msg, "mode": "markdown"}
                )
                with st.chat_message("assistant"):
                    st.markdown(error_msg)
                st.session_state.interview_stage = None
                st.session_state.interview_data = {}
                st.rerun()
                return

            result = run_credit_interview(
                cpf=st.session_state.cpf,
                renda_mensal=data["renda_mensal"],
                despesas_mensais=data["despesas_mensais"],
                tipo_emprego=data["tipo_emprego"],
                numero_dependentes=data["numero_dependentes"],
                tem_dividas=data["tem_dividas"],
            )
            reply = sanitize_ai_reply(result["reply"])
            menu_text = build_menu_text()

            st.session_state.messages.append(
                {"role": "assistant", "content": reply, "mode": "text"}
            )
            with st.chat_message("assistant"):
                st.text(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": menu_text, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(menu_text)

            st.session_state.interview_stage = None
            st.session_state.interview_data = {}
            st.session_state.current_agent = "credit"
            st.rerun()
            return

    if st.session_state.authenticated and st.session_state.awaiting_fx_params:
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        parts = original_input.split()
        if len(parts) != 3:
            msg = (
                "Não consegui entender. Informe no formato: USD BRL 100 "
                "(moeda de origem, moeda de destino e valor)."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": msg, "mode": "markdown"}
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
                {"role": "assistant", "content": msg, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.rerun()
            return

        result = get_fx_quote(base, target, amount)
        reply = sanitize_ai_reply(result["reply"])
        menu_text = build_menu_text()

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "mode": "text"}
        )
        with st.chat_message("assistant"):
            st.text(reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": menu_text, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(menu_text)

        st.session_state.awaiting_fx_params = False
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    if st.session_state.authenticated and original_input == "5":
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        goodbye = "Sessão encerrada. Vamos começar de novo? Informe seu CPF. 👋"
        st.session_state.messages.append(
            {"role": "assistant", "content": goodbye, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(goodbye)

        reset_screening_backend()
        st.session_state.clear()
        st.rerun()
        return

    if st.session_state.authenticated and original_input == "1":
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        if not st.session_state.cpf:
            error_msg = (
                "❌ Não consegui identificar seu CPF na sessão. "
                "Por favor, finalize a conversa e inicie novamente."
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": error_msg, "mode": "markdown"}
            )
            with st.chat_message("assistant"):
                st.markdown(error_msg)
            st.rerun()
            return

        result = get_credit_limit(st.session_state.cpf)
        credit_reply = sanitize_ai_reply(result["reply"])
        menu_text = build_menu_text()

        st.session_state.messages.append(
            {"role": "assistant", "content": credit_reply, "mode": "text"}
        )
        with st.chat_message("assistant"):
            st.text(credit_reply)

        st.session_state.messages.append(
            {"role": "assistant", "content": menu_text, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(menu_text)

        st.session_state.current_agent = "credit"
        st.rerun()
        return

    if st.session_state.authenticated and original_input == "2":
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        ask_value = (
            "Claro! Vamos solicitar um aumento de limite. 💳\n\n"
            "Por favor, me informe o novo valor de limite que você deseja, "
            "por exemplo: 5000 ou 7.500,00."
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": ask_value, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(ask_value)

        st.session_state.awaiting_increase_value = True
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    if st.session_state.authenticated and original_input == "3":
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        st.session_state.interview_stage = "ask_renda"
        st.session_state.interview_data = {}

        msg = (
            "Vamos iniciar sua entrevista de crédito. 📝\n\n"
            "Para começar, me informe sua renda mensal aproximada, "
            "por exemplo: 5000 ou 5.000,00."
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": msg, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(msg)

        st.session_state.current_agent = "credit"
        st.rerun()
        return

    if st.session_state.authenticated and original_input == "4":
        st.session_state.messages.append(
            {"role": "user", "content": original_input, "mode": "markdown"}
        )
        with st.chat_message("user"):
            st.markdown(original_input)

        msg = (
            "Vamos consultar a cotação. 💱\n\n"
            "Informe a moeda de origem, a moeda de destino e o valor, "
            "no formato: USD BRL 100 ou EUR BRL 2500."
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": msg, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(msg)

        st.session_state.awaiting_fx_params = True
        st.session_state.current_agent = "credit"
        st.rerun()
        return

    st.session_state.messages.append(
        {"role": "user", "content": user_input, "mode": "markdown"}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    result = send_message_to_screening(user_input)
    reply = sanitize_ai_reply(result["reply"])

    if not st.session_state.authenticated and (
        result.get("authenticated", False)
        or "autenticação realizada com sucesso" in reply.lower()
        or "você já está autenticado" in reply.lower()
    ):
        st.session_state.authenticated = True
        st.session_state.current_agent = "menu"

        menu_text = build_menu_text()
        full_message = f"{reply}\n\n{menu_text}"

        st.session_state.messages.append(
            {"role": "assistant", "content": full_message, "mode": "markdown"}
        )
        with st.chat_message("assistant"):
            st.markdown(full_message)

        st.rerun()
        return

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "mode": "text"}
    )
    with st.chat_message("assistant"):
        st.text(reply)

    st.rerun()


if __name__ == "__main__":
    main()
