"""Separate skewed shape, finite moments, kurtosis and asymptotic tail decay."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from i18n import tr
from physics import make_distribution, population_moments
from shared import COLORS, chart, download_figure, header, metric_row
from state import initialize_controls

NAMES = {
    "pareto": ("Pareto", "Pareto · 帕累托"),
    "lognormal": ("Lognormal", "Lognormal · 对数正态"),
    "student_t": ("Student t", "Student t · t 分布"),
    "cauchy": ("Cauchy", "Cauchy · 柯西"),
    "normal": ("Normal", "Normal · 正态"),
    "exponential": ("Exponential", "Exponential · 指数"),
}


def _fmt(value):
    return f"{value:.3g}" if np.isfinite(value) else tr("No finite value", "无有限值")


def _description(name, shape):
    if name == "pareto":
        return tr(
            f"The Pareto kth raw moment is finite only for α > k. With α = {shape:g}, the mean requires α > 1, variance α > 2, moment-based skewness α > 3, and kurtosis α > 4. The boundary cases also diverge.",
            f"Pareto 的 k 阶原点矩仅在 α > k 时有限。当前 α = {shape:g}：均值要求 α > 1，方差要求 α > 2，矩偏度要求 α > 3，峰度要求 α > 4。等号处也不收敛。",
        )
    if name == "student_t":
        return tr(
            f"The Student t kth absolute moment is finite only for ν > k. Currently ν = {shape:g}. Symmetry does not guarantee a defined moment-based skewness: skewness requires ν > 3, and kurtosis requires ν > 4.",
            f"Student t 的 k 阶绝对矩仅在 ν > k 时有限。当前 ν = {shape:g}。图形对称不保证矩偏度有定义：偏度仍要求 ν > 3，峰度要求 ν > 4。",
        )
    if name == "cauchy":
        return tr(
            "The Cauchy distribution is symmetric, but its mean does not exist, and its variance, standardized skewness, and kurtosis have no finite population values. Symmetry alone does not imply a skewness of zero.",
            "Cauchy 图形完全对称，但均值不存在，方差、标准化偏度与峰度也没有有限总体值。不能把“对称”直接翻译成“偏度 = 0”。",
        )
    if name == "lognormal":
        return tr(
            "Every positive integer moment of a lognormal distribution is finite, yet its tail decays more slowly than any exponential and is heavy-tailed. Heavy tails do not necessarily imply divergent moments.",
            "Lognormal 的所有正整数阶矩都有限，但它的尾部仍比任意指数衰减更慢，属于重尾分布。重尾并不等于矩一定发散。",
        )
    if name == "normal":
        return tr(
            "All normal-distribution moments exist: population skewness is 0, Pearson kurtosis is 3, and excess kurtosis is 0. Finite-sample estimates fluctuate around these values.",
            "Normal 的矩均存在：总体偏度为 0，Pearson 峰度为 3，超额峰度为 0。有限样本的估计值会在这些值附近波动。",
        )
    return tr(
        "All exponential-distribution moments exist: population skewness is 2 and Pearson kurtosis is 9. It is more skewed and produces more extreme observations than a normal distribution, but its tail is exponential, not a power law.",
        "Exponential 的矩均存在：总体偏度为 2，Pearson 峰度为 9。它比正态分布更偏、更有极端值，但具有指数尾，而不是幂律尾。",
    )


def render():
    initialize_controls(
        tail_excess=False,
        tail_logx=True,
        tail_alpha=3.0,
        tail_sigma=0.8,
        tail_nu=5.0,
    )
    labels = {name: tr(*pair) for name, pair in NAMES.items()}
    header(
        "02",
        tr("Skewness, kurtosis & tails", "偏度、峰度与尾部"),
        tr(
            "Shape, moments, and tail decay answer different questions. Explore their connections using a reproducible sample.",
            "形状、矩和尾部衰减各回答一个问题。用一次抽样，把它们放在一起观察。",
        ),
    )
    with st.container(border=True, key="controls_tails"):
        a, b, d = st.columns([1.4, 1.2, 0.8], vertical_alignment="bottom")
        with a:
            name = st.selectbox(
                tr("Distribution to explore", "研究分布"),
                list(NAMES),
                format_func=labels.get,
                key="tail_name",
            )
        with b:
            if name == "pareto":
                shape = st.slider(
                    tr("Tail exponent α", "尾指数 α"), 0.5, 8.0, step=0.1, key="tail_alpha"
                )
            elif name == "lognormal":
                shape = st.slider(
                    tr("Log-space standard deviation σ", "对数标准差 σ"),
                    0.2,
                    2.0,
                    step=0.1,
                    key="tail_sigma",
                )
            elif name == "student_t":
                shape = st.slider(
                    tr("Degrees of freedom ν", "自由度 ν"), 1.0, 20.0, step=0.5, key="tail_nu"
                )
            else:
                shape = 3.0
                st.caption(
                    tr(
                        "Standard parameters; plots below align the median and IQR.",
                        "使用标准参数；下图按中位数和 IQR 对齐。",
                    )
                )
        with d:
            if st.button(
                tr("↻ Resample", "↻ 重新抽样"),
                key="tail_resample",
                use_container_width=True,
                help=tr("Draw 4,000 new observations", "重新抽取 4,000 个观测值"),
            ):
                st.session_state["tail_seed"] = st.session_state.get("tail_seed", 1515) + 1
        with st.popover(
            tr("Display options", "显示选项"), icon=":material/tune:", key="display_tails"
        ):
            excess = st.toggle(
                tr("Show excess kurtosis", "显示超额峰度"),
                key="tail_excess",
                help=tr(
                    "Excess kurtosis = Pearson kurtosis − 3. The normal reference changes from 3 to 0.",
                    "超额峰度 = Pearson 峰度 − 3。正态基准从 3 变为 0。",
                ),
            )
            logarithmic_x = st.toggle(
                tr("Logarithmic tail x-axis", "尾部横轴使用对数"), key="tail_logx"
            )
    rv = make_distribution(name, shape)
    moments = population_moments(rv)
    seed = st.session_state.get("tail_seed", 1515)
    sample = rv.rvs(size=4000, random_state=np.random.default_rng(seed))
    k_name = "excess_kurtosis" if excess else "kurtosis"
    k_label = (
        tr("Excess kurtosis", "超额峰度") if excess else tr("Pearson kurtosis", "Pearson 峰度")
    )
    # Mid-sentence English form; "Pearson" is a proper noun and keeps its capital.
    k_phrase = "excess kurtosis" if excess else "Pearson kurtosis"
    theoretical_k = moments[k_name]
    sample_k = float(stats.kurtosis(sample, fisher=excess, bias=False))
    metric_row(
        [
            (
                tr("Population mean", "总体均值"),
                _fmt(moments["mean"]),
                tr("Existence is a population property", "存在性由分布决定"),
            ),
            (
                tr("Population variance", "总体方差"),
                _fmt(moments["variance"]),
                tr("A finite variance is needed for σ scaling", "方差有限才可按 σ 标准化"),
            ),
            (
                tr("Population skewness", "总体矩偏度"),
                _fmt(moments["skewness"]),
                tr("Standardized third central moment", "标准化三阶中心矩"),
            ),
            (
                tr(f"Population {k_phrase}", f"总体{k_label}"),
                _fmt(theoretical_k),
                tr(
                    "Distinguish sample estimates from population values",
                    "样本估计与总体定义需区分",
                ),
            ),
        ]
    )
    if not np.isfinite(theoretical_k):
        st.warning(
            tr(
                "No finite population kurtosis for these parameters; a finite sample estimate does not establish its existence.",
                "当前参数下没有有限的总体峰度；有限的样本估计不能证明总体峰度存在。",
            )
        )

    aligned = make_distribution(name, shape, align=True)
    normal = make_distribution("normal", align=True)
    shape_x = np.linspace(-3, 6, 700)
    pdf = go.Figure()
    pdf.add_trace(
        go.Scatter(
            x=shape_x,
            y=normal.pdf(shape_x),
            name=tr("Normal reference", "Normal 参照"),
            line=dict(color=COLORS["muted"], dash="dash", width=2),
        )
    )
    pdf.add_trace(
        go.Scatter(
            x=shape_x,
            y=aligned.pdf(shape_x),
            name=labels[name],
            line=dict(color=COLORS["theory"], width=3),
            fill="tozeroy",
            fillcolor="rgba(8,126,139,.08)",
        )
    )
    pdf.update_layout(
        title=tr("01 / Distribution shape", "01 / 主体形状"),
        height=340,
        xaxis_title="y = (x − median) / IQR",
        yaxis_title=tr("Transformed density", "变换后的概率密度"),
    )
    pdf.update_yaxes(rangemode="tozero")
    tail_distance = np.geomspace(0.1, 100, 500)
    median, q1, q3 = rv.ppf([0.5, 0.25, 0.75])
    threshold = median + tail_distance * (q3 - q1)
    survival = rv.sf(threshold)
    normal_sf = normal.sf(tail_distance)
    sf = go.Figure()
    sf.add_trace(
        go.Scatter(
            x=tail_distance,
            y=np.where(survival >= 1e-12, survival, np.nan),
            name=labels[name],
            line=dict(color=COLORS["theory"], width=3),
        )
    )
    sf.add_trace(
        go.Scatter(
            x=tail_distance,
            y=np.where(normal_sf >= 1e-12, normal_sf, np.nan),
            name=tr("Normal reference", "Normal 参照"),
            line=dict(color=COLORS["muted"], dash="dash", width=2),
        )
    )
    sf.update_layout(
        title=tr("02 / Right-tail probability", "02 / 右尾概率"),
        height=340,
        xaxis_title=tr("Distance from median / IQR", "距中位数的距离 / IQR"),
        yaxis_title="P(X > median + t · IQR)",
    )
    sf.update_yaxes(type="log", range=[-8, 0])
    sf.update_xaxes(type="log" if logarithmic_x else "linear")
    a, b = st.columns(2)
    with a:
        chart(
            pdf,
            key="tail_pdf",
            subtitle=tr(
                "Median 0, IQR 1; compare aligned shapes", "中位数 0，IQR 1；比较对齐后的形状"
            ),
        )
    with b:
        chart(
            sf,
            key="tail_sf",
            subtitle=tr(
                "Probability beyond the same threshold", "超出同一距离阈值，究竟有多罕见？"
            ),
        )
    outside_shape = float(aligned.cdf(-3) + aligned.sf(6))
    st.caption(
        tr(
            f"Same median and IQR · {outside_shape:.2%} of population probability lies outside the left plot. Off-screen tails are not zero.",
            f"相同中位数与 IQR · 左图窗外仍有 {outside_shape:.2%} 的总体概率；尾部离开视窗不代表概率为零。",
        )
    )

    st.markdown(
        tr(
            "#### How does sample kurtosis change as data accumulate?",
            "#### 同一个总体，样本峰度会怎样变化？",
        )
    )
    counts = np.unique(np.geomspace(20, len(sample), 80).astype(int))
    values = np.array(
        [stats.kurtosis(sample[:count], fisher=excess, bias=False) for count in counts]
    )
    convergence = go.Figure()
    convergence.add_trace(
        go.Scatter(
            x=counts,
            y=values,
            mode="lines",
            line=dict(color=COLORS["sample"], width=2.5),
            name=tr(f"Sample {k_phrase}", f"前 n 个样本的{k_label}"),
        )
    )
    if np.isfinite(theoretical_k):
        convergence.add_trace(
            go.Scatter(
                x=[counts[0], counts[-1]],
                y=[theoretical_k] * 2,
                mode="lines",
                name=tr(f"Population: {theoretical_k:.3g}", f"总体 {theoretical_k:.3g}"),
                line=dict(color=COLORS["theory"], dash="dash"),
            )
        )
    convergence.update_layout(
        height=310,
        xaxis_title=tr("Number of observations included, n", "同一批样本的前缀长度 n"),
        yaxis_title=k_label,
    )
    convergence.update_xaxes(type="log", hoverformat=",d")
    chart(convergence, key="tail_sample_kurtosis")
    left, right = st.columns([1, 2])
    with left:
        st.metric(tr(f"This sample: {k_phrase}", f"这批样本的{k_label}"), f"{sample_k:.3g}")
    with right:
        if np.isfinite(theoretical_k):
            st.write(
                tr(
                    "A few extreme observations can shift sample kurtosis substantially; resample to compare.",
                    "少量极端观测就可能明显改变样本峰度；可重新抽样比较。",
                )
            )
        else:
            st.write(
                tr(
                    "This sample returns a number, but there is no finite population kurtosis for it to estimate.",
                    "样本可以算出一个数值，但这里没有有限的总体峰度可供估计。",
                )
            )
    download_figure(convergence, "sample_kurtosis")
    with st.expander(
        tr(
            "Why are kurtosis and tail behavior different concepts?",
            "为什么峰度与 tail 不是同一个概念？",
        )
    ):
        st.write(_description(name, shape))
        st.caption(
            tr(
                f"Both distributions share the same median and IQR; no mean or variance is required. The distribution under study has {outside_shape:.2%} of its probability outside the left plot. The right y-axis ends at 10⁻⁸; a curve leaving the view does not mean its probability is zero. The shifted Pareto curve approaches its asymptotic slope only far into the tail.",
                f"两种分布使用相同中位数与 IQR；不要求均值或方差存在。左图视窗外仍有 {outside_shape:.2%} 的研究分布概率。右图纵轴最低显示 10⁻⁸，曲线离开视窗不表示尾概率为零。平移后的 Pareto 曲线在远尾才呈现其渐近斜率。",
            )
        )
        st.latex(
            r"\gamma_1=\mathbb E\!\left[\left(\frac{X-\mu}{\sigma}\right)^3\right],\qquad \beta_2=\mathbb E\!\left[\left(\frac{X-\mu}{\sigma}\right)^4\right],\qquad \gamma_2=\beta_2-3"
        )
        st.write(
            tr(
                "These definitions require the corresponding moments to exist and the variance to be nonzero. Kurtosis averages standardized fourth powers across the whole distribution, giving extreme deviations substantial weight. Tail type describes how probability decays as x grows; one kurtosis value cannot uniquely determine that asymptotic behavior.",
                "这些定义要求相应矩存在且方差非零。峰度汇总整个分布中的标准化四次偏差，远端观测会受到很大权重。尾部类型描述 x 越来越大时概率如何衰减；单个峰度值不能唯一确定这种渐近行为。",
            )
        )
        st.latex(r"f_{\rm Pareto}(x)=\alpha x^{-(\alpha+1)},\quad P(X>x)=x^{-\alpha},\quad x\geq1")
        st.write(
            tr(
                "The Pareto PDF has exponent −(α + 1), while the survival function has exponent −α. The tail comparison plots right-tail probability, not the PDF. Kurtosis uses the full sample; clipping the visible plot does not truncate the data.",
                "Pareto 的 PDF 幂指数为 −(α + 1)，survival function 的幂指数为 −α。比较图使用的是右尾概率，不是 PDF。峰度计算使用完整样本；曲线视窗的裁剪不会截断数据。",
            )
        )
        st.write(
            tr(
                "Sample skewness and kurtosis use SciPy’s bias=False correction. Correcting finite-sample bias does not make an undefined population moment exist.",
                "样本偏度与峰度采用 SciPy 的 bias=False 修正约定。修正有限样本估计的偏差不能弥补总体矩不存在的问题。",
            )
        )
        st.caption(
            tr(
                f"Random seed: {seed}. This experiment uses independent, identically distributed samples; it does not simulate microscopic dynamics such as avalanches.",
                f"随机种子：{seed}。当前实验只研究独立同分布的抽样，不模拟雪崩等微观动力学。",
            )
        )
