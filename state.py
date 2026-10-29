"""Session-local experiment persistence across navigation and language changes.

Stable keys identify controls; translated display text never enters model state.
Samples are regenerated from settings and seeds, not persisted to disk.
"""

import streamlit as st

CONTROL_PREFIXES = ("dist_", "tail_", "clt_", "ent_", "joint_")


def remember_controls():
    """Keep experiment settings when a language or reference-page rerun occurs."""
    saved = dict(st.session_state.get("_experiment_settings", {}))
    for key in st.session_state:
        if key.startswith(CONTROL_PREFIXES) and not key.endswith(("resample", "shuffle")):
            value = st.session_state[key]
            if isinstance(value, (str, int, float, bool, tuple, list)):
                saved[key] = value
    st.session_state["_experiment_settings"] = saved


def restore_controls():
    for key, value in st.session_state.get("_experiment_settings", {}).items():
        # Detach the latest value from widget cleanup before rendering. A hidden
        # widget can otherwise expose an older manually initialized value when
        # its widget ID is removed (e.g. a walkthrough step or glossary visit).
        st.session_state[key] = st.session_state.get(key, value)


def initialize_controls(**defaults):
    """Set defaults only for missing state; widgets read their values by key.

    Do not also pass value= to those widgets: restored state and a widget-level
    default would be two competing sources of initialization in Streamlit.
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
