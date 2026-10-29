"""Bilingual reference terms shared by the glossary and experiment footers."""

import unicodedata

import streamlit as st

from i18n import language, tr
from shared import header


def _term(
    id,
    en,
    zh,
    symbol,
    definition_en,
    definition_zh,
    related_lab,
    *,
    note_en="",
    note_zh="",
    aliases=(),
    formula="",
):
    return dict(
        id=id,
        en=en,
        zh=zh,
        symbol=symbol,
        definition_en=definition_en,
        definition_zh=definition_zh,
        related_lab=list(related_lab),
        note_en=note_en,
        note_zh=note_zh,
        aliases=list(aliases),
        formula=formula,
    )


TERMS = [
    _term(
        "joint_density",
        "Joint density",
        "联合密度",
        "p(x, y)",
        "A density describing two continuous variables together; integrating it over a region gives the probability of that region.",
        "描述两个连续变量的共同分布；在某个区域上积分，得到落入该区域的概率。",
        ["joint"],
        formula=r"P((X,Y)\in A)=\iint_A p(x,y)\,dx\,dy",
    ),
    _term(
        "marginal_density",
        "Marginal density",
        "边缘密度",
        "p_X(x)",
        "The density of one variable when the other variable is integrated out.",
        "对另一个变量积分后，得到单个变量的概率密度。",
        ["joint"],
        formula=r"p_X(x)=\int_{-\infty}^{\infty}p(x,y)\,dy",
    ),
    _term(
        "conditional_density",
        "Conditional density",
        "条件密度",
        "p(x | y₀)",
        "The normalized density of X given Y = y₀, defined where p_Y(y₀) is positive.",
        "给定 Y = y₀ 时 X 的归一化密度，在 p_Y(y₀) 大于零处定义。",
        ["joint"],
        note_en="For continuous Y, the exact event has probability zero. The conditional density is obtained from a density ratio, not by dividing by P(Y = y₀).",
        note_zh="连续变量 Y 取某个精确值的概率为零；条件密度通过密度之比定义，而不是除以 P(Y = y₀)。",
        formula=r"p(x\mid y_0)=p(x,y_0)/p_Y(y_0)",
    ),
    _term(
        "correlation",
        "Correlation coefficient",
        "相关系数",
        "ρ",
        "Covariance divided by the two standard deviations, measuring linear dependence when both variances are finite and positive.",
        "协方差除以两个标准差，用于衡量线性关联，要求两个方差均有限且大于零。",
        ["joint"],
        note_en="Zero correlation implies independence for jointly Gaussian variables, but not for general distributions.",
        note_zh="联合高斯变量不相关时相互独立；一般分布中不相关不代表独立。",
        formula=r"\rho=\mathrm{Cov}(X,Y)/(\sigma_X\sigma_Y)",
    ),
    _term(
        "pdf",
        "Probability density function",
        "概率密度函数",
        "f(x)",
        "For a continuous random variable, probability over an interval is the area under its density curve.",
        "对连续随机变量，区间内的概率等于概率密度曲线下的面积。",
        ["distributions", "tails", "clt"],
        note_en="A density value is not a point probability and can exceed 1. Its units are the inverse of the variable's units.",
        note_zh="密度的高度不是单点概率，可以大于 1；其单位是随机变量单位的倒数。",
        aliases=["PDF", "density", "密度"],
        formula=r"P(a\le X\le b)=\int_a^b f(x)\,dx",
    ),
    _term(
        "cdf",
        "Cumulative distribution function",
        "累积分布函数",
        "F(x)",
        "The probability that a random variable is at most x. A CDF is nondecreasing and takes values between 0 and 1.",
        "随机变量不超过 x 的概率。CDF 单调不减，取值在 0 与 1 之间。",
        ["distributions"],
        note_en="The empirical CDF counts the fraction of observations at or below x and is a step function.",
        note_zh="经验 CDF 统计样本中不超过 x 的观测比例，是阶梯函数。",
        aliases=["CDF", "ECDF", "cumulative", "经验分布"],
        formula=r"F(x)=P(X\le x),\qquad \widehat F_n(x)=\frac1n\sum_{i=1}^n\mathbf 1_{X_i\le x}",
    ),
    _term(
        "survival",
        "Survival function",
        "生存函数／右尾概率",
        "Sₓ(x)",
        "The probability of exceeding a threshold x. It makes rare events in the right tail easier to compare.",
        "随机变量超过阈值 x 的概率，适合比较右尾中的稀有事件。",
        ["distributions", "tails"],
        note_en="For Pareto I with scale 1, the survival exponent is −α, while the PDF exponent is −(α+1). Sₓ here is not thermodynamic entropy.",
        note_zh="尺度为 1 的 Pareto I，其生存函数幂指数为 −α，PDF 幂指数则为 −(α+1)。这里的 Sₓ 不是热力学熵。",
        aliases=["SF", "tail probability", "尾概率", "survival"],
        formula=r"S_X(x)=P(X>x)=1-F(x)",
    ),
    _term(
        "quantile",
        "Quantile",
        "分位数",
        "Qₚ",
        "A threshold associated with cumulative probability p. Quartiles use p = 0.25, 0.50 and 0.75; the middle one is the median.",
        "对应累计概率 p 的阈值。四分位数使用 p = 0.25、0.50、0.75，其中第二四分位数是中位数。",
        ["distributions"],
        note_en="Population quantiles come from a distribution. Sample quantiles are estimated from data; this app uses linear interpolation.",
        note_zh="总体分位数由分布定义；样本分位数由数据估计，本应用使用 linear 插值约定。",
        aliases=["percentile", "quartile", "median", "Q1", "Q2", "Q3", "中位数", "四分位数"],
        formula=r"Q_p=\inf\{x:F(x)\ge p\}",
    ),
    _term(
        "iqr",
        "Interquartile range",
        "四分位距",
        "IQR",
        "The distance between the third and first quartiles, describing the spread of the middle half of a distribution or sample.",
        "第三四分位数与第一四分位数之差，描述分布或样本中间一半的离散程度。",
        ["distributions", "tails"],
        note_en="Median/IQR alignment is not mean/standard-deviation standardization; it still works for a Cauchy distribution.",
        note_zh="按中位数与 IQR 对齐，不等于按均值与标准差标准化；前者也适用于 Cauchy 分布。",
        aliases=["spread", "四分位间距"],
        formula=r"\mathrm{IQR}=Q_3-Q_1",
    ),
    _term(
        "fence",
        "Tukey fence",
        "箱型图围栏",
        "L, U",
        "Thresholds computed from the quartiles to flag observations far from the central box, using the 1.5 IQR convention here.",
        "根据四分位数计算的阈值，用于标记偏离中央箱体较远的观测；这里采用 1.5 IQR 约定。",
        ["distributions"],
        note_en="A fence need not coincide with an observed value. A point outside it is not automatically a measurement error.",
        note_zh="围栏不一定落在实际观测值上；围栏外的点也不自动等于测量错误。",
        aliases=["fences", "outlier", "离群值", "箱线图"],
        formula=r"L=Q_1-1.5\,\mathrm{IQR},\qquad U=Q_3+1.5\,\mathrm{IQR}",
    ),
    _term(
        "whisker",
        "Whisker",
        "箱型图须线",
        "",
        "Under this app's Tukey convention, the whiskers end at the smallest and largest actual observations within the fences.",
        "在本应用的 Tukey 箱型图约定下，须线终点是围栏内最小和最大的实际观测值。",
        ["distributions"],
        note_en="Whisker endpoints differ from the fence thresholds. Both the sample quartiles and the whiskers can change after resampling.",
        note_zh="须线终点与围栏阈值不同。重新抽样后，样本四分位数和须线都可能变化。",
        aliases=["whiskers", "boxplot", "box plot", "箱线图", "箱型图"],
    ),
    _term(
        "population",
        "Population / probability model",
        "总体／概率模型",
        "",
        "The underlying probability distribution that describes possible observations. Its parameters and moments are properties of the model.",
        "描述所有可能观测的基础概率分布；总体参数和总体矩是模型本身的性质。",
        ["distributions", "tails", "clt"],
        note_en="A finite sample can produce a numerical statistic even when the corresponding finite population moment does not exist.",
        note_zh="即使相应的有限总体矩不存在，有限样本也可能算出一个数值统计量。",
        aliases=["theoretical", "理论", "总体分布"],
    ),
    _term(
        "sample",
        "Sample",
        "样本",
        "X₁, …, Xₙ",
        "A finite collection of observations drawn from a probability model. Sample statistics vary across repeated draws.",
        "从概率模型获得的一组有限观测；样本统计量会随重复抽样而变化。",
        ["distributions", "tails", "clt"],
        note_en="The sample size n counts observations in one group; the CLT experiment's R counts independently repeated groups.",
        note_zh="样本量 n 是每组观测的数量；CLT 实验中的 R 是独立重复的组数。",
        aliases=["sampling", "observation", "resample", "抽样", "观测", "样本量"],
    ),
    _term(
        "mean",
        "Mean / expectation",
        "均值／期望",
        "μ, X̄ₙ",
        "The population mean is the probability-weighted average when the expectation exists. The sample mean is the arithmetic average of observed values.",
        "总体均值是在期望存在时按概率加权的平均；样本均值是观测数据的算术平均。",
        ["distributions", "tails", "clt"],
        note_en="A symmetric Cauchy distribution has no population mean, although any finite set of finite observations has a sample mean.",
        note_zh="对称的 Cauchy 分布没有总体均值，但有限个有限观测仍可计算样本均值。",
        aliases=["mu", "expectation", "average", "sample mean", "平均", "样本均值"],
        formula=r"\mu=\mathbb E[X],\qquad \bar X_n=\frac1n\sum_{i=1}^nX_i",
    ),
    _term(
        "variance",
        "Variance",
        "方差",
        "σ²",
        "The expected squared deviation from the population mean, when defined. Its square root is the standard deviation.",
        "相对于总体均值的平方偏差的期望，在该量有定义时衡量涨落；其平方根是标准差。",
        ["distributions", "tails", "clt"],
        note_en="A finite mean does not guarantee finite variance. Pareto I has a finite mean for α>1, but finite variance requires α>2.",
        note_zh="有限均值不保证有限方差。Pareto I 在 α>1 时均值有限，但方差有限需要 α>2。",
        aliases=["sigma", "standard deviation", "std", "标准差"],
        formula=r"\sigma^2=\mathbb E[(X-\mu)^2]",
    ),
    _term(
        "skewness",
        "Skewness",
        "偏度",
        "γ₁",
        "The standardized third central moment, when finite and the variance is nonzero. It measures signed asymmetry through cubed deviations.",
        "在相应矩有限且方差非零时，偏度是标准化三阶中心矩，通过三次偏差反映有方向的不对称。",
        ["tails"],
        note_en="Symmetry does not guarantee that moment-based skewness exists: Cauchy is symmetric but has undefined skewness.",
        note_zh="对称不保证矩偏度存在：Cauchy 分布对称，但偏度没有定义。",
        aliases=["skew", "asymmetry", "偏态", "不对称"],
        formula=r"\gamma_1=\mathbb E\!\left[\left(\frac{X-\mu}{\sigma}\right)^3\right]",
    ),
    _term(
        "kurtosis",
        "Pearson kurtosis",
        "Pearson 峰度",
        "β₂",
        "The standardized fourth central moment. A finite value requires a finite fourth moment and nonzero variance; a normal distribution has kurtosis 3.",
        "标准化四阶中心矩；有限峰度需要有限四阶矩及非零方差，正态分布的峰度为 3。",
        ["tails"],
        note_en="Kurtosis is not simply peak height and does not uniquely determine the asymptotic tail type. Far-out observations receive a fourth-power weight.",
        note_zh="峰度不能简单理解为峰的高度，也不能唯一决定渐近尾部类型；远端观测会受到四次方权重。",
        aliases=["fourth moment", "峰态"],
        formula=r"\beta_2=\mathbb E\!\left[\left(\frac{X-\mu}{\sigma}\right)^4\right]",
    ),
    _term(
        "excess_kurtosis",
        "Excess kurtosis",
        "超额峰度",
        "γ₂",
        "Pearson kurtosis minus 3, so that the normal-distribution reference value becomes zero.",
        "Pearson 峰度减去 3，使正态分布的参照值变为零。",
        ["tails"],
        note_en="Always check the convention when comparing values. The app's toggle changes the convention, not the sampled observations.",
        note_zh="比较数值前先核对约定。应用中的切换改变的是峰度约定，不是抽样数据。",
        aliases=["Fisher", "excess", "Fisher kurtosis"],
        formula=r"\gamma_2=\beta_2-3",
    ),
    _term(
        "moment",
        "Moment",
        "矩",
        "E[Xᵏ]",
        "An expectation of a power of a random variable or its deviation from the mean. Moments summarize different aspects of a distribution only when they exist.",
        "随机变量的幂，或相对于均值的偏差的幂的期望；只有在存在时，矩才能概括分布的相应性质。",
        ["tails", "clt"],
        note_en="For Pareto I, the k-th raw moment is finite exactly when α>k. Equality is also divergent.",
        note_zh="对 Pareto I，k 阶原点矩恰在 α>k 时有限；等号处也发散。",
        aliases=["raw moment", "central moment", "矩存在", "原点矩", "中心矩"],
        formula=r"\mathbb E[X^k],\qquad \mathbb E[(X-\mu)^k]",
    ),
    _term(
        "heavy_tail",
        "Heavy tail",
        "重尾",
        "",
        "For the right-tail examples here, a heavy tail has no finite positive exponential moment: E[exp(t X₊)] is infinite for every t>0, where X₊=max(X,0).",
        "对这里讨论的右尾，重尾指不存在有限的正指数矩：对任意 t>0，E[exp(t X₊)] 都发散，其中 X₊=max(X,0)。",
        ["tails"],
        note_en="Pareto and lognormal are examples. Lognormal still has all positive integer moments finite; a large kurtosis alone does not establish heavy-tailed decay.",
        note_zh="Pareto 和对数正态是例子；对数正态的所有正整数阶矩仍然有限。仅凭较大的峰度不能断定渐近衰减属于重尾。",
        aliases=["tail", "power law", "Pareto", "lognormal", "幂律", "长尾", "对数正态"],
    ),
    _term(
        "iid",
        "Independent and identically distributed",
        "独立同分布",
        "i.i.d.",
        "Observations are mutually independent and all follow the same probability distribution.",
        "观测彼此独立，并且都服从同一个概率分布。",
        ["clt"],
        note_en="Independence concerns relationships between observations; identical distribution concerns their individual probability laws.",
        note_zh="独立描述观测之间的关系；同分布描述每个观测各自的概率规律。",
        aliases=["iid", "i.i.d.", "independence", "independent", "独立"],
    ),
    _term(
        "lln",
        "Law of large numbers",
        "大数定律",
        "LLN",
        "In the iid setting used here, E|X|<∞ ensures that the sample mean converges to the population mean as the sample size grows.",
        "在本应用的独立同分布情形中，E|X|<∞ 保证样本量增大时，样本均值收敛到总体均值。",
        ["clt"],
        note_en="This concerns the location of the sample mean, not a claim that the original observations become Gaussian.",
        note_zh="它描述样本均值的位置，并不是说原始观测的分布变成高斯。",
        aliases=["LLN", "strong law", "弱大数定律", "强大数定律"],
        formula=r"\bar X_n\xrightarrow{\mathrm{a.s.}}\mu",
    ),
    _term(
        "clt",
        "Central limit theorem",
        "中心极限定理",
        "CLT",
        "For iid observations with finite mean and finite nonzero variance, the standardized sample mean converges in distribution to a standard normal.",
        "对均值有限、方差有限且非零的独立同分布观测，标准化样本均值依分布趋于标准正态。",
        ["clt"],
        note_en="This is the classical finite-variance CLT. At finite n the approximation may be poor, especially for heavy-tailed parents.",
        note_zh="这里指经典的有限方差 CLT；有限 n 时近似可能较差，重尾总体尤其可能收敛缓慢。",
        aliases=["CLT", "Gaussian", "normal limit", "高斯极限", "标准化"],
        formula=r"\frac{\sqrt n(\bar X_n-\mu)}{\sigma}\xrightarrow{d}\mathcal N(0,1)",
    ),
    _term(
        "standard_error",
        "Standard error of the mean",
        "均值的标准误",
        "SE",
        "The standard deviation of the sampling distribution of the sample mean. For iid observations with finite variance, it equals σ/√n.",
        "样本均值的抽样分布的标准差。独立同分布且方差有限时，它等于 σ/√n。",
        ["clt"],
        note_en="Standard deviation describes individual observations; standard error describes the uncertainty of their average across repeated samples.",
        note_zh="标准差描述单个观测的离散；标准误描述重复抽样时平均值的涨落。",
        aliases=["SE", "SEM", "standard error", "标准误差"],
        formula=r"\mathrm{SD}(\bar X_n)=\frac{\sigma}{\sqrt n}",
    ),
    _term(
        "microstate",
        "Microstate",
        "微观态",
        "{nᵢ}",
        "A complete microscopic configuration. In the two-level experiment, it specifies whether each labeled unit is in its ground or excited state.",
        "系统完整的微观配置；在二能级实验中，它指定每个有标签单元处于基态还是激发态。",
        ["entropy"],
        note_en="Rearranging the excited units changes the microstate while keeping total energy fixed if q stays the same.",
        note_zh="当 q 不变时，重新排列激发单元会改变微观态，但保持总能量不变。",
        aliases=["configuration", "排列", "微观配置"],
    ),
    _term(
        "macrostate",
        "Macrostate",
        "宏观态",
        "E, N",
        "A description using macroscopic constraints. In this model, specifying N and E=qε leaves many microscopic arrangements possible.",
        "由宏观约束描述的状态；在本模型中，给定 N 和 E=qε 后，仍可能有很多微观排列。",
        ["entropy"],
        note_en="A change in q changes the total energy, so different points on the entropy curve represent different macroscopic constraints.",
        note_zh="改变 q 就改变总能量，因此熵曲线上不同点对应不同的宏观约束。",
        aliases=["macroscopic", "constraint", "宏观约束"],
    ),
    _term(
        "multiplicity",
        "Multiplicity",
        "微观态数／多重度",
        "Ω",
        "The number of microstates compatible with the specified macrostate. For N distinguishable two-level units with q excitations, it is C(N,q).",
        "满足指定宏观态的微观态数量；对 N 个可区分二能级单元、q 个激发，数量是 C(N,q)。",
        ["entropy"],
        note_en="This is a count, not a probability distribution over different energies. The fixed-q ensemble samples only that energy layer.",
        note_zh="这是计数，不是不同能量之间的概率分布；固定 q 的系综只在该能量层内抽样。",
        aliases=["omega", "state counting", "combinatorial", "组合数", "态计数"],
        formula=r"\Omega(N,q)=\binom Nq",
    ),
    _term(
        "entropy",
        "Boltzmann entropy",
        "玻尔兹曼熵",
        "S",
        "In the counting model used here, entropy is Boltzmann's constant times the logarithm of the number of compatible microstates.",
        "在这里的计数模型中，熵等于玻尔兹曼常数乘以可达微观态数的对数。",
        ["entropy"],
        note_en="Taking a logarithm turns multiplication of independent state counts into addition of entropies. S/kB is dimensionless.",
        note_zh="对独立系统取对数，可以把微观态数量的乘法转化为熵的加法；S/kB 无量纲。",
        aliases=["Boltzmann", "kB", "k_B", "熵", "玻尔兹曼"],
        formula=r"S=k_B\ln\Omega",
    ),
    _term(
        "microcanonical",
        "Microcanonical ensemble",
        "微正则系综",
        "E, V, N fixed",
        "An equilibrium ensemble with fixed energy and other specified macroscopic constraints, assigning equal weight to accessible microstates.",
        "固定能量及其他指定宏观约束的平衡系综，对可达微观态赋予相同权重。",
        ["entropy"],
        note_en="In the discrete two-level model, fixed N and E mean fixed q. Equal weight applies within this q layer, not across every q value.",
        note_zh="在离散二能级模型中，固定 N、E 就是固定 q；等权重作用于同一 q 层，而不是所有 q 值。",
        aliases=["ensemble", "isolated", "系综", "孤立系统"],
        formula=r"P(\text{microstate}\mid N,q)=\frac1{\Omega(N,q)}",
    ),
    _term(
        "excitation",
        "Excitation / energy gap",
        "激发／能隙",
        "q, ε",
        "A unit is excited when it occupies the upper level ε instead of the ground level 0. With q excited units, the total energy is qε.",
        "单元从基态 0 占据上能级 ε 时处于激发态；q 个单元被激发时，总能量是 qε。",
        ["entropy"],
        note_en="The energy gap ε is positive. The displayed dot positions are labels, not a model of spatial interactions.",
        note_zh="能隙 ε 为正；图中的圆点位置用于区分标签，不表示空间相互作用。",
        aliases=["epsilon", "energy gap", "two-level", "occupancy", "激发态", "基态", "二能级"],
        formula=r"n_i\in\{0,1\},\qquad q=\sum_i n_i,\qquad E=q\epsilon",
    ),
    _term(
        "inverse_temperature",
        "Inverse temperature",
        "逆温度",
        "β",
        "The quantity β=1/(kBT), with units of inverse energy. It is the energy derivative of the dimensionless entropy S/kB.",
        "β=1/(kBT)，单位为能量的倒数；它等于无量纲熵 S/kB 对能量的导数。",
        ["entropy"],
        note_en="The app plots dimensionless βε using a large-N approximation. β=0 is an infinite-temperature limit, not zero temperature.",
        note_zh="应用画出无量纲 βε，并采用大 N 近似；β=0 对应无限温极限，而不是零温。",
        aliases=["beta", "temperature", "negative temperature", "温度", "负温度"],
        formula=r"\beta=\frac1{k_BT}=\frac1{k_B}\left(\frac{\partial S}{\partial E}\right)_N,\qquad \beta\epsilon\simeq\ln\frac{N-q}{q}",
    ),
    _term(
        "population_inversion",
        "Population inversion",
        "粒子数反转",
        "q/N > 1/2",
        "In this two-level model, more units occupy the excited level than the ground level. Entropy decreases as energy rises along this branch.",
        "在本二能级模型中，激发态单元多于基态单元；沿此分支增加能量时，熵反而下降。",
        ["entropy"],
        note_en="This gives β<0 in the large-N description. Such equilibrium negative-temperature states require a bounded-above energy spectrum.",
        note_zh="在大 N 描述中，这对应 β<0；这样的平衡负温度态要求能谱有上界。",
        aliases=["inversion", "negative beta", "负温", "能谱上界"],
    ),
]


