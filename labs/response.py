"""Connect canonical level populations to energy and thermal response."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from i18n import tr
from physics import two_level_response
from plot_theme import COLORS
from shared import chart, control_panel, download_figure, header
from state import initialize_controls

TEMPERATURE_MAX = 4.0


def _controls():
    initialize_controls(response_theta=0.4)
    with control_panel("response"):
        theta = st.slider(
            tr("Temperature · k_B T / ε", "温度 k_B T / ε"),
            0.0,
            TEMPERATURE_MAX,
            step=0.01,
            key="response_theta",
            help=tr(
                "Positive temperatures; 0 shows the T → 0⁺ limit. The energy gap ε is fixed.",
                "展示正温度；0 表示 T → 0⁺ 的极限。能隙 ε 保持不变。",
            ),
        )
    return theta


def _population_figure(data):
    labels = [tr("Ground · 0", "基态 · 0"), tr("Excited · ε", "激发态 · ε")]
    probabilities = [float(data["ground"]), float(data["excited"])]
    figure = go.Figure(
        go.Bar(
            x=labels,
            y=probabilities,
            marker_color=[COLORS["secondary"], COLORS["theory"]],
            width=0.5,
            text=[f"{p:.3g}" for p in probabilities],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>P = %{y:.3g}<extra></extra>",
        )
    )
    figure.update_layout(height=400, showlegend=False, margin=dict(l=45, r=20))
    figure.update_yaxes(title=tr("Probability", "概率"), range=[0, 1.15], dtick=0.25)
    return figure


def _response_figure(theta, data):
    temperatures = np.linspace(0, TEMPERATURE_MAX, 401)
    curve = two_level_response(temperatures)
    figure = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.23)
    for row, key, symbol, limit in (
        (1, "energy", "U / (Nε)", 0.55),
        (2, "heat_capacity", "C / (Nk_B)", 0.5),
    ):
        figure.add_trace(
            go.Scatter(
                x=temperatures,
                y=curve[key],
                mode="lines",
                line=dict(color=COLORS["theory"], width=2.5),
                hovertemplate=f"k_B T / ε = %{{x:.3g}}<br>{symbol} = %{{y:.3g}}<extra></extra>",
            ),
            row=row,
            col=1,
        )
        figure.add_trace(
            go.Scatter(
                x=[theta],
                y=[float(data[key])],
                mode="markers",
                marker=dict(color=COLORS["theory"], size=10, line=dict(color="white", width=1.5)),
                cliponaxis=False,
                hovertemplate=f"k_B T / ε = %{{x:.3g}}<br>{symbol} = %{{y:.3g}}<extra></extra>",
            ),
            row=row,
            col=1,
        )
        figure.add_vline(
            x=theta, line_color=COLORS["muted"], line_width=1, line_dash="dot", row=row, col=1
        )
        figure.update_yaxes(title=symbol, range=[0, limit], nticks=4, row=row, col=1)
        figure.add_annotation(
            x=1,
            y=1.02,
            xref="x domain" if row == 1 else "x2 domain",
            yref="y domain" if row == 1 else "y2 domain",
            text=f"{symbol} = {float(data[key]):.3g}",
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            font=dict(size=11),
        )
    figure.update_xaxes(range=[0, TEMPERATURE_MAX], dtick=1)
    figure.update_xaxes(title=tr("Temperature · k_B T / ε", "温度 k_B T / ε"), row=2, col=1)
    figure.update_layout(height=400, showlegend=False, margin=dict(l=55, r=20))
    return figure


def render():
    header(
        8,
        tr("Temperature, energy & heat capacity", "温度、能量与热容量"),
        tr(
            "Energy rises with temperature. Why does heat capacity rise, then fall?",
            "温度升高，平均能量不断增加，为什么热容量却先增大、再减小？",
        ),
    )
    theta = _controls()
    data = two_level_response(theta)
    st.caption(
        tr(
            "Canonical equilibrium · independent 0/ε units · fixed gap ε · results per unit.",
            "正则平衡 · 相互独立的 0/ε 二能级单元 · 固定能隙 ε · 结果按单元归一化。",
        )
    )
    context = "T → 0⁺" if theta == 0 else f"k_B T / ε = {theta:.3g}"
    population = _population_figure(data)
    response = _response_figure(theta, data)
    left, right = st.columns(2)
    with left:
        chart(
            population,
            "response_populations",
            title=tr("01 / Level populations", "01 / 能级占据"),
            subtitle=context,
        )
        download_figure(
            population,
            "level_populations",
            label=tr("Download populations · HTML", "下载能级占据图 · HTML"),
        )
    with right:
        chart(
            response,
            "response_curves",
            title=tr("02 / Thermal response", "02 / 温度响应"),
            subtitle=context,
        )
        download_figure(
            response,
            "thermal_response",
            label=tr("Download response · HTML", "下载温度响应图 · HTML"),
        )
    if theta == 0:
        observation = tr(
            "At T → 0⁺, all units occupy the ground state: U → 0 and C → 0.",
            "T → 0⁺ 时，所有单元都处于基态：U → 0，C → 0。",
        )
    elif theta < 0.2:
        observation = tr(
            "Excitations are rare at low temperature; the mean energy responds only weakly to heating.",
            "低温下激发很少，升温引起的平均能量变化也很小。",
        )
    elif theta < 0.8:
        observation = tr(
            "The energy curve is steepest near k_B T / ε ≈ 0.417, where heat capacity peaks. This smooth peak is not a phase transition.",
            "能量曲线在 k_B T / ε ≈ 0.417 附近最陡，热容量在此达到峰值。这个平滑峰值不是相变。",
        )
    else:
        observation = tr(
            "The two levels approach equal population. Energy continues to rise toward Nε/2, but its slope—and heat capacity—decreases.",
            "两个能级的占据逐渐趋于相等。平均能量继续接近 Nε/2，但曲线斜率与热容量都在减小。",
        )
    st.write(observation)
    with st.expander(tr("From the partition function to response", "从配分函数到温度响应")):
        st.write(
            tr(
                "Each distinguishable unit has two nondegenerate levels, 0 and ε. The temperature is set by an ideal reservoir. N and ε remain fixed; these canonical results are exact for independent units at any N.",
                "每个可区分单元具有 0 和 ε 两个非简并能级，温度由理想热库设定。N 与 ε 保持不变；这些正则结果对任意 N 个相互独立单元都是精确的。",
            )
        )
        st.latex(
            r"\begin{aligned}\theta&=\frac{k_BT}{\epsilon},\quad \beta=\frac{1}{k_BT}\\"
            r"z&=1+e^{-1/\theta},\quad Z=z^N\\"
            r"p_1&=\frac{e^{-1/\theta}}{1+e^{-1/\theta}},\quad p_0=1-p_1\end{aligned}"
        )
        st.latex(
            r"\begin{aligned}U&=-\frac{\partial\ln Z}{\partial\beta}=N\epsilon p_1\\"
            r"\frac{C}{Nk_B}&=\frac{d[U/(N\epsilon)]}{d\theta}=\frac{p_1(1-p_1)}{\theta^2}\end{aligned}"
        )
        st.write(
            tr(
                "Heat capacity is the slope of mean energy versus temperature, not the amount of energy already stored. The upper and lower curves use separate vertical scales and the same temperature axis.",
                "热容量是平均能量对温度的斜率，不是已经储存的能量。上下两条曲线使用各自的纵轴，共用温度横轴。",
            )
        )
        st.latex(
            r"\begin{aligned}\operatorname{Var}(E)&=\frac{\partial^2\ln Z}{\partial\beta^2}\\"
            r"&=N\epsilon^2p_1(1-p_1)\\"
            r"C&=\frac{\operatorname{Var}(E)}{k_BT^2}\quad(T>0)\end{aligned}"
        )
        st.write(
            tr(
                "These are equilibrium energy fluctuations, not uncertainty in a sampled mean. At high temperature, Var(E)/(Nε²) → 1/4 while C/(Nk_B) → 0: the factor 1/T² matters. The total energy is bounded by Nε, but positive-temperature equilibrium approaches mean energy Nε/2.",
                "这里是平衡能量涨落，不是抽样均值的不确定性。高温时 Var(E)/(Nε²) → 1/4，而 C/(Nk_B) → 0：其中的 1/T² 因子不可忽略。总能量上界为 Nε，但正温度平衡的平均能量趋于 Nε/2。",
            )
        )
        st.caption(
            tr(
                "The 0 setting is a limiting value, not substitution into 1/T. Negative-temperature population inversion is explored in experiment 04. Unlike experiment 07, this page assumes an ideal reservoir throughout.",
                "0 设置表示极限，不是把零代入 1/T。负温度的粒子数反转见实验 04；与实验 07 不同，本页始终采用理想热库。",
            )
        )
