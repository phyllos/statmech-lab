"""Microcanonical counting for distinguishable, noninteracting two-level units."""

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.special import xlogy

from i18n import tr
from physics import sample_microstate, two_level
from shared import COLORS, chart, control_panel, download_figure, header, insight, metric_row
from state import initialize_controls


def _beta_label(value):
    if np.isposinf(value):
        return "+∞"
    if np.isneginf(value):
        return "−∞"
    return f"{value:.3g}"


def render():
    initialize_controls(ent_n=40)
    header(
        "04",
        tr("Microstates & entropy", "微观态与熵"),
        tr(
            "How many distinct microscopic arrangements can realize the same total energy?",
            "同一个总能量，可以由多少种不同的微观排列实现？",
        ),
    )
    st.caption(
        tr(
            "N distinguishable, noninteracting units · two energy levels, 0 and ε · fixed energy E = qε.",
            "N 个可区分、无相互作用的单元 · 两个能级 0 与 ε · 固定能量 E = qε。",
        )
    )

    with control_panel(
        "entropy",
        action_key="ent_shuffle",
        seed_key="ent_draw",
        seed_start=0,
        rearrange=True,
    ):
        c1, c2 = st.columns([1.2, 1.4], vertical_alignment="bottom")
        with c1:
            n = st.slider(tr("Number of units N", "单元数 N"), 8, 200, key="ent_n")
        if "ent_q" not in st.session_state:
            st.session_state["ent_q"] = n // 4
        st.session_state["ent_q"] = min(n, int(st.session_state["ent_q"]))
        with c2:
            q = st.slider(tr("Excited units q", "激发态单元数 q"), 0, n, key="ent_q")

    data = two_level(n, q)
    seed = 51504 + st.session_state.get("ent_draw", 0)
    state = np.asarray(sample_microstate(n, q, seed))
    log_omega = float(data["selected_log_multiplicity"])
    omega = math.comb(n, q)
    omega_label = f"{omega:,}" if omega < 1_000_000 else f"{omega:.3g}"
    beta = float(data["beta_epsilon"][q])

    metric_row(
        [
            (
                tr("Accessible microstates Ω", "可达微观态数 Ω"),
                omega_label,
                tr("Distinct arrangements at fixed q", "同一 q 层内的不同排列数"),
            ),
            (
                tr("Entropy S / k_B", "熵 S / k_B"),
                f"{log_omega:.3g}",
                tr("Exact counting: ln C(N, q)", "精确计数：ln C(N, q)"),
            ),
            (
                tr("Excitation probability q / N", "单元激发概率 q / N"),
                f"{q / n:.1%}",
                tr("Uniform sampling within this energy level", "在这一固定能量层内均匀抽样"),
            ),
            (
                tr("β ε · large-N approximation", "β ε · 大 N 近似"),
                _beta_label(beta),
                tr("β = 1 / (k_B T), not a probability", "β = 1 / (k_B T)，不是概率"),
            ),
        ]
    )

    columns = min(20, n)
    positions = np.arange(n)
    fig = go.Figure()
    for excited, color, label in [
        (0, COLORS["muted"], tr("Ground state · 0", "基态 · 0")),
        (1, COLORS["sample"], tr("Excited state · ε", "激发态 · ε")),
    ]:
        selected = positions[state == excited]
        fig.add_trace(
            go.Scatter(
                x=selected % columns,
                y=-(selected // columns),
                mode="markers",
                marker=dict(size=18, color=color, line=dict(color="white", width=1.5)),
                name=label,
                customdata=selected + 1,
                hovertemplate=tr(
                    f"Unit %{{customdata}}<br>{label}<extra></extra>",
                    f"单元 %{{customdata}}<br>{label}<extra></extra>",
                ),
            )
        )
    fig.update_layout(
        height=max(200, 36 * math.ceil(n / columns) + 85),
        xaxis=dict(visible=False, range=[-0.7, columns - 0.3], fixedrange=True),
        yaxis=dict(visible=False, range=[-math.ceil(n / columns) + 0.3, 0.7], fixedrange=True),
        margin=dict(l=15, r=15, t=10, b=30),
    )
    chart(
        fig,
        key="ent_state_chart",
        title=tr("01 / One possible microstate", "01 / 一个可能的微观态"),
        subtitle=tr(
            f"{q} excited · {n - q} ground-state units · E = {q}ε",
            f"{q} 个激发态 · {n - q} 个基态 · E = {q}ε",
        ),
    )
    st.caption(
        tr(
            f"Each dot is a distinguishable unit: {q} excited and {n - q} in the ground state. Rearranging changes the microstate while the total energy remains {q}ε.",
            f"每个圆点代表一个可区分单元。当前 {q} 个激发态、{n - q} 个基态；重新排列只改变微观态，总能量始终为 {q}ε。",
        )
    )

    fractions = np.asarray(data["q_grid"]) / n
    left, right = st.columns(2)
    with left:
        exact = np.asarray(data["entropy_per_particle"])
        dense = np.linspace(0, 1, 401)
        asymptotic = -(xlogy(dense, dense) + xlogy(1 - dense, 1 - dense))
        fig = go.Figure(
            go.Scatter(
                x=fractions,
                y=exact,
                mode="lines",
                name=tr("Exact: ln Ω / N", "精确：ln Ω / N"),
                line=dict(color=COLORS["theory"], width=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dense,
                y=asymptotic,
                mode="lines",
                name=tr("Stirling approximation", "Stirling 大 N 近似"),
                line=dict(color=COLORS["muted"], width=1.8, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[q / n],
                y=[log_omega / n],
                mode="markers",
                name=tr("Selected energy", "当前能量"),
                marker=dict(color=COLORS["sample"], size=12, line=dict(color="white", width=2)),
            )
        )
        fig.update_layout(
            height=350,
            xaxis_title=tr("Excited fraction x = q/N", "激发比例 x = q/N"),
            yaxis_title=tr("Entropy per unit S/(Nk_B)", "每单元熵 S/(Nk_B)"),
            xaxis_range=[0, 1],
        )
        chart(
            fig,
            key="ent_entropy_chart",
            title=tr("02 / Counting and entropy", "02 / 排列数与熵"),
            subtitle=tr("Exact counting and large-N approximation", "精确组合计数与大 N 近似"),
        )
        entropy_figure = fig
        st.caption(
            tr(
                "The solid curve uses exact finite-N counting; the dashed curve is the thermodynamic limit. The curves approach each other as N grows.",
                "实线使用有限 N 的精确组合数；虚线是热力学极限。增大 N 后，两条曲线逐渐接近。",
            )
        )
    with right:
        interior = np.linspace(0.005, 0.995, 399)
        betas = np.log((1 - interior) / interior)
        fig = go.Figure(
            go.Scatter(
                x=interior,
                y=betas,
                mode="lines",
                name=tr("β ε · large N", "β ε · 大 N 近似"),
                line=dict(color=COLORS["accent"], width=3),
            )
        )
        fig.add_hline(y=0, line_color=COLORS["muted"], line_width=1)
        fig.add_vrect(x0=0.5, x1=1, fillcolor="rgba(120,104,176,.07)", line_width=0)
        fig.add_annotation(
            x=0.98,
            xref="paper",
            y=0.04,
            yref="paper",
            text=tr("Population inversion · β < 0", "粒子数反转 · β < 0"),
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            borderpad=3,
            bgcolor="rgba(255,255,255,.88)",
            font=dict(size=11, color=COLORS["accent"]),
        )
        if np.isfinite(beta):
            fig.add_trace(
                go.Scatter(
                    x=[q / n],
                    y=[beta],
                    mode="markers",
                    name=tr("Selected energy", "当前能量"),
                    marker=dict(color=COLORS["sample"], size=12, line=dict(color="white", width=2)),
                )
            )
        fig.update_layout(
            height=350,
            xaxis_title=tr("Excited fraction x = q/N", "激发比例 x = q/N"),
            yaxis_title="β ε = ε/(k_BT)",
            xaxis_range=[0, 1],
        )
        chart(
            fig,
            key="ent_beta_chart",
            title=tr("03 / Slope and temperature", "03 / 熵的斜率与温度"),
            subtitle=tr("Positive and negative temperature via β", "用逆温度 β 观察正温与负温分支"),
        )
        st.caption(
            tr(
                "The β curve uses Stirling's approximation. Its endpoints tend to ±∞ and are omitted. Finite-N energies are discrete, so this continuous derivative is not an exact finite-difference temperature.",
                "β 曲线使用 Stirling 近似；端点趋于 ±∞，图中省略端点。有限 N 的能量离散，不能把这条连续导数视为精确差分结果。",
            )
        )

    if q == 0 or q == n:
        insight(
            tr("Only one arrangement", "只有一种排列"),
            tr(
                "When every unit occupies the same level, Ω = 1 and S = k_B ln 1 = 0. This is the counting entropy of this two-level model.",
                "全部处于同一能级时，Ω = 1，因此 S = k_B ln 1 = 0。这里讨论的是这个二能级模型的计数熵。",
            ),
        )
    elif 2 * q == n:
        insight(
            tr("Maximum entropy", "熵达到最大值"),
            tr(
                "Half excitation gives the most arrangements. The entropy slope vanishes in the large-N approximation, so β = 0. This is the infinite-temperature limit, not zero temperature.",
                "半数激发时，可实现的排列数最多，熵曲线在大 N 近似下斜率为 0，即 β = 0。这对应无限温极限，而不是零温。",
            ),
        )
    elif 2 * q > n:
        insight(
            tr("Population inversion and negative temperature", "粒子数反转与负温度"),
            tr(
                "With more excited than ground-state units, adding energy reduces the number of arrangements and gives a negative entropy slope. This branch requires an upper energy bound; in thermal energy exchange, a negative-temperature state is hotter than every positive-temperature state.",
                "激发态比基态更多时，继续增加能量反而减少排列数，因此熵斜率为负。这样的负温度分支依赖能量有上界；在热平衡的能量交换意义下，它比任何正温状态更热。",
            ),
        )
    else:
        insight(
            tr("Try this: keep N fixed and increase q", "试一试：保持 N，增加 q"),
            tr(
                "From the ground state toward half excitation, the number of arrangements rises rapidly. Beyond half excitation, it falls. The counts for q and N−q are equal, producing a symmetric entropy curve.",
                "从全部基态走向半数激发，可实现的排列迅速增加。再越过半数激发，排列数开始减少。q 与 N−q 的组合数相同，所以熵曲线左右对称。",
            ),
        )

    st.info(
        tr(
            "In the microcanonical ensemble, E and N are fixed. Sampling is uniform over the Ω microstates at the selected q. Other q values represent different macroscopic constraints, not the energy probability distribution of this fixed-energy system.",
            "在微正则系综中，E 与 N 已固定，只在当前 q 层内的 Ω 个微观态之间等概率抽样。图上不同 q 的点是不同宏观约束，不能把它们直接当成当前系统的能量概率分布。",
        ),
        icon=":material/info:",
    )

    with st.expander(
        tr("Mathematics · from counting to temperature", "数学说明 · 从组合计数到温度")
    ):
        st.latex(
            r"E=q\epsilon,\qquad \Omega(N,q)=\binom Nq=\frac{N!}{q!(N-q)!},\qquad S=k_B\ln\Omega"
        )
        st.markdown(
            tr(
                "Choosing the q excited units specifies a microstate. For any designated unit, its excitation probability follows by counting states of the remaining units:",
                "选出 q 个带激发的单元，就确定一个微观态。对任意指定的单元，激发概率来自其余单元的状态计数：",
            )
        )
        st.latex(r"P(n_1=1\mid N,q)=\frac{\binom{N-1}{q-1}}{\binom Nq}=\frac qN")
        st.markdown(
            tr(
                "For large N and occupations away from the endpoints, apply Stirling's approximation with $x=q/N$:",
                "对大 N 且远离端点的占据数使用 Stirling 近似，令 $x=q/N$：",
            )
        )
        st.latex(r"\frac{S}{Nk_B}\simeq -x\ln x-(1-x)\ln(1-x)")
        st.latex(
            r"\frac1T=\left(\frac{\partial S}{\partial E}\right)_N,\qquad \beta\epsilon\simeq\ln\frac{1-x}{x}"
        )
        st.markdown(
            tr(
                "As energy increases, $β$ changes from positive through zero to negative. Plotting $β$ avoids the divergence of $T$ at half excitation. The units do not interact; dot positions identify units and do not represent spatial interactions.",
                "$β$ 随能量增大从正变为零再变为负；图中使用 $β$，可避免直接画 $T$ 时在半数激发处的发散。此模型不包含单元间相互作用，圆点位置只用于显示标签，没有空间相互作用含义。",
            )
        )
        st.caption(tr(f"Exact integer Ω: {omega:,}", f"当前 Ω 的精确整数：{omega:,}"))
    download_figure(entropy_figure, "two_level_entropy")
