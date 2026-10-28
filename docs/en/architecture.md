# Architecture

English · [简体中文](../zh-CN/architecture.md) · [Project overview](../../README.md)

The app keeps calculations independent from Streamlit. Pages compose those calculations with controls and figures; they do not define alternative mathematical conventions.

| Module | Responsibility |
| --- | --- |
| `physics.py` | Pure models, local random generators, sample summaries and histogram normalization |
| `state.py` | Session-local control persistence across navigation |
| `distribution_ui.py` | Shared bilingual distribution names, base parameters and descriptions |
| `i18n.py` | Language choice and bilingual display text |
| `shared.py` | Chart configuration, metric readouts, headings and HTML export |
| `plot_theme.py` | Semantic colors shared by interactive and static plots |
| `styles/app.css` | Responsive layout, spacing, colors and control-bar positioning |
| `interactions.py` | Saved comparisons and the sampling walkthrough |
| `labs/` | Experiment-specific controls and plot composition |
| `glossary.py` | Searchable bilingual definitions and related terms |
| `app.py` | Navigation, session restoration and page composition |
| `export_figures.py` | Batch Matplotlib exports using the same numerical models |

## Data flow

1. Restore saved controls, then render the selected page.
2. Read stable model IDs and numeric settings from widgets.
3. Compute using `physics.py`, passing a local seed explicitly.
4. Build plots from full-precision arrays; apply readout formatting in the presentation layer.
5. Remember controls before a page or language change can trigger widget cleanup.

Histogram density uses the full sample count even when bins show only a restricted interval. `histogram_density` handles explicit nonuniform bins; `sample_histogram` chooses a display window and uniform bins. Saved and current runs share bins while retaining their own normalization counts.

## State and caching

Widget IDs, model IDs and seeds are language-independent. Translated text is presentation only. Settings and saved comparisons belong to a Streamlit session; they are not a database or a durable user profile. A new session does not restore previous samples automatically. URL parameters select only the page and language.

The CLT cache stores deterministic numerical results keyed by all experiment arguments. Streamlit may share cached results across sessions; mutable widget state and saved comparisons remain session-local. New cached functions must not read implicit session settings or use a global random generator.

Defaults are initialized once with `state.initialize_controls`; keyed widgets then omit explicit `value` arguments. Restored session values remain the single source of truth. Bounds-dependent values, such as the excited-unit count, are clamped before creating the widget.

## Adding an experiment

- Put calculations in `physics.py` (or a dedicated pure module when a topic grows), with tests for known limits and assumptions.
- Implement `render()` under `labs/`; use `chart`, `metric_row`, stable widget keys and `tr` for bilingual labels.
- Add navigation and page selection in `app.py`; register any new control prefix in `state.py` and related terms in `glossary.py`.
- Test resampling, language switching, glossary navigation and any invalid-theory case. A sample estimate must never stand in for a nonexistent population moment.
- Review the Docker runtime file list when adding top-level modules or assets.

## Verification

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
```

Numerical tests check normalization, known moments, asymptotic conditions and exact small systems. AppTest checks interaction paths and plotted arrays. Browser inspection remains necessary for sticky positioning, tooltip behavior, responsive layout and Plotly hover appearance; AppTest does not render CSS.

## Code style

Ruff is a locked development dependency. Python code uses four-space indentation, a target line length of 100, and organized imports. Long teaching text may exceed the target; keep its wording intact. Run `uv run --locked ruff format .` to apply formatting, and `uv run --locked ruff check .` to check imports and basic code issues. CSS uses expanded blocks with two-space indentation.

Documentation describes project behavior and reproducible procedures. Reference sections use factual present-tense statements; guides use direct instructions; release notes use concise change verbs such as Use, Add and Fix. English and Chinese versions cover the same content. Conversation history, personal task updates and unverified release claims are excluded.

Detailed guides live in `docs/en/` and `docs/zh-CN/` with matching filenames. Root `README.md` and `CHANGELOG.md` are the English entry points; their Chinese counterparts live in `docs/zh-CN/`. Update both language versions together when behavior or release contents change, and keep links between corresponding pages.

## Responsive controls

`shared.control_panel` owns one widget tree and one resampling action. The parameter toggle is available at every size, starts expanded, and persists across navigation and language changes. The panel establishes a CSS query container: above 680px of usable panel width, the toggle sits on the left and the action group on the right. At 680px or less, a two-column grid places Parameters/Resample in row one and Display/Compare in row two. Optional actions do not leave orphan buttons. Narrow panels and short windows bound the parameter body's height; menus stay outside the scrolling body. Saved-comparison status appears inside the popover so the trigger keeps its width. Fixed distribution parameters appear in selectors; aligned coordinates are identified near charts to distinguish them from the original parameters.

Navigation uses per-language widget keys and a validated canonical page ID. Display scales and sampling steps use required segmented controls to preserve logical values across translation.

Standalone HTML generation captures a figure and language configuration when rendering, then builds the file on download without accessing session state in the worker thread.

## Visual semantics

Chart titles and subtitles are native Plotly text with reserved toolbar space and bilingual line wrapping. SVG and HTML exports retain the same headings; Matplotlib exports share `plot_theme.COLORS`.

Population moments use `nan` for undefined quantities and `inf` for divergence. Variance requires a finite mean; standardized moments require finite variance. Explicit histogram bounds must be finite and strictly increasing; only automatic bounds receive the constant-sample fallback.

In the distributions experiment, use teal for population theory and the selected probability interval (area, CDF endpoints and sample-plot band), orange for observations, purple for observations beyond sample IQR fences, and muted dotted lines for those fences. CDF endpoints have a white outline so they remain distinct from the theoretical curve. Interval selection and sample fences are independent; the fence switch controls guide lines and labels only. A point beyond the fences is not necessarily invalid data. Distribution names, base parameters and comparison descriptions come from `distribution_ui.py`; computational conventions belong to `physics.py`.

## Manual UI checks

- Switch English/Chinese and navigate away/back: keep the experiment, parameters and display scale.
- Inspect desktop, narrow and short windows, including scrolling with parameters expanded: check overlap and usable chart space.
- Exercise resampling, saved comparisons and HTML downloads.
- Check phone legends, quartile labels, hover/touch readouts and the distinct interval/fence colors.
- Record the browser, viewport sizes and scenarios actually checked; mark anything unverified. Passing AppTest does not establish visual correctness.
