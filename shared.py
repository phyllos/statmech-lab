"""Shared presentation components. All scientific calculations live in physics.py."""

from contextlib import contextmanager
from html import escape
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from i18n import language, tr

COLORS = {
    "theory": "#087E8B",
    "sample": "#E89B3F",
    "accent": "#7868B0",
    "beyond_fences": "#7868B0",  # Sample classification, never interval selection.
    "muted": "#718493",
    "ink": "#182B3A",
}

# Resolve relative to this module so launch working directories do not affect assets.
STYLE = (
    "<style>\n"
    + (Path(__file__).parent / "styles" / "app.css").read_text(encoding="utf-8")
    + "</style>"
)


def _advance_draw(key, initial):
    st.session_state[key] = st.session_state.get(key, initial) + 1


@contextmanager
def control_panel(lab, *, seed_key, seed_start, action_key, rearrange=False):
    """Keep actions above one persistent set of parameter widgets.

    Pages append their display/comparison popovers to the returned toolbar.
    The parameter toggle changes visibility only, never the data or seed.
    CSS assigns stable action slots based on the panel's actual available width.
    """
    open_key = f"panel_open_{lab}"
    if open_key not in st.session_state:
        st.session_state[open_key] = True
    with st.container(border=True, key=f"controls_{lab}"):
        tools = st.container(
            horizontal=True,
            wrap=True,
            vertical_alignment="center",
            gap="small",
            key=f"control_toolbar_{lab}",
        )
        with tools:
            with st.container(width="content", key=f"panel_toggle_{lab}"):
                opened = st.toggle(tr("Parameters", "参数"), key=open_key, persist_state="session")
            st.button(
                tr("Rearrange", "重新排列") if rearrange else tr("Resample", "重新抽样"),
                icon=":material/refresh:",
                key=action_key,
                on_click=_advance_draw,
                args=(seed_key, seed_start),
            )
        state = "open" if opened else "closed"
        with st.container(key=f"control_body_{lab}_{state}"):
            yield tools


def header(index, title, subtitle):
    chapter = str(index).zfill(2)
    section = (
        tr(f"EXPERIMENT {chapter}", f"实验 {chapter}")
        if chapter.isdigit()
        else tr("REFERENCE", "参考")
    )
    st.markdown(
        f'<div class="lab-header"><div class="lab-eyebrow">PHYS 515 &nbsp; / &nbsp; {escape(section)}</div>'
        f'<h1>{escape(title)}</h1><div class="lab-subtitle">{escape(subtitle)}</div>'
        '<div class="lab-rule"></div></div>',
        unsafe_allow_html=True,
    )


def insight(title, body):
    st.markdown(
        f'<div class="insight"><div class="insight-title">{escape(str(title))}</div>'
        f'<div class="insight-body">{escape(str(body))}</div></div>',
        unsafe_allow_html=True,
    )


def metric_row(items):
    """Inline readings with descriptions available by mouse, keyboard or touch."""
    from hashlib import sha1

    cards = []
    for label, value, detail in items:
        label, value, detail = map(str, (label, value, detail))
        tooltip_id = "metric-" + sha1(f"{label}|{detail}".encode()).hexdigest()[:12]
        cards.append(
            '<div class="metric"><div class="metric-reading">'
            f'<span class="metric-label">{escape(label)}</span>'
            f'<span class="metric-equals">=</span><strong class="metric-value">{escape(value)}</strong></div>'
            f'<button type="button" class="metric-help" aria-label="{escape(tr("About ", "说明：") + label)}" '
            f'aria-describedby="{tooltip_id}"><span aria-hidden="true">ⓘ</span></button>'
            f'<div class="metric-detail" id="{tooltip_id}" role="tooltip">{escape(detail)}</div></div>'
        )
    st.markdown('<div class="metrics">' + "".join(cards) + "</div>", unsafe_allow_html=True)


