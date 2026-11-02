# Release notes

English · [简体中文](docs/zh-CN/CHANGELOG.md) · [Project overview](README.md)

## Unreleased

### Added

- Add experiment 05, **Joint & conditional probability**, linking Gaussian correlation, marginal densities and conditional slices.
- Add experiment 06, **Thermal contact & energy sharing**, with exact energy-sharing probabilities, entropy and equilibrium fluctuations.
- Add experiment 07, **Reservoir & canonical ensemble**, comparing finite-reservoir probabilities with a canonical approximation at the same mean energy.
- Add experiment 08, **Temperature & heat capacity**, connecting two-level populations, mean energy, heat capacity and energy fluctuations.
- Add experiment 09, **Ideal gas & speed**, comparing Gaussian velocity components with the Maxwell speed distribution.
- Add experiment 10, **Free energy & stability**, connecting Landau free-energy minima, equilibrium branches and metastability.
- Extend bilingual explanations, glossary entries and chart downloads to the new experiments.

### Changed

- Improve shared-axis boxplot labels and legends on narrow screens while retaining full hover readouts.
- Use teal markers with white outlines for selected theoretical values in the entropy and inverse-temperature plots.
- Reorganize the project overview and model notes to cover the expanded experiment collection.

### Fixed

- Include correlation and conditioning values in joint Gaussian chart exports.
- Correct equilibrium-point classification at the Landau critical temperature for very small nonzero fields.
- Include the chart-width observer in Docker builds to prevent missing-resource errors.

## v0.1.1

- Add GitHub Actions checks for Ruff, formatting and pytest on pull requests and pushes to `main`.
- Separate English and Simplified Chinese documentation, with links between matching pages.
- Use Python 3.12 for development and deployment, with `.python-version` for uv and matching Docker configuration.
- Add Streamlit Community Cloud deployment instructions and separate local binding from shared server configuration.
- Preserve the active experiment, display scale and sampling walkthrough across language changes; keep one language selected.
- Use a shared parameter panel with right-aligned desktop actions and a two-row compact toolbar. Parameters are expanded by default and can be collapsed.
- Centralize distribution names, base parameters and comparison descriptions; label fixed parameters and aligned axes.
- Distinguish undefined and divergent population moments, including Student t and Pareto boundary cases. Reject invalid explicit histogram bounds.
- Share interactive and static plot colors. Use teal CDF endpoints with white outlines and purple beyond-fence observations; the fence toggle controls guide lines and labels.
- Retain wrapped titles and subtitles in SVG and HTML exports. Generate chart HTML on demand without rerunning the experiment.
- Improve secondary-text contrast, correct Pearson capitalization and standardize the Chinese term for population inversion.
- Expand interaction/state regression coverage and document manual UI checks.

## v0.1.0 — Initial baseline

- Four interactive experiments: distributions and boxplots; skewness, kurtosis and tails; LLN and CLT; microstates and entropy.
- English/Chinese interface, searchable bilingual glossary and contextual mathematical explanations.
- Reproducible sampling, linked probability intervals, retained comparisons and a step-by-step CLT sampling walkthrough.
- Compact numerical readouts, optional explanations and responsive chart layouts.
- Session settings preserved across navigation and language changes, with a single source of widget initialization.
- Pure numerical models shared by the app and scientific figure exports; separate state, presentation and styling modules.
- Numerical and interaction regression tests, Ruff formatting/lint rules and locked Python dependencies.
- Docker configuration and deployment documentation.
