# Architecture / 架构

The app keeps calculations independent from Streamlit. Pages compose those calculations with controls and figures; they do not define alternative mathematical conventions.

应用将科学计算与 Streamlit 分离。页面负责连接参数、计算与图形，不另行定义数学约定。

| Module | Responsibility / 职责 |
| --- | --- |
| `physics.py` | Pure models, local random generators, sample summaries and histogram normalization / 纯模型、局部随机数、统计摘要与直方图归一化 |
| `state.py` | Session-local control persistence across navigation / 页面切换时保留会话内参数 |
| `distribution_ui.py` | Shared bilingual distribution names, base parameters and descriptions / 统一分布名称、原始参数与说明 |
| `i18n.py` | Language choice and bilingual display text / 语言选择与双语文本 |
| `shared.py` | Chart configuration, metric readouts, headings and HTML export / 图形配置、指标读数、标题及 HTML 导出 |
| `plot_theme.py` | Semantic colors shared by interactive and static plots / 交互与静态图共用语义配色 |
| `styles/app.css` | Responsive layout, spacing, colors and control-bar positioning / 响应式布局、间距、颜色与参数栏定位 |
| `interactions.py` | Saved comparisons and the sampling walkthrough / 保留对照及抽样演示 |
| `labs/` | Experiment-specific controls and plot composition / 各实验的控件与图形组合 |
| `glossary.py` | Searchable bilingual definitions and related terms / 双语定义与相关术语 |
| `app.py` | Navigation, session restoration and page composition / 导航、状态恢复与页面组合 |
| `export_figures.py` | Batch Matplotlib exports using the same numerical models / 共享数值模型的批量科学出图 |

## Data flow / 数据流

1. Restore saved controls, then render the selected page.
2. Read stable model IDs and numeric settings from widgets.
3. Compute using `physics.py`, passing a local seed explicitly.
4. Build plots from full-precision arrays; apply readout formatting in the presentation layer.
5. Remember controls before a page or language change can trigger widget cleanup.

恢复参数 → 控件读取稳定标识及数值 → 纯函数计算 → 完整精度数据绘图 → 显示层格式化。最后保存控件值，避免页面或语言切换清除实验状态。

Histogram density uses the full sample count even when bins show only a restricted interval. `histogram_density` handles explicit nonuniform bins; `sample_histogram` chooses a display window and uniform bins. Saved and current runs share bins while retaining their own normalization counts.

直方图始终按完整样本数归一化。`histogram_density` 支持显式非等宽分箱；`sample_histogram` 负责常用视窗和等宽分箱。保留对照与当前实验共用分箱，各自使用对应的完整样本数。

## State and caching / 状态与缓存

Widget IDs, model IDs and seeds are language-independent. Translated text is presentation only. Settings and saved comparisons belong to a Streamlit session; they are not a database or a durable user profile. A new session does not restore previous samples automatically. URL parameters select only the page and language.

控件标识、模型名称与随机种子不依赖语言。参数与对照属于 Streamlit 会话，不持久化为用户资料；新的会话不会自动恢复旧样本。URL 参数只指定页面和语言。

The CLT cache stores deterministic numerical results keyed by all experiment arguments. Streamlit may share cached results across sessions; mutable widget state and saved comparisons remain session-local. New cached functions must not read implicit session settings or use a global random generator.

CLT 缓存按全部实验参数保存确定性数值结果，可在会话间共享；控件及对照状态仍在各自会话内。新增缓存函数应显式接收参数，避免读取隐含会话状态或使用全局随机数生成器。

Defaults are initialized once with `state.initialize_controls`; keyed widgets then omit explicit `value` arguments. Restored session values remain the single source of truth. Bounds-dependent values, such as the excited-unit count, are clamped before creating the widget.

默认参数由 `state.initialize_controls` 在缺失时初始化，绑定 key 的控件不再同时传入显式 `value`。恢复后的会话值是唯一取值来源；激发态数量等依赖边界的值在创建控件前调整到有效范围。

## Adding an experiment / 新增实验

- Put calculations in `physics.py` (or a dedicated pure module when a topic grows), with tests for known limits and assumptions.
- Implement `render()` under `labs/`; use `chart`, `metric_row`, stable widget keys and `tr` for bilingual labels.
- Add navigation and page selection in `app.py`; register any new control prefix in `state.py` and related terms in `glossary.py`.
- Test resampling, language switching, glossary navigation and any invalid-theory case. A sample estimate must never stand in for a nonexistent population moment.
- Review the Docker runtime file list when adding top-level modules or assets.

新增实验先实现可独立测试的计算，再组合共享界面组件。新增参数前缀和术语入口需登记；验证抽样、双语和导航保持一致，并明确理论不适用的情形。新增模块或资源时同步检查容器文件清单。