RELATED_IDS = {
    "joint": ["joint_density", "marginal_density", "conditional_density", "correlation"],
    "distributions": ["pdf", "cdf", "quantile", "iqr", "fence", "whisker"],
    "tails": ["survival", "skewness", "kurtosis", "excess_kurtosis", "moment", "heavy_tail"],
    "clt": ["iid", "sample", "mean", "lln", "clt", "standard_error"],
    "entropy": [
        "microstate",
        "multiplicity",
        "entropy",
        "microcanonical",
        "inverse_temperature",
        "population_inversion",
    ],
}

_BY_ID = {term["id"]: term for term in TERMS}
_CATEGORIES = {
    "all": ("All topics", "全部主题"),
    "joint": ("Joint & conditional probability", "联合与条件概率"),
    "distributions": ("Distributions & boxplots", "分布与箱型图"),
    "tails": ("Moments & tails", "矩与尾部"),
    "clt": ("Sampling & limit theorems", "抽样与极限定理"),
    "entropy": ("Microstates & entropy", "微观态与熵"),
}


def _normalize(value):
    return unicodedata.normalize("NFKC", value).casefold().strip()


def search_terms(query="", category="all"):
    """Search either language, notation and common abbreviations without UI state."""
    tokens = _normalize(query).split()
    results = []
    for term in TERMS:
        if category != "all" and category not in term["related_lab"]:
            continue
        text = (
            " ".join(
                str(term.get(key, ""))
                for key in (
                    "en",
                    "zh",
                    "symbol",
                    "definition_en",
                    "definition_zh",
                    "note_en",
                    "note_zh",
                )
            )
            + " "
            + " ".join(term["aliases"])
        )
        searchable = _normalize(text)
        if all(token in searchable for token in tokens):
            results.append(term)
    return results


