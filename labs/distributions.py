"""Probability, sampling and Tukey boxplots, with a shared horizontal scale."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from i18n import tr
from interactions import comparison_controls
from physics import histogram_density, make_distribution, sample_summary
from shared import COLORS, chart, download_figure, header, insight, metric_row
from state import initialize_controls

NAMES = {
    "normal": ("Normal", "Normal · 正态"),
    "uniform": ("Uniform", "Uniform · 均匀"),
    "exponential": ("Exponential", "Exponential · 指数"),
    "lognormal": ("Lognormal", "Lognormal · 对数正态"),
    "pareto": ("Pareto", "Pareto · 帕累托"),
    "student_t": ("Student t", "Student t · t 分布"),
    "cauchy": ("Cauchy", "Cauchy · 柯西"),
}


def _shape(name):
    if name == "pareto":
        return st.slider(
            tr("Shape parameter α", "形状参数 α"), 0.5, 8.0, step=0.1, key="dist_shape_pareto"
        )
    if name == "lognormal":
        return st.slider(
            tr("Log-space standard deviation σ", "对数标准差 σ"),
            0.2,
            2.0,
            step=0.1,
            key="dist_shape_lognormal",
        )
    if name == "student_t":
        return st.slider(
            tr("Degrees of freedom ν", "自由度 ν"), 1.0, 30.0, step=0.5, key="dist_shape_t"
        )
    st.caption(
        {
            "normal": tr("Reference: μ = 0, σ = 1", "基准：μ = 0，σ = 1"),
            "uniform": tr("Reference: mean 0, variance 1", "基准：均值 0，方差 1"),
            "exponential": tr("Reference: λ = 1", "基准：λ = 1"),
            "cauchy": tr("Location 0, scale 1; mean undefined", "位置 0，尺度 1；均值不存在"),
        }[name]
    )
    return 3.0


def render():
    initialize_controls(
        dist_shape_pareto=3.0,
        dist_shape_lognormal=0.8,
        dist_shape_t=5.0,
        dist_n=300,
        dist_interval=(0.25, 0.75),
        dist_fences=True,
    )
    labels = {name: tr(*pair) for name, pair in NAMES.items()}
    header(
        "01",
        tr("Distributions & boxplots", "分布与箱型图"),
        tr(
            "From probability areas to observed data: connect the PDF, CDF, and boxplot in one experiment.",
            "从一段面积到一组数据：让 PDF、CDF 和箱型图讲述同一个概率故事。",
        ),
    )
    with st.container(border=True, key="controls_distributions"):
        a, b, c, d = st.columns([1.4, 1.2, 1.1, 0.8], vertical_alignment="bottom")
        with a:
            name = st.selectbox(
                tr("Population distribution", "选择总体分布"),
                list(NAMES),
                format_func=labels.get,
                key="dist_name",
            )
        with b:
            shape = _shape(name)
        with c:
            n = st.select_slider(
                tr("Sample size n", "样本量 n"), [50, 100, 300, 1000, 3000], key="dist_n"
            )
        with d:
            if st.button(
                tr("↻ Resample", "↻ 重新抽样"), key="dist_resample", use_container_width=True
            ):
                st.session_state["dist_seed"] = st.session_state.get("dist_seed", 515) + 1
        interval_column, tools_column = st.columns([1.8, 1.2], vertical_alignment="bottom")
        with interval_column:
            probabilities = st.slider(
                tr("Probability interval", "概率区间"),
                0.01,
                0.99,
                step=0.01,
                key="dist_interval",
                help=tr(
                    "The endpoints are cumulative probabilities. Move them to link the PDF area, CDF endpoints and the interval band on the sample plot.",
                    "两端是累计概率。调整端点，PDF 面积、CDF 端点和样本图的区间阴影会同步变化。",
                ),
            )
        with tools_column:
            tools_row = st.container(horizontal=True)
        with tools_row:
            with st.popover(
                tr("Display options", "显示选项"),
                icon=":material/tune:",
                key="display_distributions",
            ):
                align = st.toggle(
                    tr("Align median and IQR", "按中位数与 IQR 对齐"),
                    key="dist_align",
                    help=tr(
                        "Shift the population median to 0 and scale its IQR to 1; this does not use the mean or standard deviation.",
                        "将总体中位数移到 0，将总体 IQR 缩放为 1；这不使用均值和标准差。",
                    ),
                )
                legacy_views = {"主体与箱体": "body", "中央 99% 概率区间": "central99"}
                if st.session_state.get("dist_view") in legacy_views:
                    st.session_state["dist_view"] = legacy_views[st.session_state["dist_view"]]
                view_names = {
                    "body": tr("Body and boxplot", "主体与箱体"),
                    "central99": tr("Central 99% interval", "中央 99% 概率区间"),
                }
                view = st.selectbox(
                    tr("Horizontal view", "横轴视窗"),
                    ["body", "central99"],
                    format_func=view_names.get,
                    key="dist_view",
                    help=tr(
                        "Changes only the visible range. Statistics use the full sample.",
                        "仅改变显示范围；统计量始终使用完整样本。",
                    ),
                )
                show_fences = st.toggle(
                    tr("Show 1.5 IQR fences", "显示 1.5 IQR 围栏"), key="dist_fences"
                )
    rv = make_distribution(name, shape, align)
    seed = st.session_state.get("dist_seed", 515)
    sample = rv.rvs(size=n, random_state=np.random.default_rng(seed))
    summary = sample_summary(sample)
    settings = dict(name=name, shape=shape, align=align, n=n, seed=seed)

    def describe(saved):
        symbol = {"pareto": "α", "lognormal": "σ", "student_t": "ν"}.get(saved["name"])
        parameter = f", {symbol} = {saved['shape']:g}" if symbol else ""
        scale = tr("aligned", "已对齐") if saved["align"] else tr("original scale", "原始尺度")
        return f"{labels[saved['name']]}{parameter} · {scale} · n = {saved['n']:,} · seed = {saved['seed']}"

    with tools_row:
        reference = comparison_controls(
            "distributions", settings, describe, model_keys=("name", "shape", "align")
        )
    previous = (
        rv.rvs(size=reference["n"], random_state=np.random.default_rng(reference["seed"]))
        if reference
        else None
    )
    previous_summary = sample_summary(previous) if previous is not None else None
    if view == "body":
        tq1, tq3 = rv.ppf([0.25, 0.75])
        tiqr = tq3 - tq1
        support_lo, support_hi = rv.support()
        lo, hi = max(support_lo, tq1 - 2 * tiqr), min(support_hi, tq3 + 2 * tiqr)
    else:
        lo, hi = rv.ppf([0.005, 0.995])
    p_lo, p_hi = rv.cdf([lo, hi])
    left, right = rv.ppf(probabilities)
    # Quantile spacing resolves the narrow body even when a heavy tail stretches
    # the visible x range by several orders of magnitude.
    x = rv.ppf(np.linspace(p_lo, p_hi, 850))
    selected_x = rv.ppf(np.linspace(probabilities[0], probabilities[1], 300))
    selected = (sample >= left) & (sample <= right)
    outside = int(np.count_nonzero((sample < lo) | (sample > hi)))
    metric_row(
        [
            (
                tr("Theoretical probability", "理论区间概率"),
                f"{probabilities[1] - probabilities[0]:.0%}",
                tr("PDF area = CDF increment", "PDF 面积 = CDF 的增量"),
            ),
            (
                tr("Observed fraction", "样本区间比例"),
                f"{selected.mean():.1%}",
                tr(f"{selected.sum()} / {n} observations", f"{selected.sum()} / {n} 个观测值"),
            ),
            (
                tr("Sample median", "样本中位数"),
                f"{summary['median']:.3g}",
                tr(f"Population median {rv.median():.3g}", f"总体中位数 {rv.median():.3g}"),
            ),
            (
                tr("Sample IQR", "样本 IQR"),
                f"{summary['iqr']:.3g}",
                tr("Q₃ − Q₁ · middle 50%", "Q₃ − Q₁ · 中间约 50%"),
            ),
        ]
    )

    pdf = go.Figure()
    edges = rv.ppf(np.linspace(p_lo, p_hi, 38))
    density = histogram_density(sample, edges)
    pdf.add_trace(
        go.Bar(
            x=(edges[:-1] + edges[1:]) / 2,
            y=density,
            width=np.diff(edges),
            name=tr("Sample histogram", "样本直方图"),
            marker_color=COLORS["sample"],
            opacity=0.38,
            hovertemplate=tr(
                "x=%{x:.3g}<br>Frequency density=%{y:.3g}<extra></extra>",
                "x=%{x:.3g}<br>频率密度=%{y:.3g}<extra></extra>",
            ),
        )
    )
    pdf.add_trace(
        go.Scatter(
            x=selected_x,
            y=rv.pdf(selected_x),
            fill="tozeroy",
            fillcolor="rgba(8,126,139,.16)",
            line=dict(width=0),
            name=tr("Selected area", "选中区间面积"),
            hoverinfo="skip",
        )
    )
    pdf.add_trace(
        go.Scatter(
            x=x,
            y=rv.pdf(x),
            line=dict(color=COLORS["theory"], width=3),
            name=tr("Population PDF", "总体 PDF"),
            hovertemplate="x=%{x:.3g}<br>f(x)=%{y:.3g}<extra></extra>",
        )
    )
    if previous is not None:
        previous_density = histogram_density(previous, edges)
        pdf.add_trace(
            go.Scatter(
                x=np.repeat(edges, 2)[1:-1],
                y=np.repeat(previous_density, 2),
                mode="lines",
                name=tr("Saved sample", "保留样本"),
                line=dict(color=COLORS["muted"], dash="dash", width=1.7),
            )
        )
    pdf.update_layout(
        title=tr("01 / Probability is area", "01 / 概率是面积"),
        height=320,
        barmode="overlay",
        xaxis_title="x",
        yaxis_title=tr("Density f(x)", "概率密度 f(x)"),
    )
    pdf.update_xaxes(range=[lo, hi])
    pdf.update_yaxes(rangemode="tozero")

    cdf = go.Figure()
    ordered = np.sort(sample)
    visible_x = ordered[(ordered >= lo) & (ordered <= hi)]
    ecdf_x = np.r_[lo, visible_x, hi]
    ecdf_y = np.searchsorted(ordered, ecdf_x, side="right") / n
    cdf.add_trace(
        go.Scatter(
            x=x,
            y=rv.cdf(x),
            name=tr("Population CDF", "总体 CDF"),
            line=dict(color=COLORS["theory"], width=3),
            hovertemplate="x=%{x:.3g}<br>F(x)=%{y:.3g}<extra></extra>",
        )
    )
    cdf.add_trace(
        go.Scatter(
            x=ecdf_x,
            y=ecdf_y,
            name=tr("Empirical CDF", "经验 CDF"),
            line=dict(color=COLORS["sample"], width=2, shape="hv"),
            hovertemplate="x=%{x:.3g}<br>F̂(x)=%{y:.3g}<extra></extra>",
        )
    )
    cdf.add_vrect(x0=left, x1=right, fillcolor=COLORS["theory"], opacity=0.08, line_width=0)
    cdf.add_trace(
        go.Scatter(
            x=[left, right],
            y=list(probabilities),
            mode="markers",
            marker=dict(size=9, color=COLORS["accent"]),
            name=tr("Interval endpoints", "区间端点"),
            hovertemplate="x=%{x:.3g}<br>F(x)=%{y:.2f}<extra></extra>",
        )
    )
    if previous is not None:
        previous_ordered = np.sort(previous)
        previous_x = np.r_[
            lo, previous_ordered[(previous_ordered >= lo) & (previous_ordered <= hi)], hi
        ]
        cdf.add_trace(
            go.Scatter(
                x=previous_x,
                y=np.searchsorted(previous_ordered, previous_x, side="right") / len(previous),
                name=tr("Saved sample CDF", "保留样本 CDF"),
                mode="lines",
                line=dict(color=COLORS["muted"], dash="dash", width=1.7, shape="hv"),
            )
        )
    cdf.update_layout(
        title=tr("02 / Cumulative probability", "02 / 累计概率的增量"),
        height=320,
        xaxis_title="x",
        yaxis_title=tr("Cumulative probability F(x)", "累计概率 F(x)"),
    )
    cdf.update_xaxes(range=[lo, hi])
    cdf.update_yaxes(range=[0, 1])
    a, b = st.columns(2)
    with a:
        chart(
            pdf,
            key="dist_pdf",
            subtitle=tr("PDF with sampled frequencies", "密度曲线与样本频率；阴影代表选中概率"),
        )
    with b:
        chart(
            cdf,
            key="dist_cdf",
            subtitle=tr("The same interval on the CDF", "同一区间在累计概率中的对应位置"),
        )
    st.caption(
        tr(
            f"Interval [{left:.3g}, {right:.3g}] · {outside} / {n} observations outside the view.",
            f"区间 [{left:.3g}, {right:.3g}] · 窗外 {outside} / {n} 个观测。",
        )
    )

    st.markdown(
        tr("#### One axis, three ways to look at the data", "#### 同一条数轴，三种观察方式")
    )
    box = go.Figure()
    jitter = np.random.default_rng(19).uniform(-0.10, 0.10, n)
    outliers = (sample < summary["lower_fence"]) | (sample > summary["upper_fence"])
    for mask, label, color in [
        (~outliers, tr("Sample points", "样本点"), COLORS["sample"]),
        (outliers, tr("Beyond fences", "围栏外观测"), COLORS["accent"]),
    ]:
        box.add_trace(
            go.Scatter(
                x=sample[mask],
                y=jitter[mask],
                mode="markers",
                marker=dict(size=5, color=color, opacity=0.6),
                name=label,
                hovertemplate=tr(
                    "Observation %{x:.3g}<extra></extra>", "观测值 %{x:.3g}<extra></extra>"
                ),
            )
        )
    sample_row, population_row = (1.4, 2.1) if previous is not None else (0.7, 1.4)
    box.add_trace(
        go.Box(
            q1=[summary["q1"]],
            median=[summary["median"]],
            q3=[summary["q3"]],
            lowerfence=[summary["lower_whisker"]],
            upperfence=[summary["upper_whisker"]],
            y=[sample_row],
            orientation="h",
            width=0.32,
            name=tr("Sample boxplot", "样本箱型图"),
            marker_color=COLORS["sample"],
            fillcolor="rgba(232,155,63,.18)",
            boxpoints=False,
            hoverinfo="skip",
            legendgroup="sample_summary",
        )
    )
    # Native box hover displays five rotated labels at once. Invisible hit targets
    # keep the box geometry intact and expose only the nearest statistic.
    box.add_trace(
        go.Scatter(
            x=[summary[k] for k in ("lower_whisker", "q1", "median", "q3", "upper_whisker")],
            y=[sample_row] * 5,
            mode="markers",
            showlegend=False,
            legendgroup="sample_summary",
            marker=dict(size=16, color="rgba(232,155,63,0)"),
            text=[
                tr("Lower whisker", "下须线"),
                "Q₁",
                tr("Median", "中位数"),
                "Q₃",
                tr("Upper whisker", "上须线"),
            ],
            hovertemplate="%{text}: %{x:.3g}<extra></extra>",
        )
    )
    if previous_summary:
        # A dashed range and median make the retained box distinguishable without color.
        saved = previous_summary
        box.add_trace(
            go.Scatter(
                x=[
                    saved["lower_whisker"],
                    saved["q1"],
                    saved["median"],
                    saved["q3"],
                    saved["upper_whisker"],
                ],
                y=[0.7] * 5,
                mode="lines+markers",
                name=tr("Saved sample summary", "保留样本摘要"),
                line=dict(color=COLORS["muted"], dash="dash", width=2),
                marker=dict(
                    size=[8, 12, 9, 12, 8],
                    symbol=["line-ns", "line-ns", "diamond-open", "line-ns", "line-ns"],
                ),
                text=[
                    tr("Lower whisker", "下须线"),
                    "Q₁",
                    tr("Median", "中位数"),
                    "Q₃",
                    tr("Upper whisker", "上须线"),
                ],
                hovertemplate="%{text}: %{x:.3g}<extra></extra>",
            )
        )
    tq = rv.ppf([0.25, 0.5, 0.75])
    box.add_trace(
        go.Scatter(
            x=tq,
            y=[population_row] * 3,
            mode="lines+markers+text",
            text=["Q₁", tr("Median", "中位数"), "Q₃"],
            textposition="top center",
            marker=dict(
                size=[9, 12, 9], color=COLORS["theory"], symbol=["line-ns", "diamond", "line-ns"]
            ),
            line=dict(color=COLORS["theory"], width=4),
            name=tr("Population quartiles", "总体四分位数"),
            hovertemplate="%{text}: %{x:.3g}<extra></extra>",
        )
    )
    box.add_vrect(
        x0=left, x1=right, fillcolor=COLORS["theory"], opacity=0.06, line_width=0, layer="below"
    )
    if show_fences:
        for label, val, anchor, shift in [
            (tr("Lower fence", "下围栏"), summary["lower_fence"], "left", 5),
            (tr("Upper fence", "上围栏"), summary["upper_fence"], "right", -5),
        ]:
            box.add_vline(x=val, line_dash="dot", line_color=COLORS["muted"])
            if lo <= val <= hi:
                box.add_annotation(
                    x=val,
                    xref="x",
                    y=0.98,
                    yref="paper",
                    text=label,
                    showarrow=False,
                    xanchor=anchor,
                    yanchor="top",
                    xshift=shift,
                    bgcolor="rgba(255,255,255,.92)",
                    borderpad=3,
                    font=dict(size=11, color=COLORS["muted"]),
                )
    rows = [(0, tr("Raw sample", "原始样本"))]
    if previous is not None:
        rows.append((0.7, tr("Saved sample", "保留样本")))
    rows.extend(
        [
            (sample_row, tr("Sample boxplot", "样本箱型图")),
            (population_row, tr("Population quantiles", "总体分位数")),
        ]
    )
    box.update_layout(
        height=390 if previous is not None else 320,
        hovermode="closest",
        xaxis_title=tr("x · shared scale", "同一尺度下的 x"),
        yaxis=dict(
            tickvals=[row[0] for row in rows],
            ticktext=[row[1] for row in rows],
            range=[-0.25, population_row + 0.5],
            showgrid=False,
        ),
        margin=dict(l=95),
    )
    box.update_xaxes(range=[lo, hi])
    chart(box, key="dist_box")
    st.caption(
        tr(
            f"{summary['outlier_count']} points lie beyond the fences; whiskers end at actual observations.",
            f"有 {summary['outlier_count']} 个围栏外观测；围栏是阈值，须线停在实际观测值。",
        )
    )
    download_figure(box, "distribution_boxplot")
    with st.expander(tr("Definitions & conventions", "数学定义与实验约定")):
        st.caption(
            tr(
                f"Selected interval: [{left:.3g}, {right:.3g}]. This view contains {p_hi - p_lo:.2%} of the population probability; {outside} / {n} observations lie outside it. Interval endpoints may be off-screen; change the horizontal view to inspect them. Statistics use the full sample, and histogram densities are normalized by the total sample size.",
                f"选中区间 [{left:.3g}, {right:.3g}]。当前视窗覆盖总体概率 {p_hi - p_lo:.2%}；窗外共有 {outside} / {n} 个样本。区间端点可能位于视窗外，可切换横轴视窗查看。所有统计量使用完整样本，直方图始终按总样本数归一化。",
            )
        )
        if previous is not None:
            previous_outside = int(np.sum((previous < lo) | (previous > hi)))
            st.caption(
                tr(
                    f"Saved sample: {previous_outside} / {len(previous)} observations outside this view. Both histograms use the same bins and their own full sample size.",
                    f"保留样本中有 {previous_outside} / {len(previous)} 个观测位于窗外。两组直方图共用分箱，各自按完整样本量归一化。",
                )
            )
        insight(
            tr("Fences are thresholds; whiskers end at observations", "围栏是阈值，须线是观测值"),
            tr(
                f"The fences are [{summary['lower_fence']:.3g}, {summary['upper_fence']:.3g}], while the whiskers end at [{summary['lower_whisker']:.3g}, {summary['upper_whisker']:.3g}]. There are {summary['outlier_count']} observations beyond the fences. Sample quartiles are also estimated from data, so both the box and the whiskers may move after resampling.",
                f"本批样本的围栏为 [{summary['lower_fence']:.3g}, {summary['upper_fence']:.3g}]；实际须线端点为 [{summary['lower_whisker']:.3g}, {summary['upper_whisker']:.3g}]。共有 {summary['outlier_count']} 个点落在围栏外。样本四分位数也由数据估计，所以重新抽样时，箱体和须线都可能移动。",
            ),
        )
        st.latex(r"P(a\leq X\leq b)=\int_a^b f(x)\,dx=F(b)-F(a)")
        st.latex(
            r"\widehat F_n(x)=\frac{1}{n}\sum_{i=1}^{n}\mathbf{1}_{X_i\leq x},\qquad \mathrm{IQR}=Q_3-Q_1"
        )
        st.latex(r"L=Q_1-1.5\,\mathrm{IQR},\qquad U=Q_3+1.5\,\mathrm{IQR}")
        st.write(
            tr(
                "Population quantiles come from the inverse theoretical CDF. Sample quantiles use NumPy’s linear interpolation convention. Whiskers end at the smallest and largest observed values within [L, U]. An observation beyond a fence is not automatically an error.",
                "总体分位数由理论 CDF 的反函数给出；样本分位数使用 NumPy 的 linear 插值约定。须线端点是 [L, U] 内最小与最大的实际观测值。围栏外观测并不自动意味着数据错误。",
            )
        )
        st.write(
            tr(
                "The alignment is Y = (X − median(X))/IQR(X). It applies to every distribution on this page, including those without a mean or variance. The PDF includes the Jacobian of this change of variables.",
                "对齐变换为 Y = (X − median(X))/IQR(X)，适用于本页所有分布，包括均值或方差不存在的分布。PDF 按变量变换的 Jacobian 修正。",
            )
        )
        st.caption(
            tr(
                f"Random seed: {seed}. Display options retain the same random sample; “Resample” changes the seed.",
                f"随机种子：{seed}。调整显示选项不改变这批随机样本；“重新抽样”才会更换种子。",
            )
        )
