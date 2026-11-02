"""Uniform quartic Landau model: stationary points versus equilibrium."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from experiments import EXPERIMENT_BY_ID
from i18n import tr
from physics import landau_free_energy, landau_stationary
from plot_theme import COLORS
from shared import chart, control_panel, download_figure, header
from state import initialize_controls

TEMPERATURE_RANGE = (0.5, 1.5)
ORDER_RANGE = (-1.15, 1.15)


def _reset_field():
    st.session_state.landau_field = 0.0


def _controls():
    initialize_controls(landau_temperature=0.75, landau_field=0.0)
    with control_panel("landau") as toolbar:
        with toolbar:
            with st.popover(tr("External field", "外场")):
                field = st.slider(
                    tr("Scaled field h", "无量纲外场 h"),
                    -0.2,
                    0.2,
                    step=0.01,
                    key="landau_field",
                    help=tr(
                        "Positive h favors positive m through −hm.", "正 h 通过 −hm 项偏向正 m。"
                    ),
                )
                st.button(tr("Reset h = 0", "恢复 h = 0"), on_click=_reset_field)
        temperature = st.slider(
            tr("Temperature · t = T/Tc", "温度 t = T/Tc"),
            *TEMPERATURE_RANGE,
            step=0.01,
            key="landau_temperature",
            help=tr(
                "Tc is the zero-field critical temperature of this model.",
                "Tc 是此模型的零外场临界温度。",
            ),
        )
    return temperature, field


def _landscape(temperature, field, data):
    m = np.linspace(*ORDER_RANGE, 601)
    fig = go.Figure(
        go.Scatter(
            x=m,
            y=landau_free_energy(m, temperature, field),
            mode="lines",
            line=dict(color=COLORS["theory"], width=2.5),
            showlegend=False,
            hovertemplate="m = %{x:.3g}<br>f = %{y:.3g}<extra></extra>",
        )
    )
    styles = {
        "stable": (tr("Global minimum", "全局极小值"), "circle", "theory"),
        "metastable": (tr("Metastable minimum", "亚稳极小值"), "circle-open", "secondary"),
        "unstable": (tr("Local maximum", "局部极大值"), "x", "muted"),
        "critical": (tr("Critical minimum", "临界极小值"), "circle", "theory"),
        "spinodal": (tr("Stationary inflection", "驻定拐点"), "diamond-open", "muted"),
    }
    for kind, (label, symbol, color) in styles.items():
        mask = np.array([value == kind for value in data["kind"]])
        if not mask.any():
            continue
        fig.add_trace(
            go.Scatter(
                x=data["m"][mask],
                y=data["free_energy"][mask],
                mode="markers",
                name=label,
                marker=dict(color=COLORS[color], symbol=symbol, size=10, line=dict(width=1.5)),
                customdata=data["curvature"][mask],
                hovertemplate=f"{label}<br>m = %{{x:.3g}}<br>f = %{{y:.3g}}<br>f″ = %{{customdata:.3g}}<extra></extra>",
            )
        )
    fig.update_layout(height=390)
    fig.update_xaxes(title=tr("Order parameter m", "序参量 m"), range=ORDER_RANGE)
    fig.update_yaxes(title=tr("Scaled free energy f", "无量纲自由能 f"))
    return fig


def _equilibrium(temperature, field, data):
    fig = go.Figure()
    if field == 0:
        low = np.linspace(TEMPERATURE_RANGE[0], 1.0, 151)
        high = np.linspace(1.0, TEMPERATURE_RANGE[1], 151)
        paths = [(low, -np.sqrt(1 - low)), (low, np.sqrt(1 - low)), (high, np.zeros_like(high))]
    else:
        temperatures = np.linspace(*TEMPERATURE_RANGE, 301)
        values = [landau_stationary(t, field)["equilibrium"][0] for t in temperatures]
        paths = [(temperatures, values)]
    for index, (x, y) in enumerate(paths):
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                showlegend=index == 0,
                legendgroup="equilibrium",
                name=tr("Global minima", "全局极小值"),
                line=dict(color=COLORS["theory"], width=2.5),
                hovertemplate="t = %{x:.3g}<br>m = %{y:.3g}<extra></extra>",
            )
        )
    fig.add_vline(x=temperature, line_dash="dot", line_width=1, line_color=COLORS["muted"])
    fig.add_trace(
        go.Scatter(
            x=[temperature] * len(data["equilibrium"]),
            y=data["equilibrium"],
            mode="markers",
            name=tr("Current temperature", "当前温度"),
            cliponaxis=False,
            marker=dict(color=COLORS["theory"], size=10, line=dict(color="white", width=1.5)),
            hovertemplate=tr("Current equilibrium", "当前平衡态")
            + "<br>t = %{x:.3g}<br>m = %{y:.3g}<extra></extra>",
        )
    )
    fig.update_layout(height=390, legend_groupclick="togglegroup")
    fig.update_xaxes(title="t = T/Tc", range=TEMPERATURE_RANGE)
    fig.update_yaxes(title=tr("Equilibrium m", "平衡序参量 m"), range=ORDER_RANGE)
    return fig


def _observation(temperature, field, data):
    if field == 0:
        if temperature < 1:
            return tr(
                "Two equally deep minima are stable; the stationary point at m = 0 is a maximum. Both equilibrium branches are shown.",
                "两侧极小值同样稳定；m = 0 虽然是驻点，却是极大值。右图保留两支平衡解。",
            )
        if temperature == 1:
            return tr(
                "At t = 1, the curvature at zero vanishes, but f = m⁴/4 still has a minimum. Zero curvature alone does not determine stability.",
                "t = 1 时，原点曲率为零，但 f = m⁴/4 仍有极小值。仅凭零曲率不能判断稳定性。",
            )
        return tr(
            "Above Tc at zero field, m = 0 is the unique minimum.",
            "零外场下，温度高于 Tc 时，m = 0 是唯一极小值。",
        )
    if "metastable" in data["kind"]:
        return tr(
            "The field tilts the two wells. The deeper minimum is equilibrium; the higher local minimum is metastable and does not appear on the equilibrium curve.",
            "外场使双谷倾斜。较深的谷底是平衡态；较高的局部极小值是亚稳态，不属于右图的平衡曲线。",
        )
    return tr(
        "The field selects one equilibrium branch. At fixed nonzero h, the equilibrium curve is smooth through t = 1; Tc labels the zero-field transition.",
        "外场选择一支平衡解。固定非零 h 时，平衡曲线平滑经过 t = 1；Tc 标记的是零外场相变。",
    )


def render():
    header(
        EXPERIMENT_BY_ID["landau"].number,
        tr("Free energy & stability", "自由能与稳定性"),
        tr(
            "Is every stationary point a stable equilibrium?",
            "自由能曲线的每个驻点，都是稳定平衡吗？",
        ),
    )
    temperature, field = _controls()
    data = landau_stationary(temperature, field)
    st.caption(
        tr(
            "Uniform quartic Landau model · t = T/Tc · dimensionless m, h and f.",
            "均匀四次 Landau 模型 · t = T/Tc · m、h、f 均为无量纲量。",
        )
    )
    landscape = _landscape(temperature, field, data)
    equilibrium = _equilibrium(temperature, field, data)
    for column, figure, key, title in zip(
        st.columns(2),
        [landscape, equilibrium],
        ["landau_landscape", "landau_equilibrium"],
        [
            tr("01 / Find the minima", "01 / 寻找极小值"),
            tr("02 / Equilibrium branches", "02 / 平衡解的分支"),
        ],
        strict=True,
    ):
        with column:
            chart(
                figure,
                key,
                title=title,
                subtitle=(
                    f"t = T/Tc = {temperature:.3g} · h = {field:.3g}\nf = (t−1)m²/2 + m⁴/4 − hm"
                ),
            )
            download_figure(figure, key)
    st.write(_observation(temperature, field, data))
    with st.expander(tr("Stationarity, curvature & equilibrium", "驻点、曲率与平衡")):
        st.latex(r"f(m;t,h)=\frac{t-1}{2}m^2+\frac14m^4-hm")
        st.latex(r"f'(m)=(t-1)m+m^3-h=0,\qquad f''(m)=t-1+3m^2")
        st.write(
            tr(
                "At fixed temperature and field, equilibrium minimizes this potential globally. Positive curvature gives a local minimum; negative curvature gives a local maximum. A local minimum above the global minimum is metastable. The curves specify equilibrium and local stability, not a relaxation time or a trajectory.",
                "固定温度与外场时，平衡态对应此势的全局极小值。正曲率给出局部极小值，负曲率给出局部极大值；高于全局最低点的局部极小值是亚稳态。曲线描述平衡与局部稳定性，不给出弛豫时间或演化轨迹。",
            )
        )
        st.latex(r"h=0:\quad m_{\rm eq}=\begin{cases}\pm\sqrt{1-t},&t<1\\0,&t\geq1\end{cases}")
        st.write(
            tr(
                "At t = 1 and h = 0, the quadratic term vanishes and the positive quartic term stabilizes the origin. For t < 1, the two symmetry-related minima are both shown: they are alternative pure equilibrium states, not an instruction to average them into m = 0.",
                "t = 1、h = 0 时，二次项消失，正的四次项仍稳定原点。t < 1 时，两侧对称极小值都画出；它们代表不同的纯平衡态，不应直接平均成 m = 0 来代替这些分支。",
            )
        )
        st.caption(
            tr(
                "A finite symmetric ensemble can have mean m = 0 by symmetry. Spontaneous symmetry breaking concerns the thermodynamic limit and the order in which an infinitesimal field is removed.",
                "有限的对称系综可因对称性而具有平均 m = 0。自发对称性破缺涉及热力学极限，以及移去无穷小外场的先后顺序。",
            )
        )
    with st.expander(tr("External field & model limits", "外场与模型的适用范围")):
        st.write(
            tr(
                "A positive h lowers the positive-m well through −hm; a negative h does the reverse. Metastability ends when a local minimum and a maximum merge. At this spinodal, f′ = f″ = 0, but the nonzero cubic term in the local expansion makes the merged point an inflection, not a stable minimum.",
                "正 h 通过 −hm 降低正 m 一侧的谷底，负 h 则相反。局部极小值与极大值合并时，亚稳态消失。在这一亚稳极限处，f′ = f″ = 0，但局部展开的三次项非零，合并点是拐点，并非稳定极小值。",
            )
        )
        st.latex(r"t<1:\quad |h_{\rm sp}|=\frac{2}{3\sqrt3}(1-t)^{3/2}")
        st.write(
            tr(
                "This phenomenological mean-field model keeps a uniform scalar order parameter and a positive quartic coefficient. Units absorb the coefficients; m is not constrained to the microscopic interval [−1, 1]. The expansion is motivated near the zero-field critical point. It omits spatial fluctuations, domains and nucleation, and is not an exact Ising simulation. Sweeping h follows global equilibrium here, so no hysteresis dynamics is implied.",
                "此现象学平均场模型保留均匀的标量序参量与正的四次项，系数吸收到单位中；m 不受微观磁化强度的 [−1, 1] 区间约束。展开以零外场临界点附近为出发点，忽略空间涨落、畴和成核，并非精确 Ising 模拟。这里扫动 h 时始终取全局平衡，不代表滞回动力学。",
            )
        )
        st.caption(
            tr(
                "The displayed f omits an m-independent background. Its values are potential values, not probabilities; a single-particle Boltzmann factor is not a distribution of this macroscopic order parameter.",
                "图中的 f 省略了与 m 无关的背景项。它是势函数值，不是概率；不能直接把单粒子玻尔兹曼因子当作这个宏观序参量的分布。",
            )
        )
