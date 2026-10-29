"""A linked Gaussian slice and conditional density, without simulated samples."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from i18n import tr
from physics import gaussian_conditioning
from plot_theme import COLORS
from shared import chart, control_panel, download_figure, header
from state import initialize_controls


def _controls():
    initialize_controls(joint_rho=0.6, joint_y0=1.0)
    with control_panel("joint"):
        left, right = st.columns(2)
        with left:
            rho = st.slider(
                tr("Correlation ρ", "相关系数 ρ"),
                -0.95,
                0.95,
                step=0.05,
                key="joint_rho",
                help=tr(
                    "Both variables keep mean 0 and standard deviation 1.",
                    "两个变量的均值始终为 0，标准差始终为 1。",
                ),
            )
        with right:
            y0 = st.slider(
                tr("Condition on Y = y₀", "给定 Y = y₀"), -3.0, 3.0, step=0.1, key="joint_y0"
            )
    return rho, y0


def _figures(model, y0):
    # Fixed coordinate/density scales make changes across settings comparable.
    x = np.linspace(-4.5, 4.5, 401)
    grid = np.linspace(-4.5, 4.5, 181)
    xx, yy = np.meshgrid(grid, grid)
    density = model["joint"].pdf(np.stack((xx, yy), axis=-1))
    joint = go.Figure(
        go.Contour(
            x=grid,
            y=grid,
            z=density,
            contours=dict(start=0.02, end=0.5, size=0.04, coloring="fill"),
            colorscale=[[0, "#FFFFFF"], [0.12, "#E4F1F2"], [1, COLORS["theory"]]],
            zmin=0,
            zmax=0.52,
            showscale=False,
            line=dict(width=0.6, color="#9FC6CA"),
            name=tr("Joint density", "联合密度"),
            showlegend=False,
            hovertemplate="x = %{x:.3g}<br>y = %{y:.3g}<br>p(x, y) = %{z:.3g}<extra></extra>",
        )
    )
    joint.add_trace(
        go.Scatter(
            x=[-4.5, 4.5],
            y=[y0, y0],
            mode="lines",
            line=dict(color=COLORS["theory"], width=3, dash="dash"),
            name=f"Y = {y0:.3g}",
            hovertemplate=f"Y = {y0:.3g}<extra></extra>",
        )
    )
    joint.update_layout(
        height=350,
        margin=dict(l=45, r=15),
        xaxis=dict(title="x", range=[-4.5, 4.5], constrain="domain"),
        yaxis=dict(title="y", range=[-4.5, 4.5], scaleanchor="x", scaleratio=1, constrain="domain"),
    )
    comparison = go.Figure()
    comparison.add_trace(
        go.Scatter(
            x=x,
            y=model["conditional"].pdf(x),
            mode="lines",
            name=tr("Conditional p(x | y₀)", "条件密度 p(x | y₀)"),
            line=dict(color=COLORS["theory"], width=3),
            hovertemplate="x = %{x:.3g}<br>p(x | y₀) = %{y:.3g}<extra></extra>",
        )
    )
    comparison.add_trace(
        go.Scatter(
            x=x,
            y=model["marginal"].pdf(x),
            mode="lines",
            name=tr("Marginal p(x)", "边缘密度 p(x)"),
            line=dict(color=COLORS["secondary"], width=2, dash="dash"),
            hovertemplate="x = %{x:.3g}<br>p(x) = %{y:.3g}<extra></extra>",
        )
    )
    comparison.update_layout(
        height=350,
        margin=dict(l=45, r=15),
        xaxis=dict(title="x", range=[-4.5, 4.5]),
        yaxis=dict(title=tr("Probability density", "概率密度"), range=[0, 1.4]),
    )
    return joint, comparison


def render():
    header(
        5,
        tr("Joint & conditional probability", "联合与条件概率"),
        tr(
            "What does knowing Y tell us about X? Both marginals stay N(0, 1).",
            "知道 Y 的值，会怎样改变我们对 X 的判断？两个边缘分布始终为 N(0, 1)。",
        ),
    )
    rho, y0 = _controls()
    model = gaussian_conditioning(rho, y0)
    joint, comparison = _figures(model, y0)
    left, right = st.columns(2)
    with left:
        chart(
            joint,
            "joint_density",
            title=tr("01 / Select a slice", "01 / 选择一个切片"),
            subtitle=tr("Joint density · line at Y = y₀", "联合密度 · 横线对应 Y = y₀"),
        )
    with right:
        chart(
            comparison,
            "joint_conditional",
            title=tr("02 / Update the density", "02 / 更新概率密度"),
            subtitle=tr("Normalize the slice to area 1", "将切片归一化，使曲线下面积为 1"),
        )
    st.caption(
        tr(
            "Marginal: integrate over Y. Conditional: normalize one slice to area 1, even in the tails.",
            "边缘密度：对 Y 积分。条件密度：将一个切片归一化至面积为 1，尾部的低密度切片也一样。",
        )
    )
    if np.isclose(rho, 0):
        st.write(
            tr(
                "At ρ = 0, the curves coincide: X and Y are independent in this jointly Gaussian model.",
                "ρ = 0 时，两条曲线重合：在这个联合高斯模型中，X 与 Y 独立。",
            )
        )
    else:
        mean, sd = model["conditional"].mean(), model["conditional"].std()
        st.write(
            tr(
                f"Given Y = {y0:.3g}, X has mean {mean:.3g} and standard deviation {sd:.3g}. "
                "The marginal stays unchanged; larger |ρ| makes the conditional curve narrower.",
                f"给定 Y = {y0:.3g}，X 的条件均值为 {mean:.3g}，条件标准差为 {sd:.3g}。"
                "边缘分布保持不变；|ρ| 越大，条件分布越窄。",
            )
        )
    download_figure(
        comparison,
        "joint_conditional",
        label=tr("Download conditional density comparison · HTML", "下载条件密度对照图 · HTML"),
    )
    with st.expander(tr("Model & derivation", "模型与推导")):
        st.write(
            tr(
                "X and Y are jointly Gaussian with zero means, unit variances and correlation ρ. "
                "Integrating over all Y gives the marginal; fixing Y and normalizing gives the conditional.",
                "X 与 Y 服从均值为零、方差为一、相关系数为 ρ 的联合高斯分布。"
                "对全部 Y 积分得到边缘密度；固定 Y 并归一化得到条件密度。",
            )
        )
        st.latex(r"p(x,y)=\frac{\exp[-(x^2-2\rho xy+y^2)/(2(1-\rho^2))]}{2\pi\sqrt{1-\rho^2}}")
        st.latex(r"p_X(x)=\int_{-\infty}^{\infty}p(x,y)\,dy=\frac{e^{-x^2/2}}{\sqrt{2\pi}}")
        st.latex(
            r"p(x\mid y_0)=\frac{p(x,y_0)}{p_Y(y_0)},\qquad X\mid Y=y_0\sim\mathcal N(\rho y_0,\,1-\rho^2)"
        )
        st.caption(
            tr(
                "The second Normal parameter is variance. For continuous Y, P(Y = y₀) = 0; "
                "this is a conditional density, not selection from a finite-width band. "
                "Zero correlation does not imply independence for general distributions. "
                "The endpoints ρ = ±1 are excluded because the joint density becomes singular.",
                "正态分布的第二个参数是方差。连续变量满足 P(Y = y₀) = 0；"
                "这里使用条件密度，而非从有限宽度区间筛选样本。"
                "一般分布中，不相关不代表独立。ρ = ±1 会使联合分布退化，因此不包含这两个端点。",
            )
        )
