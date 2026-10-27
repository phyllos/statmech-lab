"""Small, explicit bilingual UI helpers; model identifiers never depend on text."""

import streamlit as st

LANGUAGES = ("en", "zh")


def language():
    value = st.session_state.get("language", "en")
    return value if value in LANGUAGES else "en"


def tr(en, zh):
    """Select display text, including already formatted dynamic values."""
    return zh if language() == "zh" else en
