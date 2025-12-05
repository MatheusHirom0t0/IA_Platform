"""TODO"""
from typing import Optional
import streamlit as st


def init_session_state() -> None:
    """TODO"""
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


def maybe_store_cpf_from_input(user_input: str) -> None:
    """TODO"""
    digits = "".join(ch for ch in user_input if ch.isdigit())
    if len(digits) == 11:
        st.session_state.cpf = digits
