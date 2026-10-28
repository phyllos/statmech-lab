# StatMech Lab · PHYS 515

English · [简体中文](docs/zh-CN/README.md)

An interactive concept lab for statistical physics, for local use or web hosting. Linked plots, reproducible sampling, and mathematical explanations connect probability distributions, fluctuations, and microstate counting.

## Run locally

The project uses Python 3.12 for local development and deployment. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to manage the environment; `.python-version` specifies the interpreter version, and uv can install it if needed.

```bash
git clone https://github.com/phyllos/statmech-lab.git
cd statmech-lab
uv sync --locked
uv run --locked streamlit run app.py --server.address=127.0.0.1
```

If you already have a checkout, run the last two commands from its root instead of cloning again. Open the local URL printed in the terminal, usually `http://localhost:8501`. Stop the server with `Ctrl+C`.

Dependencies are pinned in `uv.lock`; the project uses `package = false` and needs no package build. `requires-python` declares the compatibility range. Local validation targets Python 3.12.

## Deploy on Streamlit Community Cloud

Use repository **`phyllos/statmech-lab`**, branch **`main`**, entrypoint **`app.py`**, and select **Python 3.12** in Advanced settings. No secrets are required. Community Cloud uses the existing `uv.lock` and `pyproject.toml`; no separate `requirements.txt` is needed.

See the [deployment guide](docs/en/deployment.md) for setup, verification, sharing and updates. The Dockerfile supports deployment on other container hosts.

## Explore

1. **Distributions & boxplots**: PDFs, CDFs, interval probabilities, sample histograms, quantiles, fences, and observed whisker endpoints.
2. **Skewness, kurtosis & tails**: tail probabilities, population moment existence, and fluctuations in sample kurtosis.
3. **LLN & CLT**: individual observations, repeated sample means, standardization, and cases outside the classical CLT assumptions.
4. **Microstates & entropy**: two-level configurations at fixed excitation count, multiplicity, entropy, and large-N inverse temperature.

The interface starts in English. Use **English / 中文** below the sidebar brand to switch languages while keeping the current experiment, parameters, and sampled data.

Display settings and comparisons are available through compact controls; the CLT walkthrough is collapsed by default. Optional interactions in the distribution and CLT experiments let you link the interval across plots, retain a result for comparison, and replay the CLT sampling process step by step. See [interaction guide](docs/en/interactions.md).

The sidebar **Glossary** provides 28 bilingual terms. Search in either language, by abbreviation or symbol, and filter by topic. Each experiment also ends with a collapsible list of relevant terms. Opening the glossary and returning to an experiment preserves its settings and sample.

Direct links accept `?lab=distributions`, `?lab=tails`, `?lab=clt`, `?lab=entropy`, or `?lab=glossary`. Add `&lang=zh` or `&lang=en` to select a language. For example: `?lab=glossary&lang=zh`.

Hover for values, drag to zoom, and double-click to reset. The toolbar supports panning and SVG export; each experiment also offers a standalone interactive HTML chart.

## Reproducibility and conventions

- Coordinates use dimensionless variables. The two-level model measures energy in units of the positive gap ε and entropy in units of kB.
- Population moments come from the probability model. Undefined moments (`NaN`) and divergent moments (`∞`) are distinguished; larger samples do not create a missing population moment. Variance requires a finite mean, and standardized skewness/kurtosis require finite variance.
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
distribution_ui.py     Shared distribution names, parameters and descriptions
plot_theme.py          Semantic colors shared by interactive and static plots
shared.py              Shared chart styling and UI components
styles/app.css         Responsive layout and visual styles
interactions.py        Comparison controls and sampling walkthrough
labs/                  Four experiment pages
export_figures.py      Batch scientific figure export
docs/en/               English teaching notes, architecture and deployment guides
docs/zh-CN/            Simplified Chinese documentation
tests/                 Numerical and application-path checks
.python-version        Python 3.12 selection for local uv commands
.streamlit/config.toml Shared theme and headless-server configuration
```

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
uv run --locked python export_figures.py
```

Static PNG and SVG figures are written to `figs/`. The exporter and app share numerical models and semantic colors. These are curated teaching figures; they do not export the current browser session.

## Scope and sources

The lab covers probability distributions, sampling, limit theorems and two-level entropy. Canonical ensembles, thermal reservoirs, ideal gases and Liouville evolution are outside its current scope.

Examples build on PHYS 515 teaching and discussions of PDF/CDF, quantiles, median/IQR alignment, survival functions, Pareto distributions and boxplots. See [source notes](docs/en/sources.md).

## Version control

The project version is **0.1.1**. `v0.1.0` marks the initial baseline. `main` contains integrated changes; version tags identify release snapshots. **Unreleased** lists changes not yet assigned to a release. See the [release notes](CHANGELOG.md) and [Git workflow](docs/en/git-workflow.md).

## Architecture and deployment

See [architecture](docs/en/architecture.md) for module boundaries and the manual UI checklist, and [deployment](docs/en/deployment.md) for local, Community Cloud and container setup. The application itself needs no account, API key or database; hosting services have their own account and sharing settings.
