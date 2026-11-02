"""Exact energy-sharing probabilities and entropy at a selected energy split."""

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from experiments import EXPERIMENT_BY_ID
from i18n import tr
from physics import thermal_contact
from plot_theme import COLORS
from shared import chart, control_panel, download_figure, header, metric_row
from state import initialize_controls


def _controls():
    initialize_controls(thermal_n_a=20, thermal_n_b=60, thermal_q_total=20, thermal_q_a=5)
    with control_panel("thermal"):
        a, b = st.columns(2)
        with a:
            n_a = st.slider(tr("Units in A · N_A", "A 的单元数 N_A"), 4, 120, key="thermal_n_a")
        with b:
            n_b = st.slider(tr("Units in B · N_B", "B 的单元数 N_B"), 4, 120, key="thermal_n_b")
        st.session_state.thermal_q_total = min(st.session_state.thermal_q_total, n_a + n_b)
        total, selected = st.columns(2)
        with total:
            q_total = st.slider(
                tr("Total excitation q", "总激发数 q"),
                0,
                n_a + n_b,
                key="thermal_q_total",
                help=tr(
                    "Total energy E = qε stays fixed while A and B exchange energy.",
                    "A 与 B 交换能量时，总能量 E = qε 保持不变。",
                ),
            )
        lo, hi = max(0, q_total - n_b), min(n_a, q_total)
        st.session_state.thermal_q_a = min(hi, max(lo, st.session_state.thermal_q_a))
        with selected:
            if lo == hi:
                st.caption(
                    tr(
                        f"Only allowed split: q_A = {lo}, q_B = {q_total - lo}",
                        f"唯一允许的分配：q_A = {lo}，q_B = {q_total - lo}",
                    )
                )
            else:
                st.slider(
                    tr("Inspect a split · q_A", "查看一种分配 q_A"),
                    lo,
                    hi,
                    key="thermal_q_a",
                    help=tr(
                        "Highlights the same split on both plots; it does not change the equilibrium distribution.",
                        "在两张图上高亮同一种分配；不会改变平衡概率分布。",
                    ),
                )
    return n_a, n_b, q_total, st.session_state.thermal_q_a


def _figures(data, q_selected):
    q_a, q_b = data["q_a"], data["q_b"]
    index = int(q_selected - q_a[0])
    single_split = len(q_a) == 1
    probability = go.Figure(
        go.Bar(
            x=q_a,
            y=data["probabilities"],
            customdata=q_b,
            marker_color=COLORS["theory"],
            opacity=0.55,
            width=0.35 if single_split else None,
            name=tr("Equilibrium probability", "平衡概率"),
            showlegend=False,
            hovertemplate="q_A = %{x}<br>q_B = %{customdata}<br>P = %{y:.3g}<extra></extra>",
        )
    )
    probability.add_trace(
        go.Scatter(
            x=[q_selected],
            y=[data["probabilities"][index]],
            mode="markers",
            name=tr("Selected split", "选中分配"),
            marker=dict(size=10, color=COLORS["theory"], line=dict(color="white", width=2)),
            hovertemplate="q_A = %{x}<br>P = %{y:.3g}<extra></extra>",
        )
    )
    entropy = go.Figure()
    for values, label, color, dash in (
        (data["log_omega_a"], "A", COLORS["secondary"], "dash"),
        (data["log_omega_b"], "B", COLORS["muted"], "dot"),
        (data["split_entropy"], "A + B", COLORS["theory"], "solid"),
    ):
        entropy.add_trace(
            go.Scatter(
                x=q_a,
                y=values,
                mode="lines+markers",
                name=label,
                line=dict(color=color, dash=dash, width=2.5 if label == "A + B" else 1.5),
                marker=dict(size=3),
                customdata=q_b,
                hovertemplate=f"{label}<br>q_A = %{{x}}<br>q_B = %{{customdata}}<br>S/k_B = %{{y:.3g}}<extra></extra>",
            )
        )
    entropy.add_trace(
        go.Scatter(
            x=[q_selected],
            y=[data["split_entropy"][index]],
            mode="markers",
            name=tr("Selected split", "选中分配"),
            marker=dict(size=10, color=COLORS["theory"], line=dict(color="white", width=2)),
            hovertemplate="q_A = %{x}<br>(S_A + S_B)/k_B = %{y:.3g}<extra></extra>",
        )
    )
    for fig in (probability, entropy):
        fig.update_layout(
            height=340,
            margin=dict(l=45, r=15),
            xaxis=dict(
                title=tr("Excitations in A · q_A", "A 的激发数 q_A"),
                range=[float(q_a[0]) - 0.6, float(q_a[-1]) + 0.6],
            ),
        )
        if len(q_a) <= 16:
            fig.update_xaxes(dtick=1)
    probability.update_yaxes(
        title=tr("Probability P(q_A)", "概率 P(q_A)"),
        range=[0, float(np.max(data["probabilities"])) * 1.15],
    )
    entropy_top = max(1.0, float(np.max(data["split_entropy"])) * 1.15)
    # Leave space below zero so ground/full-excitation markers remain visible.
    entropy.update_yaxes(
        title=tr("Entropy S / k_B", "熵 S / k_B"),
        range=[-0.06 * entropy_top, entropy_top],
    )
    if single_split:
        entropy.update_yaxes(tickvals=[0])
        entropy.add_annotation(
            x=0.5,
            y=0.55,
            xref="paper",
            yref="paper",
            text=tr("One microstate", "唯一微观态") + "<br>S_A = S_B = 0",
            showarrow=False,
            font=dict(size=12, color=COLORS["secondary"]),
        )
    return probability, entropy