CHART_CONFIG = {
    "displaylogo": False,
    "scrollZoom": False,
    "displayModeBar": "hover",
    "modeBarButtons": [["zoom2d", "pan2d", "resetScale2d", "toImage"]],
}


def chart_config():
    return {
        **CHART_CONFIG,
        "locale": "zh-cn" if language() == "zh" else "en",
        "locales": {
            "zh-cn": {
                "dictionary": {
                    "Zoom": "缩放",
                    "Pan": "平移",
                    "Reset axes": "重置坐标轴",
                    "Download plot as a png": "下载 PNG 图形",
                    "Download plot as a svg": "下载 SVG 图形",
                    "Double-click to reset": "双击复原",
                },
                "format": {"decimal": ".", "thousands": ","},
            }
        },
    }


def style_figure(fig, *, native_title=True):
    """Reserve separate space for controls, axes and the wrapping bottom legend.

    Inline charts use an HTML heading in document flow. Standalone exports keep
    their native title. Neither presentation changes the data or axis limits.
    """
    axes_hidden = fig.layout.xaxis.visible is False and fig.layout.yaxis.visible is False
    show_legend = fig.layout.showlegend is not False and any(
        trace.showlegend is not False and trace.name for trace in fig.data
    )
    existing = fig.layout.margin.to_plotly_json()
    margins = {
        "l": existing.get("l", 20),
        "r": existing.get("r", 20),
        "t": 64 if native_title and fig.layout.title.text else 30,
        "b": (54 if axes_hidden else 100) if show_legend else 54,
    }
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, PingFang SC, sans-serif", size=12, color=COLORS["ink"]),
        margin=margins,
        colorway=[COLORS[k] for k in ("theory", "sample", "accent", "muted")],
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            xref="container",
            yref="container",
            x=0.025,
            y=0.01,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=11),
            itemsizing="constant",
            tracegroupgap=4,
        ),
        title=dict(x=0.025, xanchor="left", font=dict(size=15)),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_layout(height=max(fig.layout.height or 360, 200 if axes_hidden else 320))
    # Hover formatting changes readouts only; plotted arrays retain full precision.
    for axis in fig.select_xaxes():
        if not axis.hoverformat:
            axis.hoverformat = ".3g"
    for axis in fig.select_yaxes():
        if not axis.hoverformat:
            axis.hoverformat = ".3g"
    fig.update_xaxes(
        showgrid=False, zeroline=False, linecolor="#DFE7ED", automargin=True, title_standoff=12
    )
    fig.update_yaxes(gridcolor="#EFF3F6", zeroline=False, automargin=True, title_standoff=10)
    return fig


def chart(fig, key=None, *, title=None, subtitle=None):
    if title:
        fig.update_layout(title_text=title)
    heading = fig.layout.title.text
    display = go.Figure(fig)
    display.update_layout(title_text=None)
    style_figure(display, native_title=False)
    with st.container(border=True, key=f"figure_{key}" if key else None):
        if heading:
            description = (
                f'<div class="figure-subtitle">{escape(subtitle)}</div>' if subtitle else ""
            )
            st.markdown(
                f'<div class="figure-heading"><div class="figure-title">{escape(heading)}</div>{description}</div>',
                unsafe_allow_html=True,
            )
        st.plotly_chart(
            display,
            width="stretch",
            key=key,
            theme=None,
            config={
                **chart_config(),
                "toImageButtonOptions": {"format": "svg", "filename": key or "stat_mech_figure"},
            },
        )


def download_figure(fig, stem):
    # Deferred callbacks run outside the script thread: capture language/config
    # now, and retain an independent figure for the displayed experiment.
    snapshot = go.Figure(fig)
    config = chart_config()

    def make_html():
        return style_figure(go.Figure(snapshot)).to_html(include_plotlyjs=True, config=config)

    st.download_button(
        tr("Download interactive chart · HTML", "下载交互图 HTML"),
        data=make_html,
        file_name=f"{stem}.html",
        mime="text/html",
        key=f"download_{stem}",
        on_click="ignore",
    )
