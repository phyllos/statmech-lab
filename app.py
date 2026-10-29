"""Local bilingual PHYS 515 laboratory. Run: uv run streamlit run app.py."""

from html import escape

import streamlit as st

from i18n import LANGUAGES, language, tr
from shared import STYLE
from state import remember_controls, restore_controls

st.set_page_config(page_title="StatMech Lab · PHYS 515", page_icon="∿", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)

LABS = {
    "distributions": ("01  Distributions & boxplots", "01  分布与箱型图"),
    "tails": ("02  Shape & tails", "02  偏度、峰度与尾部"),
    "clt": ("03  LLN & CLT", "03  大数定律与 CLT"),
    "entropy": ("04  Microstates & entropy", "04  微观态与熵"),
    "joint": ("05  Joint & conditional probability", "05  联合与条件概率"),
    "glossary": ("Reference · Glossary", "参考 · 术语表"),
}

if "language" not in st.session_state:
    requested = st.query_params.get("lang", "en")
    st.session_state.language = requested if requested in LANGUAGES else "en"
if "active_lab" not in st.session_state:
    requested = st.query_params.get("lab", "distributions")
    st.session_state.active_lab = requested if requested in LABS else "distributions"
restore_controls()
lab_labels = {key: tr(*names) for key, names in LABS.items()}


def select_lab():
    selected = st.session_state.get(f"nav_{language()}")
    if selected in LABS:
        st.session_state.active_lab = selected
    sync_navigation()


def sync_navigation():
    remember_controls()
    st.session_state.language = language()
    st.query_params["lang"] = language()
    active = st.session_state.get("active_lab", "distributions")
    st.session_state.active_lab = active if active in LABS else "distributions"
    st.query_params["lab"] = st.session_state.active_lab


with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark" aria-hidden="true">'
        '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M3 17C6 17 5 8 10 8C16 8 14 24 20 24C26 24 25 15 29 15" '
        'stroke="currentColor" stroke-width="2.8" stroke-linecap="round"/></svg></div><div>'
        '<div class="brand-title">StatMech Lab</div>'
        '<div class="brand-sub">PROBABILITY → PHYSICS</div></div></div>'
        f'<div class="brand-course">{escape(tr("Statistical physics · Concept lab", "统计物理 · 概念实验室"))}</div>',
        unsafe_allow_html=True,
    )
    st.segmented_control(
        "Language / 语言",
        required=True,
        options=list(LANGUAGES),
        format_func=lambda value: "English" if value == "en" else "中文",
        key="language",
        on_change=sync_navigation,
        width="stretch",
    )
    # One widget instance per language: Streamlit transmits radio values as their
    # formatted labels, so a translated label must never outlive its language.
    # The canonical lab id lives in the non-widget key "active_lab".
    st.radio(
        tr("Explore", "实验目录"),
        options=list(LABS),
        index=list(LABS).index(st.session_state.active_lab),
        format_func=lab_labels.get,
        key=f"nav_{language()}",
        on_change=select_lab,
    )
    st.divider()
    st.markdown(tr("**Observe, then explain**", "**先观察，再解释**"))
    steps = tr(
        [
            "Change a parameter. Watch the plot.",
            "Resample. Explore random variation.",
            "Open the derivation. Connect ideas.",
        ],
        [
            "改变一个参数，看看图形怎样变化。",
            "重新抽样，区分规律与偶然。",
            "展开推导，连接现象与公式。",
        ],
    )
    st.markdown(
        '<div class="sidebar-note sidebar-guide">' + "<br>".join(map(escape, steps)) + "</div>",
        unsafe_allow_html=True,
    )
    with st.expander(tr("Charts & controls", "图表与操作")):
        st.markdown(
            tr(
                "Hover for values, drag to zoom, and double-click to reset. Use the toolbar to pan, reset or export SVG; click a legend entry to show or hide a curve.",
                "悬停查看数值，拖动缩放，双击复原。右上工具栏提供平移、复原与 SVG 导出；点击图例可显示或隐藏曲线。",
            )
        )
        st.markdown(
            tr(
                "The same settings reproduce the same samples. Resample changes the random seed; switching language preserves your experiment.",
                "相同参数可复现抽样结果。点击「重新抽样」更换随机种子；切换语言会保留当前实验。",
            )
        )
    st.markdown(
        '<div class="sidebar-note" style="margin-top:12px">'
        '<span class="legend-dot" style="background:#087e8b"></span>'
        + tr("Population / theory", "总体 / 理论")
        + " &nbsp; "
        '<span class="legend-dot" style="background:#e89b3f"></span>'
        + tr("Sample / observation", "样本 / 观测")
        + "<br>"
        "PHYS 515 · Interactive companion</div>",
        unsafe_allow_html=True,
    )

if st.session_state.active_lab == "distributions":
    from labs.distributions import render
elif st.session_state.active_lab == "tails":
    from labs.tails import render
elif st.session_state.active_lab == "clt":
    from labs.clt import render
elif st.session_state.active_lab == "entropy":
    from labs.entropy import render
elif st.session_state.active_lab == "joint":
    from labs.joint import render
else:
    from glossary import render

# Keep each control bar inside its experiment; shared reference material follows it.
with st.container(key=f"workspace_{st.session_state.active_lab}"):
    render()
if st.session_state.active_lab != "glossary":
    from glossary import render_related

    render_related(st.session_state.active_lab)
remember_controls()
st.markdown(
    '<div class="app-footer">STATMECH LAB &nbsp; / &nbsp; '
    + tr(
        "Probability · Fluctuations · Microstates &nbsp; / &nbsp; Every experiment starts with a question",
        "概率 · 涨落 · 微观态 &nbsp; / &nbsp; 每个实验都从一个问题开始",
    )
    + "</div>",
    unsafe_allow_html=True,
)
