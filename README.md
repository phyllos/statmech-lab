# StatMech Lab · PHYS 515

English · [简体中文](docs/zh-CN/README.md)

An interactive statistical physics lab connecting probability, microstate counting, ensembles and thermodynamic stability. Linked plots, reproducible sampling and optional derivations support exploration in English and Simplified Chinese. The app runs locally or on a web server.

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

## Experiments

| No. | Experiment | Main concepts |
| --- | --- | --- |
| 01 | Distributions & boxplots | PDF/CDF, interval probability, quantiles and sample summaries |
| 02 | Skewness, kurtosis & tails | Tail probabilities, moment existence and sample fluctuations |
| 03 | LLN & CLT | Sample means, standardization and conditions for convergence |
| 04 | Microstates & entropy | Two-level configurations, multiplicity, entropy and inverse temperature |
| 05 | Joint & conditional probability | Gaussian correlation, marginalization and conditioning |
| 06 | Thermal contact & energy sharing | Exact energy-sharing probabilities, entropy and equilibrium fluctuations |
| 07 | Reservoir & canonical ensemble | Finite-reservoir probabilities and the canonical approximation |
| 08 | Temperature & heat capacity | Two-level populations, thermal response and energy fluctuations |
| 09 | Ideal gas & speed | Gaussian velocity components and the Maxwell speed distribution |
| 10 | Free energy & stability | Landau free-energy minima, equilibrium branches and metastability |

Experiments 01–03 and 05 develop probability concepts. Experiments 04 and 06–08 follow the same two-level model from fixed energy to thermal contact and temperature response. Experiment 09 applies probability to gas velocities; experiment 10 provides a separate introduction to free energy and stability.

## Using the lab

- **Language and navigation:** English is the default. Switch with **English / 中文** in the sidebar; experiment parameters, samples and display settings are preserved within the session.
- **Controls and explanations:** Parameters are expanded by default. Display options, saved comparisons and derivations are available where relevant; deterministic experiments have no resampling action.
- **Glossary:** Search bilingual terms by name, abbreviation or symbol, or filter by topic. Each experiment also provides related terms.
- **Charts and exports:** Hover for values, drag to zoom and double-click to reset. The toolbar exports SVG; download buttons produce standalone interactive HTML charts. These files capture the current chart, not the full application's controls.

See the [interaction guide](docs/en/interactions.md) for linked selections, comparisons and suggested explorations, and [model notes](docs/en/sources.md) for assumptions and derivations.

Direct links use `?lab=<id>` and an optional `&lang=en` or `&lang=zh`. Experiment IDs are `distributions`, `tails`, `clt`, `entropy`, `joint`, `thermal`, `canonical`, `response`, `gas` and `landau`; the glossary uses `glossary`. For example: `?lab=thermal&lang=zh`.

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
physics.py             Pure numerical models, without UI or file effects
distribution_ui.py     Shared distribution names, parameters and descriptions
plot_theme.py          Semantic colors shared by interactive and static plots
shared.py              Shared chart styling and UI components
styles/                Responsive layout, visual styles and chart-width observer
interactions.py        Comparison controls and sampling walkthrough
labs/                  Experiment pages
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

The experiments focus on equilibrium probability models and thermodynamic concepts. They do not simulate microscopic time evolution. The Landau model assumes a uniform order parameter; spatial fluctuations, nucleation and hysteresis dynamics are outside its scope.

The examples build on PHYS 515 teaching and discussions. See [content and sources](docs/en/sources.md) for model assumptions, mathematical conventions and references.

## Version control

The project version is **0.1.1**. `v0.1.0` marks the initial baseline. `main` contains integrated changes; version tags identify release snapshots. **Unreleased** lists changes not yet assigned to a release. See the [release notes](CHANGELOG.md) and [Git workflow](docs/en/git-workflow.md).

## Architecture and deployment

See [architecture](docs/en/architecture.md) for module boundaries and the manual UI checklist, and [deployment](docs/en/deployment.md) for local, Community Cloud and container setup. The application itself needs no account, API key or database; hosting services have their own account and sharing settings.
