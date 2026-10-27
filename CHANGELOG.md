# Release notes / 版本说明

## Unreleased / 未发布

- Distinguish undefined and divergent population moments, including Student t and Pareto boundary cases; reject invalid explicit histogram bounds.
- Share interactive/static plot colors and retain wrapped native titles and subtitles in SVG/HTML exports.
- 区分未定义与发散的总体矩，覆盖 Student t 与 Pareto 边界；拒绝非法显式直方图范围。
- 交互与静态图共享配色，SVG／HTML 导出保留换行图题与简短说明。

- Preserve the active experiment, display scale and sampling walkthrough across language changes; require a selected language and retain Pearson's capitalization.
- Share a persistent parameter panel across experiments, with right-aligned desktop actions and a two-row compact layout based on panel width. Parameters start expanded and can be collapsed.
- Centralize distribution names, base parameters and comparison descriptions; show fixed parameters in selectors and identify aligned axes near charts.
- Use teal CDF endpoint markers with white outlines and purple beyond-fence observations. The fence toggle controls guide lines and labels only.
- Improve secondary-text contrast and standardize the Chinese term for population inversion.
- Generate chart HTML on demand without rerunning the experiment.
- Add interaction/state regression tests; consolidate manual UI checks in the architecture notes and remove the separate browser script and guide.

- 切换语言后保留当前实验、显示尺度及抽样演示；语言保持选中，Pearson 保留正确大小写。
- 实验共用参数面板，桌面操作靠右，窄面板按实际宽度固定两行；参数默认展开，可手动收起。
- 统一分布名称、原始参数与对照说明；固定参数直接显示在选择框，对齐坐标在图表附近说明。
- CDF 区间端点采用青色白描边，围栏外观测保留紫色；围栏开关仅控制辅助线与标签。
- 改善辅助文字对比度，统一“粒子数反转”术语。
- 按需生成交互图 HTML，下载不触发实验重跑。
- 补充交互与状态回归测试；手动界面检查合并到架构说明，移除独立浏览器脚本与指南。

## v0.1.0 — Initial baseline / 初始基线

- Four interactive experiments: distributions and boxplots; skewness, kurtosis and tails; LLN and CLT; microstates and entropy.
- English/Chinese interface, searchable bilingual glossary and contextual mathematical explanations.
- Reproducible sampling, linked probability intervals, retained comparisons and a step-by-step CLT sampling walkthrough.
- Compact numerical readouts, optional explanations and responsive chart layouts.
- Session settings preserved across navigation and language changes, with a single source of widget initialization.
- Pure numerical models shared by the app and scientific figure exports; separate state, presentation and styling modules.
- Numerical and interaction regression tests, Ruff formatting/lint rules and locked Python dependencies.
- Docker configuration and deployment documentation. Container build and startup validation remain a deployment step.

- 四个交互实验：分布与箱型图、偏度与峰度及尾部、大数定律与中心极限定理、微观态与熵。
- 中英双语界面、可搜索术语表与相关数学解释。
- 可复现抽样、概率区间联动、保留结果对照及逐步 CLT 抽样演示。
- 紧凑读数、按需说明与响应式图表布局。
- 页面与语言切换保留会话参数，控件使用统一的初始化来源。
- 应用与科学出图共享纯数值模型；状态、展示组件及样式独立组织。
- 数值与交互回归测试、Ruff 格式和检查规则，以及锁定的 Python 依赖。
- Docker 配置与部署文档；容器构建和启动验证在部署阶段完成。
