"""Independent sampling experiments: LLN, sample means, and the classical CLT."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from i18n import tr
from interactions import comparison_controls, sampling_walkthrough
from physics import clt_experiment, make_distribution, sample_histogram
from shared import COLORS, chart, control_panel, download_figure, header, metric_row
from state import initialize_controls

DISTRIBUTIONS = {
    "exponential": ("Exponential", "指数 · Exponential"),
    "uniform": ("Uniform", "均匀 · Uniform"),
    "normal": ("Normal", "正态 · Normal"),
    "pareto": ("Pareto · power-law tail", "Pareto · 幂律尾"),
    "cauchy": ("Cauchy · no finite mean", "Cauchy · 无有限均值"),
}


@st.cache_data(show_spinner=False, max_entries=30)
def _experiment(name, shape, n, repetitions, seed):
    return clt_experiment(name, shape, n, repetitions, seed, include_first_group=True)


def render():
    initialize_controls(
        clt_n=30,
        clt_repetitions=2000,
        clt_alpha=3.0,
        clt_view="means",
    )
    header(
        "03",
        tr("Large numbers & the CLT", "大数定律与 CLT"),
        tr(
            "Individual observations can be irregular. What happens when we average independent observations?",
            "一次观测可以很不规则。把独立观测取平均后，会发生什么？",
        ),
    )

    # Migrate old translated option values once; internal values are language-independent.
    legacy_distributions = {labels[1]: name for name, labels in DISTRIBUTIONS.items()}
    old_distribution = st.session_state.get("clt_distribution")
    if old_distribution in legacy_distributions:
        st.session_state["clt_distribution"] = legacy_distributions[old_distribution]
    legacy_views = {"样本均值": "means", "标准化均值": "standardized"}
    old_view = st.session_state.get("clt_view")
    if old_view in legacy_views:
        st.session_state["clt_view"] = legacy_views[old_view]
    distribution_labels = {name: tr(*labels) for name, labels in DISTRIBUTIONS.items()}

    with control_panel(
        "clt",
        lambda: (
            f"{distribution_labels[st.session_state.get('clt_distribution', 'exponential')]} · n = {st.session_state['clt_n']} · R = {st.session_state['clt_repetitions']:,}"
        ),
        seed_key="clt_draw",
        seed_start=0,
    ):
        c1, c2, c3 = st.columns([1.15, 1.35, 1.15], vertical_alignment="bottom")
        with c1:
            name = st.selectbox(
                tr("Parent distribution", "每次观测来自"),
                list(DISTRIBUTIONS),
                format_func=distribution_labels.get,
                key="clt_distribution",
            )
            shape = (
                st.slider(
                    tr("Pareto shape α", "Pareto 形状 α"), 0.5, 6.0, step=0.1, key="clt_alpha"
                )
                if name == "pareto"
                else 3.0
            )
        with c2:
            n = st.slider(
                tr("Observations per group n", "每组样本数 n"),
                1,
                500,
                key="clt_n",
                help=tr(
                    "Draw n independent observations per group, then calculate one mean.",
                    "每组先取 n 个独立观测，再计算一个均值。",
                ),
            )
        with c3:
            repetitions = st.select_slider(
                tr("Independent groups R", "独立重复组数 R"),
                [500, 1000, 2000, 3000, 5000],
                key="clt_repetitions",
            )
        tools_row = st.container(horizontal=True)
        with tools_row:
            if st.button(tr("Resample", "重新抽样"), key="clt_resample"):
                st.session_state["clt_draw"] = st.session_state.get("clt_draw", 0) + 1

    seed = 51503 + st.session_state.get("clt_draw", 0)
    result = _experiment(name, shape, n, repetitions, seed)
    rv = make_distribution(name, shape)
    mu, variance = result["population_mean"], result["population_variance"]
    finite = result["finite_variance"]
    means = np.asarray(result["means"])
    sem = np.sqrt(variance / n) if finite else None
    settings = dict(name=name, shape=shape, n=n, repetitions=repetitions, seed=seed)

    def describe(saved):
        parameter = f", α = {saved['shape']:g}" if saved["name"] == "pareto" else ""
        return f"{distribution_labels[saved['name']]}{parameter} · n = {saved['n']} · R = {saved['repetitions']:,} · seed = {saved['seed']}"

    with tools_row:
        with st.popover(
            tr("Display options", "显示选项"), icon=":material/tune:", key="display_clt"
        ):
            if not finite and st.session_state.get("clt_view") == "standardized":
                st.session_state["clt_view"] = "means"
            view_labels = {
                "means": tr("Sample means", "样本均值"),
                "standardized": tr("Standardized means", "标准化均值"),
            }
            mode = st.segmented_control(
                tr("Display scale", "观察尺度"),
                list(view_labels),
                format_func=view_labels.get,
                key="clt_view",
                required=True,
                disabled=not finite,
            )
            st.caption(tr(f"Random seed: {seed}", f"随机种子：{seed}"))
        reference = comparison_controls("clt", settings, describe, model_keys=("name", "shape"))
    previous_result = (
        _experiment(
            reference["name"],
            reference["shape"],
            reference["n"],
            reference["repetitions"],
            reference["seed"],
        )
        if reference
        else None
    )

    if not finite and name == "pareto" and shape > 1:
        st.warning(
            tr(
                "1 < α ≤ 2: the mean is finite, but variance is not. The law of large numbers applies; the classical √n-scaled CLT does not.",
                "1 < α ≤ 2：均值有限、方差不有限；大数定律仍可适用，经典 √n 标准化 CLT 不适用。",
            ),
            icon=":material/info:",
        )
    elif not finite and name == "cauchy":
        st.warning(
            tr(
                "Independent standard Cauchy averages remain standard Cauchy. No population mean or variance exists; increasing n does not concentrate the average.",
                "独立标准 Cauchy 的平均仍服从标准 Cauchy；总体均值、方差不存在，增加 n 不会让均值集中。",
            ),
            icon=":material/info:",
        )
    elif not finite:
        st.warning(
            tr(
                "For Pareto α ≤ 1, there is no finite population mean. The usual law of large numbers and finite-variance CLT do not apply here.",
                "当前 Pareto α ≤ 1，没有有限的总体均值。这不是通常大数定律或有限方差 CLT 的适用情形。",
            ),
            icon=":material/info:",
        )

    metric_row(
        [
            (
                tr("Population mean μ", "总体均值 μ"),
                f"{mu:.3g}" if np.isfinite(mu) else tr("No finite value", "无有限值"),
                tr("A population property, not a sample result", "分布性质，不由本次抽样决定"),
            ),
            (
                tr("Theoretical SE σ/√n", "理论标准误 σ/√n"),
                f"{sem:.3g}" if finite else tr("Not applicable", "不适用"),
                tr("Population SD of the sample mean", "样本均值的总体标准差"),
            ),
            (
                tr("Simulated means: SD", "模拟均值的标准差"),
                f"{np.std(means, ddof=1):.3g}",
                tr(f"From {repetitions:,} independent groups", f"来自 {repetitions:,} 组独立实验"),
            ),
        ]
    )

    standardized = finite and mode == "standardized"
    values = np.asarray(result["standardized"]) if standardized else means
    previous_values = (
        np.asarray(previous_result["standardized"] if standardized else previous_result["means"])
        if previous_result
        else None
    )
    x_label = "z = √n (x̄ − μ) / σ" if standardized else tr("Sample mean x̄", "样本均值 x̄")

    left, right = st.columns(2)
    with left:
        parent_lo, parent_hi = rv.ppf([0.005, 0.995])
        xs = rv.ppf(np.linspace(0.005, 0.995, 1000))
        fig = go.Figure(
            go.Scatter(
                x=xs,
                y=rv.pdf(xs),
                mode="lines",
                name=tr("Population PDF", "总体 PDF"),
                line=dict(color=COLORS["theory"], width=3),
                fill="tozeroy",
                fillcolor="rgba(8,126,139,.10)",
            )
        )
        fig.update_layout(
            height=330,
            xaxis_title=tr("Single observation x", "单次观测 x"),
            yaxis_title=tr("Probability density f(x)", "概率密度 f(x)"),
            showlegend=False,
        )
        fig.update_xaxes(range=[parent_lo, parent_hi])
        chart(
            fig,
            key="clt_population_chart",
            title=tr("01 / Single observations", "01 / 单次观测"),
            subtitle=tr("Population density of X", "原始观测 X 的总体概率密度"),
        )
        st.caption(
            tr(
                "The view covers the central 99% of population probability. The PDF is not renormalized to this window.",
                "显示总体中央 99% 的概率区间；PDF 未按显示区间重新归一化。",
            )
        )
    with right:
        bounds = None
        if previous_values is not None:
            current_bounds = np.quantile(values, [0.005, 0.995])
            saved_bounds = np.quantile(previous_values, [0.005, 0.995])
            bounds = (
                min(current_bounds[0], saved_bounds[0]),
                max(current_bounds[1], saved_bounds[1]),
            )
        centers, density, widths, lo, hi = sample_histogram(values, bounds=bounds)
        fig = go.Figure(
            go.Bar(
                x=centers,
                y=density,
                width=widths,
                name=tr("Simulation", "抽样结果"),
                marker_color=COLORS["sample"],
                opacity=0.72,
            )
        )
        if previous_values is not None:
            old_centers, old_density, _, _, _ = sample_histogram(previous_values, bounds=(lo, hi))
            fig.add_trace(
                go.Scatter(
                    x=old_centers,
                    y=old_density,
                    mode="lines",
                    name=tr("Saved means", "保留的均值"),
                    line=dict(color=COLORS["muted"], width=2, dash="dash", shape="hvh"),
                )
            )
        xs = np.linspace(lo, hi, 500)
        if finite:
            approx = stats.norm.pdf(xs) if standardized else stats.norm.pdf(xs, loc=mu, scale=sem)
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=approx,
                    mode="lines",
                    name=tr("Standard normal", "标准正态参照")
                    if standardized
                    else tr("Normal approximation", "正态近似"),
                    line=dict(color=COLORS["theory"], width=2.5, dash="dash"),
                )
            )
        elif name == "cauchy":
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=stats.cauchy.pdf(xs),
                    mode="lines",
                    name=tr("Exact: standard Cauchy", "精确：标准 Cauchy"),
                    line=dict(color=COLORS["theory"], width=2.5),
                )
            )
        fig.update_layout(
            height=330,
            barmode="overlay",
            bargap=0,
            xaxis_title=x_label,
            yaxis_title=tr("Probability density", "概率密度"),
        )
        if not standardized:
            fig.update_xaxes(range=[parent_lo, parent_hi])
        chart(
            fig,
            key="clt_means_chart",
            title=tr("02 / Sample means", "02 / 独立样本均值"),
            subtitle=tr(
                f"{repetitions:,} groups of {n} observations",
                f"{repetitions:,} 组实验，每组包含 {n} 个观测",
            ),
        )
        means_figure = fig
        view_lo, view_hi = (lo, hi) if standardized else (parent_lo, parent_hi)
        outside = int(np.sum((values < view_lo) | (values > view_hi)))
        unbinned = int(np.sum((values < lo) | (values > hi)))
        st.caption(
            tr(
                f"{outside:,} / {repetitions:,} means outside the view; {unbinned:,} outside the bins.",
                f"窗外 {outside:,} / {repetitions:,} 个均值；分箱外 {unbinned:,} 个。",
            )
        )

    if finite:
        explanation = tr(
            "Increasing n reduces the mean's theoretical fluctuations; the parent distribution stays the same.",
            "增大 n 会缩小均值的理论涨落；原始观测的分布保持不变。",
        )
        if standardized:
            explanation = tr(
                "Scaling by σ/√n lets us compare shapes; the normal curve is a finite-n approximation.",
                "按 σ/√n 缩放后更便于比较形状；正态曲线是有限 n 下的近似。",
            )
        if name == "pareto" and shape <= 3:
            explanation += tr(" Heavy tails can make convergence slow.", " 重尾可能使收敛较慢。")
        st.caption(explanation)

    sampling_walkthrough(result, n=n, repetitions=repetitions, seed=seed, model=(name, shape))

    with st.expander(
        tr("The law of large numbers: one sample path", "再看大数定律：一条样本路径"),
        expanded=False,
    ):
        draws = rv.rvs(size=5000, random_state=np.random.default_rng(seed + 907))
        ns = np.arange(1, len(draws) + 1)
        running = np.cumsum(draws) / ns
        fig = go.Figure(
            go.Scatter(
                x=ns,
                y=running,
                mode="lines",
                name=tr("Running sample mean", "累积样本均值"),
                line=dict(color=COLORS["sample"], width=1.8),
            )
        )
        if np.isfinite(mu):
            fig.add_trace(
                go.Scatter(
                    x=[1, len(draws)],
                    y=[mu, mu],
                    mode="lines",
                    name=tr("Population mean μ", "总体均值 μ"),
                    line=dict(color=COLORS["theory"], dash="dash"),
                )
            )
        fig.update_xaxes(hoverformat=",d")
        fig.update_layout(
            height=310,
            xaxis=dict(title=tr("Cumulative observations n", "累计观测数 n"), type="log"),
            yaxis_title=tr("Running mean x̄ₙ", "累积平均 x̄ₙ"),
        )
        chart(fig, key="clt_running_chart")
        st.caption(
            tr(
                "A separate, reproducible sequence of 5,000 independent observations. One path builds intuition, but does not prove convergence; it need not approach the mean monotonically.",
                "这是另一组固定种子的 5,000 次独立观测。单条路径用于形成直觉，不能作为收敛定理的证明；曲线也不必单调接近均值。",
            )
        )

    with st.expander(
        tr("Mathematics · three random quantities, two theorems", "数学说明 · 三种随机量，两个定理")
    ):
        scale_note = (
            tr(
                "Both panels share an x range so concentration is visible. ",
                "左右图使用相同 x 轴范围，便于观察均值的集中。",
            )
            if not standardized
            else tr("The standardized view uses its own z scale. ", "标准化后单独显示 z 轴尺度。")
        )
        bin_note = (
            tr(
                "Bins span both runs' central 99% intervals. ",
                "分箱覆盖两次实验各自的中央 99% 区间。",
            )
            if previous_values is not None
            else tr(
                "Bins cover the run's central 99% interval. ", "分箱覆盖本次实验的中央 99% 区间。"
            )
        )
        st.caption(
            tr(
                f"{scale_note}{outside:,} / {repetitions:,} means lie outside the view. {bin_note}{unbinned} tail values are unbinned; normalization uses all {repetitions:,} groups.",
                f"{scale_note}窗外 {outside:,} / {repetitions:,} 个均值。{bin_note}另有 {unbinned} 个尾端均值未入箱；分母始终保留全部 {repetitions:,} 组。",
            )
        )
        if previous_values is not None:
            old_outside = int(np.sum((previous_values < view_lo) | (previous_values > view_hi)))
            old_unbinned = int(np.sum((previous_values < lo) | (previous_values > hi)))
            st.caption(
                tr(
                    f"Saved run: {old_outside:,} means outside the view; {old_unbinned:,} outside the bins. Its density uses all {len(previous_values):,} groups. Standardization uses each run's own n.",
                    f"保留实验：窗外 {old_outside:,} 个均值，分箱外 {old_unbinned:,} 个；密度按全部 {len(previous_values):,} 组归一化。标准化时各自使用对应的 n。",
                )
            )

        st.write(
            tr(
                "The law of large numbers concerns convergence to the population mean; the CLT describes the scale and shape of fluctuations.",
                "大数定律关注样本均值趋近总体均值；中心极限定理描述涨落的尺度与形状。",
            )
        )
        st.latex(
            r"X_i\sim f,\qquad \bar X_n=\frac1n\sum_{i=1}^nX_i,\qquad Z_n=\frac{\sqrt n(\bar X_n-\mu)}{\sigma}"
        )
        st.markdown(
            tr(
                r"**Law of large numbers:** For the iid setting used here, $E|X|<\infty$ ensures that sample means converge to $\mu=E[X]$.",
                r"**大数定律：** 本页使用独立同分布情形；若 $E|X|<\infty$，样本均值趋近 $\mu=E[X]$。",
            )
        )
        st.latex(r"\bar X_n\xrightarrow{\mathrm{a.s.}}\mu")
        st.markdown(
            tr(
                r"**Classical CLT:** If also $0<\sigma^2=\mathrm{Var}(X)<\infty$, standardized means converge in distribution to a standard normal.",
                r"**经典 CLT：** 再要求 $0<\sigma^2=\mathrm{Var}(X)<\infty$，标准化均值依分布趋近标准正态。",
            )
        )
        st.latex(
            r"Z_n\xrightarrow{d}\mathcal N(0,1),\qquad \mathrm{Var}(\bar X_n)=\frac{\sigma^2}{n}"
        )
        st.markdown(
            tr(
                "The law of large numbers concerns the location of the mean; the CLT concerns the scale and shape of its fluctuations. Increasing n does not turn the original observations $X_i$ into normally distributed variables.",
                "大数定律讨论均值的位置，CLT 讨论其涨落的尺度与形状。原始观测 $X_i$ 的分布不会因为 n 增大而变成正态。",
            )
        )
    download_figure(means_figure, "clt_sample_means")
