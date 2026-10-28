# Content and sources

English · [简体中文](../zh-CN/sources.md) · [Project overview](../../README.md)

## Teaching background

The project builds on PHYS 515 statistical physics teaching and conceptual discussions, organizing probability, sampling and microstate counting into interactive experiments.

- **Probability and distributions**: PDFs/CDFs, quantiles, boxplots, median/IQR alignment, and the meaning of skewness and kurtosis.
- **Tails and limits**: survival functions, Pareto distributions, conditions for moment existence, the law of large numbers and the central limit theorem.
- **Microstates and thermodynamics**: the microcanonical ensemble, Boltzmann entropy, and the relationship between entropy, energy and temperature in a two-level model.

The examples distinguish population quantities from sample statistics, connect different graphical representations and state the assumptions behind each conclusion. Interface explanations, numerical models and figure exports follow these teaching goals.

The scope covers probability, sampling and two-level entropy. It does not include canonical ensembles, thermal reservoirs, ideal gases or the Gibbs correction.

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
