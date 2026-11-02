"""From finite-reservoir counting to a mean-matched canonical distribution."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from experiments import EXPERIMENT_BY_ID
from i18n import tr
from physics import canonical_comparison
from plot_theme import COLORS
from shared import chart, control_panel, download_figure, header, metric_row
from state import initialize_controls

BATH_SIZES = (20, 40, 80, 160, 320, 640, 1280, 2560)


def _excitation_count(total_units, target_fraction):
    """Convert the UI's 1/20 fraction steps to q, rounding half up.

    Recover the integer slider step before multiplying by the system size;
    binary float error must not move an exact half-integer below its tie.
    """
    step = round(target_fraction * 20)
    return (step * total_units + 10) // 20


def _controls():
    initialize_controls(canon_n_a=20, canon_n_b=40, canon_fraction=0.25)
    with control_panel("canon"):
        a, b, fraction = st.columns(3)
        with a:
            n_a = st.slider(tr("System size · N_A", "系统大小 N_A"), 2, 40, step=2, key="canon_n_a")
        with b:
            n_b = st.select_slider(
                tr("Reservoir size · N_B", "热库大小 N_B"),
                options=BATH_SIZES,
                key="canon_n_b",
                help=tr(
                    "Keep A and the excited fraction fixed, then enlarge B.",
                    "保持 A 和激发比例不变，逐步增大 B。",
                ),
            )
        with fraction:
            target = st.slider(
                tr("Target excited fraction", "目标激发比例"),
                0.05,
                0.5,
                step=0.05,
                key="canon_fraction",
                help=tr(
                    "The combined system has q ≈ p(N_A + N_B) excitations, rounded to the nearest integer (halves round up). "
                    "The actual fraction sets both distributions. At p = 0.5, β = 0 (infinite temperature).",
                    "组合系统的总激发数 q ≈ p(N_A + N_B)，取最近整数，恰好半整数时向上取整。两种分布使用同一实际比例。"
                    "p = 0.5 时 β = 0，对应无限温极限。",
                ),
            )
    q = _excitation_count(n_a + n_b, target)
    return n_a, n_b, q


def _figure(data):
    figure = go.Figure()
    for values, label, color, dash, symbol in (
        (
            data["exact"],
            tr("Finite reservoir · exact", "有限热库 · 精确"),
            COLORS["theory"],
            "solid",
            "circle",
        ),
        (
            data["canonical"],
            tr("Canonical approximation", "正则近似"),
            COLORS["secondary"],
            "dash",
            "circle-open",
        ),
    ):
        figure.add_trace(
            go.Scatter(
                x=data["q_a"],
                y=values,
                name=label,
                mode="lines+markers",
                line=dict(color=color, width=2.5, dash=dash),
                marker=dict(size=6, symbol=symbol),
                hovertemplate="q_A = %{x}<br>P = %{y:.3g}<extra>%{fullData.name}</extra>",
            )
        )
    figure.update_layout(height=360, margin=dict(l=45, r=20), hovermode="x unified")
    figure.update_xaxes(
        title=tr("System excitations · q_A = E_A / ε", "系统激发数 q_A = E_A / ε"),
        range=[-0.5, float(data["q_a"][-1]) + 0.5],
        dtick=1 if len(data["q_a"]) <= 21 else 5,
    )
    figure.update_yaxes(
        title=tr("Probability P(q_A)", "概率 P(q_A)"),
        range=[0, 1.15 * max(float(np.max(data["exact"])), float(np.max(data["canonical"])))],
    )
    return figure


def render():
    header(
        EXPERIMENT_BY_ID["canonical"].number,
        tr("From a reservoir to the canonical ensemble", "从有限热库到正则系综"),
        tr(
            "How large must a reservoir be before the Boltzmann approximation works well?",
            "热库要多大，玻尔兹曼近似才好用？",
        ),
    )
    n_a, n_b, q = _controls()
    data = canonical_comparison(n_a, n_b, q)
    p = data["fraction"]
    st.caption(
        tr(
            f"Same two-level gap ε · fixed total energy qε · q = {q}, actual p = {p:.3g}.",
            f"相同二能级能隙 ε · 总能量固定为 qε · q = {q}，实际 p = {p:.3g}。",
        )
    )
    metric_row(
        [
            (
                "βε",
                f"{data['beta_eps']:.3g}",
                tr(
                    "Canonical temperature parameter ln((1−p)/p); β = 0 is infinite temperature, not zero temperature.",
                    "正则温度参数 ln((1−p)/p)；β = 0 对应无限温，而非零温。",
                ),
            ),
            (
                tr("Exact energy SD / ε", "精确能量标准差 / ε"),
                f"{np.sqrt(data['exact_variance']):.3g}",
                tr(
                    f"Canonical prediction: {np.sqrt(data['canonical_variance']):.3g}. These are equilibrium fluctuations, not sampling error.",
                    f"正则预测：{np.sqrt(data['canonical_variance']):.3g}。这是平衡涨落，不是抽样误差。",
                ),
            ),
            (
                tr("Distribution gap · TV", "分布差异 TV"),
                f"{data['total_variation']:.3g}",
                tr(
                    "Total variation = ½ Σ |P_exact − P_can| over all q_A. It ranges from 0 to 1; 0 means identical distributions.",
                    "总变差 = ½ Σ |P_精确 − P_正则|，在全部 q_A 上求和。范围为 0 到 1；0 表示两种分布一致。",
                ),
            ),
        ]
    )
    figure = _figure(data)
    chart(
        figure,
        "canonical_probability",
        title=tr("Exact counting and the reservoir limit", "精确计数与热库极限"),
        subtitle=f"N_A = {n_a} · N_B = {n_b} · q = {q} · βε = {data['beta_eps']:.3g}",
    )
    st.write(
        tr(
            f"Both means are ⟨q_A⟩ = {data['mean']:.3g}. The finite reservoir reduces energy fluctuations; "
            "enlarge B while keeping A and the target fraction fixed to compare the two laws.",
            f"两者的均值都是 ⟨q_A⟩ = {data['mean']:.3g}。有限热库会抑制能量涨落；"
            "保持 A 和目标比例不变，增大 B，观察两种分布的差异。",
        )
    )
    download_figure(
        figure,
        "canonical_reservoir",
        label=tr("Download reservoir comparison · HTML", "下载热库对照图 · HTML"),
    )
    with st.expander(tr("Why the Boltzmann factor appears", "玻尔兹曼因子从哪里来")):
        st.write(
            tr(
                "A and B contain distinguishable, noninteracting two-level units with the same gap ε. "
                "Weak contact permits energy exchange; coupling energy is neglected. "
                "Combined microstates at fixed total excitation q have equal weight. Lines join discrete probabilities, not densities or time trajectories.",
                "A、B 都由可区分、内部无相互作用的二能级单元组成，能隙同为 ε。弱热接触允许能量交换，耦合能忽略。"
                "总激发数 q 固定时，组合微观态等权重。图中连线连接离散概率，不表示密度或随时间演化的轨迹。",
            )
        )
        st.latex(
            r"P_{\mathrm{exact}}(q_A)=\frac{\binom{N_A}{q_A}\binom{N_B}{q-q_A}}{\binom{N_A+N_B}{q}}"
        )
        st.write(
            tr(
                "Let p = q/(N_A + N_B). The mean bath excitation is pN_B. Expanding its entropy around that energy gives a linear term; "
                "when the bath is large enough, its curvature matters little over the system's typical fluctuations.",
                "令 p = q/(N_A + N_B)，热库的平均激发数为 pN_B。在这一能量附近展开热库熵，保留线性项；"
                "当热库足够大时，在系统典型涨落范围内，熵曲率的影响变小。",
            )
        )
        st.latex(
            r"\ln\Omega_B(q-q_A)\simeq C-\beta\epsilon q_A,\qquad \beta\epsilon=\ln\frac{1-p}{p}"
        )
        st.latex(
            r"P_{\mathrm{can}}(q_A)=\frac{\binom{N_A}{q_A}e^{-\beta\epsilon q_A}}{Z_A}=\binom{N_A}{q_A}p^{q_A}(1-p)^{N_A-q_A},\qquad Z_A=(1+e^{-\beta\epsilon})^{N_A}"
        )
        st.caption(
            tr(
                "The Boltzmann factor weights each microstate. An energy level also carries its multiplicity C(N_A, q_A). "
                "β here matches the mean excitation; it is not an exact finite-difference temperature of the small bath.",
                "玻尔兹曼因子给每个微观态赋权；同一能量层还要乘上简并度 C(N_A, q_A)。"
                "这里的 β 用来匹配平均激发比例，不是小热库熵的精确有限差分温度。",
            )
        )
        st.latex(
            r"\langle q_A\rangle=N_Ap,\qquad \mathrm{Var}_{\mathrm{exact}}(q_A)=N_Ap(1-p)\frac{N_B}{N_A+N_B-1},\qquad \mathrm{Var}_{\mathrm{can}}(q_A)=N_Ap(1-p)"
        )
        st.write(
            tr(
                "The exact law enforces 0 ≤ q−q_A ≤ N_B. The canonical law keeps its full support 0..N_A; "
                "it is not renormalized to the finite bath's allowed range. As N_B grows at fixed N_A and fraction, the finite-reservoir correction tends to 1. "
                "Integer rounding can cause small changes in p between settings. This first comparison covers positive temperatures and the β = 0 limit.",
                "精确分布要求 0 ≤ q−q_A ≤ N_B。正则分布保留完整的 0..N_A 支撑，不按有限热库的允许范围截断或重新归一化。"
                "固定 N_A 和激发比例增大 N_B 时，有限热库修正因子趋近 1。整数取整可能使不同设置间的实际 p 略有变化。"
                "这一实验先展示正温度及 β = 0 极限。",
            )
        )