## Verification / 验证

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
```

Numerical tests check normalization, known moments, asymptotic conditions and exact small systems. AppTest checks interaction paths and plotted arrays. Browser inspection remains necessary for sticky positioning, tooltip behavior, responsive layout and Plotly hover appearance; AppTest does not render CSS.

数值测试验证归一化、已知矩、适用条件和小系统精确结果；AppTest 验证交互路径与绘图数据。参数栏定位、提示框、响应式排布和 Plotly 悬浮效果仍需要浏览器目测，AppTest 不渲染 CSS。


## Code style / 代码风格

Ruff is a locked development dependency. Python code uses four-space indentation, a target line length of 100, and organized imports. Long teaching text may exceed the target; keep its wording intact. Run `uv run --locked ruff format .` to apply formatting, and `uv run --locked ruff check .` to check imports and basic code issues. CSS uses expanded blocks with two-space indentation.

Ruff 作为开发依赖锁定。Python 统一采用四空格缩进、100 字符目标行宽和有序导入。较长教学文本允许超过目标行宽，以保留完整语义。使用 `uv run --locked ruff format .` 格式化，使用 `uv run --locked ruff check .` 检查导入和基础代码问题。CSS 使用展开的声明块与两空格缩进。

## Responsive controls / 响应式控制面板

`shared.control_panel` owns one widget tree and one resampling action. The parameter toggle is available at every size, starts expanded, and persists across navigation and language changes. The panel establishes a CSS query container: above 680px of usable panel width, the toggle sits on the left and the action group on the right. At 680px or less, a two-column grid places Parameters/Resample in row one and Display/Compare in row two. Optional actions do not leave orphan buttons. Narrow panels and short windows bound the parameter body's height; menus stay outside the scrolling body. Saved-comparison status appears inside the popover so the trigger keeps its width.

`shared.control_panel` 使用同一组参数和抽样控件。参数默认展开，各尺寸均可收起，并保留会话选择。按面板实际可用宽度切换排版：宽于 680px 时参数开关靠左、操作靠右；窄面板固定两列，首行是参数／抽样，次行是显示／对照。窄面板或短窗口限制参数区域高度，弹窗入口始终保留。固定分布参数直接显示在选择框；坐标对齐时在图表附近说明，避免把原始参数与转换后的坐标混淆。

Navigation uses per-language widget keys and a validated canonical page ID. Display scales and sampling steps use required segmented controls to preserve logical values across translation.

Standalone HTML generation captures a figure and language configuration when rendering, then builds the file on download without accessing session state in the worker thread.


## Visual semantics / 视觉语义

Chart titles and subtitles are native Plotly text with reserved toolbar space and bilingual line wrapping. SVG and HTML exports retain the same headings; Matplotlib exports share `plot_theme.COLORS`.

图题与简短说明使用 Plotly 原生文字，预留工具栏空间并按中英文换行；SVG 与 HTML 导出保留相同图题，Matplotlib 出图共享 `plot_theme.COLORS`。

Population moments use `nan` for undefined quantities and `inf` for divergence. Variance requires a finite mean; standardized moments require finite variance. Explicit histogram bounds must be finite and strictly increasing; only automatic bounds receive the constant-sample fallback.

总体矩用 `nan` 表示未定义、`inf` 表示发散；方差需有有限均值，标准化偏度与峰度需有有限方差。显式直方图范围必须有限且严格递增；常量样本的兜底仅用于自动范围。

In the distributions experiment, use teal for population theory and the selected probability interval (area, CDF endpoints and sample-plot band), orange for observations, purple for observations beyond sample IQR fences, and muted dotted lines for those fences. CDF endpoints have a white outline so they remain distinct from the theoretical curve. Interval selection and sample fences are independent; the fence switch controls guide lines and labels only. A point beyond the fences is not necessarily invalid data.

在分布与箱型图实验中，青色表示总体理论及选中概率区间；橙色表示样本；紫色标记样本围栏外观测；灰色点线表示围栏。CDF 端点使用青色配白描边。概率区间与样本围栏独立，围栏开关仅控制辅助线与标签，围栏外观测不等于错误数据。分布名称、原始参数与对照说明由 `distribution_ui.py` 统一生成，计算约定仍属于 `physics.py`。

## Manual UI checks / 手动界面检查

- Switch English/Chinese and navigate away/back: keep the experiment, parameters and display scale. / 切换语言及往返页面后保留实验、参数和显示尺度。
- Inspect desktop, narrow and short windows, including scrolling with parameters expanded: check overlap and usable chart space. / 检查桌面、窄屏及矮屏，包含参数展开时滚动，确认控件不重叠、图表有可用空间。
- Exercise resampling, saved comparisons and HTML downloads. / 检查抽样、保留对照和 HTML 下载。
- Check phone legends, quartile labels, hover/touch readouts and the distinct interval/fence colors. / 检查手机图例、四分位标注、悬浮或触控读数，以及区间／围栏配色的区分。
- Record the browser, viewport sizes and scenarios actually checked; mark anything unverified. Passing AppTest does not establish visual correctness. / 记录实际检查的浏览器、尺寸与场景；注明未验证项，不能用 AppTest 通过代替视觉检查。
