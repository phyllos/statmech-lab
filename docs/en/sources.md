# Content and sources

English · [简体中文](../zh-CN/sources.md) · [Project overview](../../README.md)

## Teaching background

The project builds on PHYS 515 teaching and conceptual discussions, with interactive experiments spanning probability, ensembles and thermodynamic stability.

- **Probability and distributions**: PDFs/CDFs, quantiles, boxplots, median/IQR alignment, and the meaning of skewness and kurtosis.
- **Tails and limits**: survival functions, Pareto distributions, conditions for moment existence, the law of large numbers and the central limit theorem.
- **Joint probability**: Gaussian correlation, marginal distributions and conditional densities.
- **Microstates and ensembles**: two-level counting, entropy, thermal contact, finite reservoirs and the canonical ensemble.
- **Thermal response and stability**: energy fluctuations, heat capacity, ideal-gas velocities and the Landau free-energy model.

The examples distinguish population quantities from sample statistics, connect different graphical representations and state the assumptions behind each conclusion. Interface explanations, numerical models and figure exports follow these teaching goals.

The experiments describe equilibrium distributions and thermodynamic relations. Gas mixing entropy, the Gibbs correction and microscopic time evolution are outside the current scope.

The Landau experiment follows the symmetry-based quartic expansion and mean-field limitations discussed in [David Tong, Statistical Physics, §5.4–5.5](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S5.html). Its coefficients are rescaled for an illustrative dimensionless model.

## Definitions and software references

- [SciPy kurtosis](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html): Pearson and Fisher excess kurtosis definitions and sample bias correction.
- [SciPy Pareto](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pareto.html): Type-I Pareto, PDF/SF and parameterization.
- [NumPy quantile](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html): quantile interpolation conventions.
- [Streamlit Plotly charts](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart): interactive chart display.

## Model assumptions

### Joint Gaussian model

The joint Gaussian experiment fixes both marginals at N(0, 1) and generates no random samples. Plot ranges stay fixed; zero correlation implies independence here because the variables are jointly Gaussian.

### Thermal contact

The thermal-contact experiment uses equal energy gaps and negligible coupling energy, with equal weights for combined microstates at fixed total energy. Its entropy curves fix both subsystem energies; the entropy with only the total energy constrained is constant.

### Finite reservoir

The reservoir experiment compares both laws at p = q/(N_A + N_B), after rounding the target excitation count to the nearest integer, with halves rounded up. The canonical law retains its full support and uses βε = ln((1−p)/p); this mean-matched parameter is not an exact finite-system entropy derivative. The interface covers positive temperatures and the β = 0 limit.

### Temperature response

The temperature-response experiment assumes an ideal reservoir, fixed N and a fixed nondegenerate gap ε. Results are per unit and exact for independent units at any N. The zero slider setting denotes T → 0⁺; the smooth heat-capacity peak is not a phase transition.

### Landau model

The Landau experiment uses the dimensionless potential f = (t−1)m²/2 + m⁴/4 − hm, with t = T/Tc. Both zero-field equilibrium minima are retained below Tc; the critical quartic minimum and spinodal stationary inflections are distinguished. The model assumes a uniform scalar order parameter and does not simulate spatial fluctuations, nucleation or hysteresis dynamics.

## Key derivations

### Tail probabilities and moments

For Type-I Pareto with xm=1, f(x)=α x^(-α-1), x≥1 and α>0.
Its kth raw moment is α∫₁∞ x^(k-α-1) dx, which is finite only when α>k.
The survival function is x^(-α), with a power-law exponent differing from the PDF's by 1.

### Limit theorems

For iid variables with finite mean μ and finite, nonzero variance σ²,
Zₙ=√n(X̄ₙ-μ)/σ converges in distribution to the standard normal as n→∞.
The law of large numbers requires weaker conditions; Pareto with 1<α≤2 illustrates the distinction between a finite mean and finite variance.
The arithmetic mean of iid Cauchy samples retains the same Cauchy distribution.

### Two-level entropy

For N two-level sites with fixed q, Ω=C(N,q) and S=kB ln Ω.
Stirling's approximation gives S/(NkB)≈−x ln x−(1−x)ln(1−x), where x=q/N.
Differentiating with respect to E=Nεx gives βε≈ln((1−x)/x). This does not assign probabilities to different q layers.

### Finite-reservoir and canonical probabilities

For a system A coupled to a finite two-level reservoir B, the exact marginal is hypergeometric. With p = q/(N_A + N_B), its canonical approximation is binomial: P(q_A) = C(N_A,q_A) p^q_A (1−p)^(N_A−q_A). Both means are N_A p; the exact variance is the canonical variance N_A p(1−p) multiplied by N_B/(N_A+N_B−1). The approximation follows from expanding the reservoir entropy around its mean energy. It keeps all q_A = 0..N_A, including energies excluded by a finite reservoir.

### Heat capacity and fluctuations

For independent, nondegenerate two-level units coupled to an ideal reservoir, θ = kB T/ε and p = exp(−1/θ)/(1+exp(−1/θ)). The partition function is Z = (1+exp(−1/θ))^N, U/(Nε) = p and C/(NkB) = p(1−p)/θ². These are exact canonical results, without Stirling's approximation. For T>0, Var(E) = kB T² C. At T→0⁺, U and C vanish; at high temperature, U/(Nε)→1/2 and Var(E)/(Nε²)→1/4 while C/(NkB)→0. The smooth two-level heat-capacity peak does not indicate a phase transition.

### Ideal-gas velocities

For a three-dimensional classical ideal gas at rest in the canonical ensemble, each velocity component is Gaussian with variance σ² = kB T/m. Integrating over a velocity-space shell gives g(v) = √(2/π) v² σ⁻³ exp(−v²/(2σ²)), v≥0. Its mode, mean and RMS speed are √2 σ, √(8/π) σ and √3 σ. Speed is the magnitude of all three components, not |v_x|. Experiment 09 fixes v₀ = √(kB T₀/m) and varies T/T₀; plotted densities are normalized in v/v₀ over their full support, not the cropped view. The canonical law is not an exact finite-isolated-system marginal and is not derived from the CLT.

### Landau equilibrium and stability

For f(m;t,h) = (t−1)m²/2 + m⁴/4 − hm, stationary points satisfy m³ + (t−1)m − h = 0. At h=0, equilibrium is m=0 for t≥1 and m=±√(1−t) for t<1. At t=1 the quartic minimum has zero curvature; zero curvature alone is inconclusive. At t<1 the spinodal fields obey |h_sp| = 2(1−t)^(3/2)/(3√3); the merging stationary points are inflections with nonzero third derivative. Only global minima enter the equilibrium curve. This is a uniform mean-field potential, not a microscopic simulation or a model of relaxation.
