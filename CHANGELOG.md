# Release notes

English · [简体中文](docs/zh-CN/CHANGELOG.md) · [Project overview](README.md)

## Unreleased

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
