# Architecture / 架构

The app keeps calculations independent from Streamlit. Pages compose those calculations with controls and figures; they do not define alternative mathematical conventions.

应用将科学计算与 Streamlit 分离。页面负责连接参数、计算与图形，不另行定义数学约定。

| Module | Responsibility / 职责 |
| --- | --- |
| `physics.py` | Pure models, local random generators, sample summaries and histogram normalization / 纯模型、局部随机数、统计摘要与直方图归一化 |
| `state.py` | Session-local control persistence across navigation / 页面切换时保留会话内参数 |
| `i18n.py` | Language choice and bilingual display text / 语言选择与双语文本 |
| `shared.py` | Chart configuration, metric readouts, headings and HTML export / 图形配置、指标读数、标题及 HTML 导出 |
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
