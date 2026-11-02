"""Contrast one Gaussian velocity component with the magnitude of 3D velocity."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from experiments import EXPERIMENT_BY_ID
from i18n import tr
from physics import ideal_gas_speeds
from plot_theme import COLORS
from shared import chart, control_panel, download_figure, header
from state import initialize_controls

VIEW_LIMIT = 8.0


def _controls():
    initialize_controls(gas_temperature=1.0)
    with control_panel("gas"):
        return st.slider(
            tr("Temperature · T / T₀", "温度 T / T₀"),
            0.25,
            4.0,
            step=0.05,
            key="gas_temperature",
            help=tr(
                "T₀ is a fixed reference temperature, not a critical temperature. Mass and axis units stay fixed as T changes.",
                "T₀ 是固定的参考温度，不是临界温度。改变 T 时，粒子质量与坐标单位保持不变。",
            ),
        )


def _figures(data):
    """Fixed axes expose thermal broadening without rescaling it away."""
    figures = []
    for kind, lo, peak, xlabel, peak_label in (
        (
            "component",
            -VIEW_LIMIT,
            0.0,
            tr("Component · v_x / v₀", "速度分量 v_x / v₀"),
            tr("Component mode", "分量众数"),
        ),
        (
            "speed",
            0.0,
            data["most_probable_speed"],
            tr("Speed · |v| / v₀", "速率 |v| / v₀"),
            tr("Most probable speed", "最概然速率"),
        ),
    ):
        law = data[kind]
        x = np.linspace(lo, VIEW_LIMIT, 801)
        coordinate = "v_x / v₀" if kind == "component" else "|v| / v₀"
        density_label = tr("Density", "概率密度")
        figure = go.Figure()
        figure.add_trace(
            go.Scatter(
                x=x,
                y=law.pdf(x),
                mode="lines",
                line=dict(color=COLORS["theory"], width=2.5),
                hovertemplate=f"{coordinate} = %{{x:.3g}}<br>{density_label} = %{{y:.3g}}<extra></extra>",
            )
        )
        figure.add_vline(
            x=peak,
            line_color=COLORS["muted"],
            line_dash="dot",
            line_width=1,
        )
        figure.add_trace(
            go.Scatter(
                x=[peak],
                y=[float(law.pdf(peak))],
                mode="markers",
                marker=dict(color=COLORS["theory"], size=9, line=dict(color="white", width=1.5)),
                hovertemplate=f"{peak_label}<br>{coordinate} = %{{x:.3g}}<extra></extra>",
            )
        )
        figure.update_layout(height=360, showlegend=False, margin=dict(l=45, r=20))
        figure.update_xaxes(title=xlabel, range=[lo, VIEW_LIMIT], dtick=2)
        figure.update_yaxes(title=tr("Probability density", "概率密度"), range=[0, 1.3], dtick=0.25)
        figures.append(figure)
    return figures


def render():
    header(
        EXPERIMENT_BY_ID["gas"].number,
        tr("Ideal gas: components & speed", "理想气体：速度分量与速率"),
        tr(
            "A velocity component peaks at zero. Why does the speed peak elsewhere?",
            "速度分量在零附近最常见，为什么速率的峰值却不在零？",
        ),
    )
    temperature = _controls()
    data = ideal_gas_speeds(temperature)
    st.caption(
        tr(
            "3D classical ideal gas at rest · fixed mass m · v₀ = √(k_B T₀ / m), a fixed reference speed.",
            "三维经典理想气体，无整体流动 · 固定质量 m · v₀ = √(k_B T₀ / m)，为固定参考速度。",
        )
    )
    component, speed = _figures(data)
    reference_units = tr(
        "v₀ = √(k_B T₀ / m) · fixed m, T₀",
        "v₀ = √(k_B T₀ / m) · 固定 m、T₀",
    )
    left, right = st.columns(2)
    with left:
        chart(
            component,
            "gas_component",
            title=tr("01 / One velocity component", "01 / 一个速度分量"),
            subtitle=(
                f"T/T₀ = {temperature:.3g} · σ_x/v₀ = {data['component_sd']:.3g}\n{reference_units}"
            ),
        )
        download_figure(
            component,
            "gas_component",
            label=tr("Download component · HTML", "下载分量分布图 · HTML"),
        )
    with right:
        chart(
            speed,
            "gas_speed",
            title=tr("02 / Speed in three dimensions", "02 / 三维空间中的速率"),
            subtitle=(
                f"T/T₀ = {temperature:.3g} · v_mp/v₀ = {data['most_probable_speed']:.3g}\n"
                f"{reference_units}"
            ),
        )
        download_figure(
            speed, "gas_speed", label=tr("Download speed · HTML", "下载速率分布图 · HTML")
        )
    st.write(
        tr(
            "A component can be positive or negative. Speed combines all three components: spherical shells contribute a 4πv² factor, shifting its density peak away from zero. Heating broadens both distributions.",
            "分量可正可负；速率由三个分量共同决定。速度空间中的球壳带来 4πv² 因子，使速率密度的峰值偏离零。升温时，两种分布都会变宽。",
        )
    )
    component_tail = 2 * data["component"].sf(VIEW_LIMIT)
    speed_tail = data["speed"].sf(VIEW_LIMIT)
    component_tail_text = "<0.01%" if component_tail < 0.0001 else f"{component_tail:.2%}"
    speed_tail_text = "<0.01%" if speed_tail < 0.0001 else f"{speed_tail:.2%}"
    st.caption(
        tr(
            f"Outside the view: component {component_tail_text} · speed {speed_tail_text}. Fixed axes; densities are not renormalized to the view.",
            f"图外概率：分量 {component_tail_text} · 速率 {speed_tail_text}。坐标范围固定，密度不按视窗重新归一化。",
        )
    )
    with st.expander(tr("Why the spherical shell matters", "为什么要考虑球壳")):
        st.write(
            tr(
                "This is a one-particle equilibrium distribution in the canonical, classical ideal-gas model. With no bulk flow, the three velocity components are independent zero-mean Gaussians. No collision dynamics or random samples are simulated here.",
                "这里展示经典理想气体正则模型中单个粒子的平衡分布。没有整体流动时，三个速度分量是相互独立、均值为零的高斯变量。本页不模拟碰撞动力学，也不生成随机样本。",
            )
        )
        st.latex(
            r"\begin{aligned}\sigma^2&=\frac{k_BT}{m}\\"
            r"f_x(v_x)&=\frac{e^{-v_x^2/(2\sigma^2)}}{\sqrt{2\pi}\sigma}\\"
            r"f_{\mathbf v}(\mathbf v)&=\frac{e^{-|\mathbf v|^2/(2\sigma^2)}}{(2\pi\sigma^2)^{3/2}}\end{aligned}"
        )
        st.write(
            tr(
                "A component density integrates over v_y and v_z. A speed density instead collects every direction at the same radius v = |v|. A thin spherical shell has volume 4πv² dv.",
                "分量密度通过对 v_y、v_z 积分得到；速率密度则汇集同一半径 v = |v| 上的所有方向。薄球壳的体积为 4πv² dv。",
            )
        )
        st.latex(
            r"\begin{aligned}P(v\leq|\mathbf v|<v+dv)&\simeq g(v)\,dv\\"
            r"g(v)&=4\pi v^2 f_{\mathbf v}(\mathbf v)\big|_{|\mathbf v|=v}\\"
            r"&=\sqrt{\frac{2}{\pi}}\frac{v^2}{\sigma^3}e^{-v^2/(2\sigma^2)},\quad v\geq0\end{aligned}"
        )
        st.write(
            tr(
                "Near zero the shell volume is small; at high speeds the Boltzmann factor suppresses the density. Their competition produces a nonzero most probable speed. For continuous distributions, probability belongs to an interval; a density peak does not give a finite probability to one exact velocity.",
                "零附近的球壳体积很小，高速处又受到玻尔兹曼因子的抑制；两者共同产生非零的最概然速率。连续分布的概率对应区间，密度峰值不表示某个精确速度具有有限概率。",
            )
        )
        st.latex(r"|\mathbf v|=\sqrt{v_x^2+v_y^2+v_z^2}\ne |v_x|")
        st.caption(
            tr(
                "Taking only |v_x| folds the Gaussian into a half-normal distribution, whose mode remains zero. Maxwell's speed law comes from three components, not from taking the absolute value of one.",
                "只取 |v_x| 会将高斯折叠成半正态分布，众数仍为零。麦克斯韦速率分布来自三个分量，不是对单个分量取绝对值。",
            )
        )
    with st.expander(tr("Typical speeds, units & assumptions", "典型速率、单位与适用范围")):
        st.latex(
            r"\begin{aligned}v_{\mathrm{mp}}&=\sqrt{2}\sigma\\"
            r"\langle v\rangle&=\sqrt{8/\pi}\sigma\\"
            r"v_{\mathrm{rms}}&=\sqrt{\langle v^2\rangle}=\sqrt{3}\sigma\end{aligned}"
        )
        st.write(
            tr(
                f"At this temperature, in units of v₀: most probable {data['most_probable_speed']:.3g}, mean {data['mean_speed']:.3g}, RMS {data['rms_speed']:.3g}. The mean velocity vector is zero; the mean speed is positive.",
                f"当前温度下，以 v₀ 为单位：最概然速率 {data['most_probable_speed']:.3g}，平均速率 {data['mean_speed']:.3g}，方均根速率 {data['rms_speed']:.3g}。平均速度矢量为零，平均速率大于零。",
            )
        )
        st.latex(
            r"\begin{aligned}\theta&=T/T_0,\quad v_0=\sqrt{k_BT_0/m}\\"
            r"u&=v/v_0,\quad \sigma/v_0=\sqrt{\theta}\\"
            r"g_u(u)&=v_0\,g_v(v_0u)\end{aligned}"
        )
        st.write(
            tr(
                "The plotted densities are with respect to velocity divided by the fixed v₀. Both have unit area over their full support. Scaling the horizontal axis by the current σ instead would hide the temperature dependence of their widths.",
                "图中密度对应以固定 v₀ 归一化的速度变量，在完整支撑上面积均为 1。如果改用当前温度下的 σ 归一化横轴，分布宽度随温度的变化就会被消去。",
            )
        )
        st.latex(r"\langle E_{\mathrm{kin}}\rangle=\tfrac12m\langle v^2\rangle=\tfrac32k_BT")
        st.caption(
            tr(
                "The model assumes positive temperature, nonrelativistic motion and the dilute classical regime. A finite isolated gas has an energy constraint and need not have an exactly Maxwellian marginal. This page uses the canonical law; it does not derive it from the CLT or model quantum degeneracy, mixing entropy or equilibration.",
                "模型假定正温度、非相对论运动与稀薄经典条件。有限孤立气体受到总能量约束，其边缘分布不一定精确满足麦克斯韦形式。本页使用正则分布，不用 CLT 推导它，也不模拟量子简并、混合熵或达到平衡的过程。",
            )
        )