def _title(term):
    label = f"{term['en']} · {term['zh']}"
    return f"{label}  —  {term['symbol']}" if term["symbol"] else label


def _reset_filters():
    st.session_state["glossary_search"] = ""
    st.session_state["glossary_category"] = "all"


def render():
    header(
        "reference",
        tr("Glossary", "术语表"),
        tr(
            "A bilingual reference for the experiments. Search by term, abbreviation or symbol; definitions follow your selected language.",
            "实验中的中英文术语速查。可搜索名称、缩写或符号；定义随所选语言切换。",
        ),
    )
    left, right = st.columns([2, 1])
    with left:
        query = st.text_input(
            tr("Find a term", "查找术语"),
            key="glossary_search",
            placeholder=tr("e.g. kurtosis, IQR, β, 峰度", "例如 kurtosis、IQR、β、峰度"),
        )
    with right:
        category_labels = {key: tr(*names) for key, names in _CATEGORIES.items()}
        category = st.selectbox(
            tr("Topic", "主题"),
            options=list(_CATEGORIES),
            format_func=category_labels.get,
            key="glossary_category",
        )
    results = search_terms(query, category)
    st.caption(
        tr(
            f"{len(results)} of {len(TERMS)} terms",
            f"共 {len(TERMS)} 个术语，当前显示 {len(results)} 个",
        )
    )
    if query or category != "all":
        st.button(tr("Clear filters", "清除筛选"), key="glossary_reset", on_click=_reset_filters)
    if not results:
        st.info(
            tr(
                "No matching terms. Try an English or Chinese keyword, an abbreviation, or another topic.",
                "没有找到匹配的术语。可以尝试中英文关键词、缩写，或切换主题。",
            )
        )
        return
    lang = language()
    for term in results:
        with st.expander(_title(term)):
            st.write(term[f"definition_{lang}"])
            if term["formula"]:
                st.latex(term["formula"])
            if term[f"note_{lang}"]:
                st.markdown(f"**{tr('Keep in mind', '注意区分')}** · {term[f'note_{lang}']}")


def render_related(lab_id):
    """A compact, intentionally closed reference at the end of each experiment."""
    ids = RELATED_IDS.get(lab_id, ())
    if not ids:
        return
    with st.expander(tr("Key terms · English / 中文", "相关术语速查 · English / 中文")):
        lang = language()
        for term_id in ids:
            term = _BY_ID[term_id]
            st.markdown(f"**{term['en']} · {term['zh']}**")
            st.write(term[f"definition_{lang}"])
        st.caption(
            tr(
                "Open Glossary in the sidebar for formulas, distinctions and bilingual search.",
                "在侧栏打开完整术语表，可查看公式、易混点并进行中英文搜索。",
            )
        )