def _count(value):
    return f"{value:,}" if value < 1_000_000 else f"{value:.3g}"


def render():
    header(
        EXPERIMENT_BY_ID["thermal"].number,
        tr("Thermal contact & energy sharing", "热接触与能量分配"),
        tr(
            "Two systems exchange energy. Which split has the most microscopic arrangements?",
            "两个系统交换能量时，哪种能量分配对应最多的微观排列？",
        ),
    )
    st.caption(
        tr(
            "Same two levels, 0 and ε · weak thermal contact · fixed total energy E = qε.",
            "相同的两个能级 0 与 ε · 弱热接触 · 总能量固定为 E = qε。",
        )
    )
    n_a, n_b, q_total, selected = _controls()
    data = thermal_contact(n_a, n_b, q_total)
    index = int(selected - data["q_a"][0])
    q_b = q_total - selected
    metric_row(
        [
            (
                f"Ω_A(q_A = {selected})",
                _count(math.comb(n_a, selected)),
                tr("Microstates of A at the selected energy", "A 在选中能量下的微观态数"),
            ),
            (
                f"Ω_B(q_B = {q_b})",
                _count(math.comb(n_b, q_b)),
                tr("Microstates of B at the remaining energy", "B 在剩余能量下的微观态数"),
            ),
            (
                tr("Selected probability", "选中分配的概率"),
                f"{data['probabilities'][index]:.3g}",
                tr(
                    "Ω_A Ω_B divided by all compatible combined microstates",
                    "Ω_A Ω_B 除以全部可达的组合微观态数",
                ),
            ),
        ]
    )
    probability, entropy = _figures(data, selected)
    parameters = f"N_A = {n_a} · N_B = {n_b} · q = {q_total}"
    left, right = st.columns(2)
    with left:
        chart(
            probability,
            "thermal_probability",
            title=tr("01 / Which split is likely?", "01 / 哪种分配更常见？"),
            subtitle=tr("Exact probabilities", "精确概率") + "\n" + parameters,
        )
    with right:
        chart(
            entropy,
            "thermal_entropy",
            title=tr("02 / Count, then take the log", "02 / 从计数到熵"),
            subtitle=tr("Fixed-split entropy · S_A + S_B", "固定分配的熵 · S_A + S_B")
            + "\n"
            + parameters,
        )
    modes = ", ".join(str(q) for q in data["modes"])
    if len(data["q_a"]) == 1:
        st.write(
            tr(
                "Only one split is accessible, so there are no energy-sharing fluctuations here.",
                "此时只有一种允许的分配，因此没有能量分配的涨落。",
            )
        )
    else:
        st.write(
            tr(
                f"Most probable q_A: {modes}. Mean q_A = {data['mean']:.3g}; SD = {np.sqrt(data['variance']):.3g}. "
                "The probability peaks maximize S_A + S_B over allowed splits; other allowed splits remain possible.",
                f"最可能的 q_A：{modes}。平均 q_A = {data['mean']:.3g}，标准差为 {np.sqrt(data['variance']):.3g}。"
                "概率峰值对应固定分配下 S_A + S_B 的最大值；其他允许的分配仍可能出现。",
            )
        )
    download_figure(
        probability,
        "thermal_probability",
        label=tr("Download energy-sharing probabilities · HTML", "下载能量分配概率图 · HTML"),
    )
    with st.expander(tr("Model, counting & equilibrium", "模型、计数与平衡")):
        st.write(
            tr(
                "Each system contains distinguishable, noninteracting two-level units. Weak coupling permits energy exchange "
                "while its interaction energy is neglected. All combined microstates at fixed q are assigned equal weight. "
                "The plots show equilibrium statistics, not the trajectory or rate of equilibration; lines connect discrete values.",
                "两个系统各由可区分、内部无相互作用的二能级单元组成。弱耦合允许能量交换，其相互作用能忽略不计。"
                "总激发数 q 固定时，全部可达组合微观态等权重。图中展示平衡统计，不表示弛豫轨迹或速率；连线连接的是离散取值。",
            )
        )
        st.latex(r"q_B=q-q_A,\qquad \max(0,q-N_B)\le q_A\le\min(N_A,q)")
        st.latex(
            r"P(q_A)=\frac{\Omega_A(q_A)\Omega_B(q-q_A)}{\binom{N_A+N_B}{q}},\qquad \Omega_i(q_i)=\binom{N_i}{q_i}"
        )
        st.latex(
            r"\frac{S_{\mathrm{split}}}{k_B}=\ln\Omega_A+\ln\Omega_B,\qquad \ln P(q_A)=\frac{S_{\mathrm{split}}}{k_B}-\ln\binom{N_A+N_B}{q}"
        )
        st.caption(
            tr(
                "S_split fixes both subsystem energies. The entropy of the entire isolated system, with only total energy fixed, "
                "is k_B ln C(N_A + N_B, q) and stays constant across these splits.",
                "S_split 同时约束两个子系统的能量。若仅固定总能量，整个孤立系统的熵为 k_B ln C(N_A + N_B, q)，不会随选中分配改变。",
            )
        )
        st.latex(r"\langle q_A\rangle=\frac{N_A}{N_A+N_B}q")
        st.write(
            tr(
                "On average, energy is shared in proportion to system size. Equal amounts occur for equal-sized systems; "
                "the most probable integer split need not equal the mean, and two neighboring splits can tie.",
                "平均能量按系统大小分配；系统大小相同时，平均分配的能量才相等。最可能的整数分配不一定等于均值，也可能有相邻两个并列峰值。",
            )
        )
        st.latex(
            r"\frac{\partial(S_A+S_B)}{\partial E_A}=k_B(\beta_A-\beta_B)=0\quad\Rightarrow\quad\beta_A=\beta_B"
        )
        st.caption(
            tr(
                "The temperature argument uses a smooth, large-system approximation at an interior maximum. "
                "The finite-system probabilities above use exact counting and do not require derivatives or a temperature convention.",
                "温度条件适用于大系统、熵可平滑近似且极大值位于内部的情形。上面的有限系统概率来自精确计数，不依赖求导或温度定义约定。",
            )
        )
