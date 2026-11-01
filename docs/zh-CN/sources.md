# 内容与来源

[English](../en/sources.md) · 简体中文 · [项目介绍](README.md)

## 教学背景

本项目基于 PHYS 515 的统计物理教学与概念讨论，将概率、抽样和微观态计数组织成可交互的学习实验。

- **概率与分布**：PDF/CDF、分位数、箱型图、median/IQR 对齐，以及偏度和峰度的含义。
- **尾部与极限**：survival function、Pareto 分布、矩的存在条件、大数定律与中心极限定理。
- **微观态与热力学**：微正则系综、Boltzmann 熵，以及二能级模型中熵、能量和温度的联系。

案例强调理论量与样本统计量的区别、不同图形表示之间的联系，以及结论成立的条件。界面说明、数值实现和图形导出围绕这些教学目标组织。

内容范围为概率、抽样、二能级熵与有限系统的热接触，并引入二能级热库的正则极限与温度响应；不包含理想气体与 Gibbs 修正。

## 定义与软件参考

- [SciPy kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html)：Pearson 与 Fisher 超额峰度的定义、样本偏差修正。
- [SciPy Pareto](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pareto.html)：Type-I Pareto、PDF/SF 与参数化。
- [NumPy quantile](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html)：分位数插值约定。
- [Streamlit Plotly charts](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart)：交互式图形展示。

## 关键推导

对 Type-I Pareto（xm=1），f(x)=α x^(-α-1)，x≥1，α>0。
其 k 阶原点矩积分为 α∫₁∞ x^(k-α-1) dx，仅 α>k 时有限。
SF 为 x^(-α)，与 PDF 的幂指数相差 1。

对 iid、有限均值 μ 与有限非零方差 σ² 的随机变量，
Zₙ=√n(X̄ₙ-μ)/σ 在 n→∞ 时依分布趋于标准正态。
大数定律只要求更弱的条件；Pareto 的 1<α≤2 区间说明有限均值和有限方差的区别。
Cauchy 的独立同分布样本算术均值仍是同一 Cauchy 分布。

对固定 q 的 N 个二能级位置，Ω=C(N,q)，S=kB ln Ω。
Stirling 近似给 S/(NkB)≈−x ln x−(1−x)ln(1−x)，x=q/N。
对 E=Nεx 求导得到 βε≈ln((1−x)/x)。这不为不同 q 层指定出现概率。

系统 A 与有限二能级热库 B 接触时，精确边缘分布为超几何分布。令 p = q/(N_A + N_B)，正则近似为二项分布：P(q_A) = C(N_A,q_A) p^q_A (1−p)^(N_A−q_A)。两者均值均为 N_A p；精确方差是在正则方差 N_A p(1−p) 上乘以 N_B/(N_A+N_B−1)。近似来自在热库平均能量附近展开其熵，保留全部 q_A = 0..N_A，包括有限热库所不允许的能量。

对与理想热库接触的独立、非简并二能级单元，令 θ = kB T/ε、p = exp(−1/θ)/(1+exp(−1/θ))。配分函数 Z = (1+exp(−1/θ))^N，U/(Nε) = p，C/(NkB) = p(1−p)/θ²。这些是精确的正则结果，不使用 Stirling 近似。T>0 时 Var(E) = kB T² C；T→0⁺ 时 U 与 C 趋于零。高温时 U/(Nε)→1/2，Var(E)/(Nε²)→1/4，而 C/(NkB)→0。二能级热容量的平滑峰值不表示相变。
