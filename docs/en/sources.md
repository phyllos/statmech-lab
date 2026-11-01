# Content and sources

English · [简体中文](../zh-CN/sources.md) · [Project overview](../../README.md)

## Teaching background

The project builds on PHYS 515 statistical physics teaching and conceptual discussions, organizing probability, sampling and microstate counting into interactive experiments.

- **Probability and distributions**: PDFs/CDFs, quantiles, boxplots, median/IQR alignment, and the meaning of skewness and kurtosis.
- **Tails and limits**: survival functions, Pareto distributions, conditions for moment existence, the law of large numbers and the central limit theorem.
- **Microstates and thermodynamics**: the microcanonical ensemble, Boltzmann entropy, and the relationship between entropy, energy and temperature in a two-level model.

The examples distinguish population quantities from sample statistics, connect different graphical representations and state the assumptions behind each conclusion. Interface explanations, numerical models and figure exports follow these teaching goals.

The scope covers probability, sampling, two-level entropy and finite-system thermal contact. It also introduces the canonical limit and temperature response of two-level units; ideal gases and the Gibbs correction are not included.

## Definitions and software references

- [SciPy kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html): Pearson and Fisher excess kurtosis definitions and sample bias correction.
- [SciPy Pareto](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pareto.html): Type-I Pareto, PDF/SF and parameterization.
- [NumPy quantile](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html): quantile interpolation conventions.
- [Streamlit Plotly charts](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart): interactive chart display.

## Key derivations

For Type-I Pareto with xm=1, f(x)=α x^(-α-1), x≥1 and α>0.
Its kth raw moment is α∫₁∞ x^(k-α-1) dx, which is finite only when α>k.
The survival function is x^(-α), with a power-law exponent differing from the PDF's by 1.

For iid variables with finite mean μ and finite, nonzero variance σ²,
Zₙ=√n(X̄ₙ-μ)/σ converges in distribution to the standard normal as n→∞.
The law of large numbers requires weaker conditions; Pareto with 1<α≤2 illustrates the distinction between a finite mean and finite variance.
The arithmetic mean of iid Cauchy samples retains the same Cauchy distribution.

For N two-level sites with fixed q, Ω=C(N,q) and S=kB ln Ω.
Stirling's approximation gives S/(NkB)≈−x ln x−(1−x)ln(1−x), where x=q/N.
Differentiating with respect to E=Nεx gives βε≈ln((1−x)/x). This does not assign probabilities to different q layers.

For a system A coupled to a finite two-level reservoir B, the exact marginal is hypergeometric. With p = q/(N_A + N_B), its canonical approximation is binomial: P(q_A) = C(N_A,q_A) p^q_A (1−p)^(N_A−q_A). Both means are N_A p; the exact variance is the canonical variance N_A p(1−p) multiplied by N_B/(N_A+N_B−1). The approximation follows from expanding the reservoir entropy around its mean energy. It keeps all q_A = 0..N_A, including energies excluded by a finite reservoir.

For independent, nondegenerate two-level units coupled to an ideal reservoir, θ = kB T/ε and p = exp(−1/θ)/(1+exp(−1/θ)). The partition function is Z = (1+exp(−1/θ))^N, U/(Nε) = p and C/(NkB) = p(1−p)/θ². These are exact canonical results, without Stirling's approximation. For T>0, Var(E) = kB T² C. At T→0⁺, U and C vanish; at high temperature, U/(Nε)→1/2 and Var(E)/(Nε²)→1/4 while C/(NkB)→0. The smooth two-level heat-capacity peak does not indicate a phase transition.
