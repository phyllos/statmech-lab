# StatMech Lab · PHYS 515

English · [简体中文](README.zh-CN.md)

A local, interactive concept lab for statistical physics. Linked plots, reproducible sampling, and mathematical explanations connect probability distributions, fluctuations, and microstate counting.

## Run locally

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12 or a compatible newer version.

```bash
cd stat_mech
uv sync --locked
uv run --locked streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`. Stop the server with `Ctrl+C`. Dependencies are pinned in `uv.lock`; the project uses `package = false` and needs no package build.

## Explore

1. **Distributions & boxplots**: PDFs, CDFs, interval probabilities, sample histograms, quantiles, fences, and observed whisker endpoints.
2. **Skewness, kurtosis & tails**: tail probabilities, population moment existence, and fluctuations in sample kurtosis.
3. **LLN & CLT**: individual observations, repeated sample means, standardization, and cases outside the classical CLT assumptions.
4. **Microstates & entropy**: two-level configurations at fixed excitation count, multiplicity, entropy, and large-N inverse temperature.

The interface starts in English. Use **English / 中文** below the sidebar brand to switch languages while keeping the current experiment, parameters, and sampled data.

Display settings and comparisons are available through compact controls; the CLT walkthrough is collapsed by default. Optional interactions in the distribution and CLT experiments let you link the interval across plots, retain a result for comparison, and replay the CLT sampling process step by step. See [interaction guide](docs/interactions.md).

The sidebar **Glossary** provides 28 bilingual terms. Search in either language, by abbreviation or symbol, and filter by topic. Each experiment also ends with a collapsible list of relevant terms. Opening the glossary and returning to an experiment preserves its settings and sample.

Direct links accept `?lab=distributions`, `?lab=tails`, `?lab=clt`, `?lab=entropy`, or `?lab=glossary`. Add `&lang=zh` or `&lang=en` to select a language. For example: `?lab=glossary&lang=zh`.

Hover for values, drag to zoom, and double-click to reset. The toolbar supports panning and SVG export; each experiment also offers a standalone interactive HTML chart.

## Reproducibility and conventions

- Coordinates use dimensionless variables. The two-level model measures energy in units of the positive gap ε and entropy in units of kB.
- Population moments come from the probability model. Larger samples do not create population moments that fail to exist; nonfinite values are never replaced with zero.
- Default kurtosis is Pearson's standardized fourth central moment (3 for a normal distribution). Excess kurtosis subtracts 3; the selected convention is labeled.
- Sample quantiles use NumPy `method="linear"`. Tukey whiskers end at the most extreme observed values inside the 1.5 IQR fences. Statistics use the complete sample.
- A finite plot window does not truncate the distribution or renormalize its probability. Histograms divide counts by the full sample size and bin width, and report observations outside the view.
- Sampling uses local random generators. Identical parameters and seed reproduce identical data. Resample changes the seed; changing language does not.
- The classical CLT view requires iid observations with finite, nonzero variance. When its assumptions fail, the app does not draw an unjustified Gaussian approximation.
- The two-level model has N distinguishable, noninteracting units with energies 0 and ε. At fixed q, Ω = binom(N,q); configurations within that energy layer have equal weight.
- `βε = ln((N-q)/q)` is a large-N approximation, not an exact derivative of finite-N discrete entropy. Endpoints are limits; half excitation gives β = 0.

## Source layout

```text
app.py                 Application entry point and navigation
i18n.py                Language selection and display text
state.py               Session-local experiment persistence
glossary.py            Bilingual terms and contextual quick references
physics.py             Pure numerical model, without UI or file effects
shared.py              Shared chart styling and UI components
styles/app.css         Responsive layout and visual styles
interactions.py        Comparison controls and sampling walkthrough
labs/                  Four experiment pages
export_figures.py      Batch scientific figure export
docs/                  Scope and source notes
tests/                 Numerical and application-path checks
.streamlit/config.toml Local server and theme configuration
```

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
uv run --locked python export_figures.py
```

Static PNG and SVG figures are written to `figs/`. The exporter and app share `physics.py`.

## Scope and sources

This version bridges probability and entropy. Canonical ensembles, thermal reservoirs, ideal gases, and Liouville evolution are possible future modules.

Examples build on PHYS 515 teaching and discussions of PDF/CDF, quantiles, median/IQR alignment, survival functions, Pareto distributions and boxplots. See [source notes](docs/sources.md).

## Version control

`v0.1.0` is the initial project baseline on `main`, including the four bilingual experiments, linked views, saved comparisons, glossary, code-quality tools and deployment configuration. See the [release notes](CHANGELOG.md) and [Git workflow](docs/git-workflow.md).

## Architecture and deployment

See [architecture](docs/architecture.md) for module boundaries and extension guidelines, and [deployment](docs/deployment.md) for local and container commands. No account, API key, or database is required.
