# Browser regression / 浏览器回归

AppTest checks state and scientific arrays, but does not render CSS or reproduce stale translated values held by a browser. The optional browser check exercises the actual frontend against a local preview.

AppTest 验证状态和数值，不渲染 CSS，也不模拟浏览器保留的旧语言标签。浏览器检查需独立运行；不能用 AppTest 通过代替视觉与前端验证。

Start the app in one terminal:

```bash
uv run --locked streamlit run app.py
```

In another terminal, install the optional browser tooling and run the check:

```bash
uv run --with playwright playwright install chromium
uv run --with playwright python tests/browser/check_ui.py
```

For another local port, pass `--url http://127.0.0.1:8517`. This script changes only its own browser session and accepts loopback URLs only. Screenshots go into the ignored `figs/browser-checks/` directory. Playwright is optional tooling and is not part of the locked runtime dependencies.

检查覆盖四页的语言往返、再次点击当前语言、切换语言后的重新抽样、弹窗显示尺度保持，以及 390×844、820×900、1280×650 和 1440×1000 的控制面板显示规则。截图需要人工检查图例、弹窗位置与文本重叠。

On narrow or short screens, the toolbar stays visible and starts with its parameters expanded. The toggle shows or hides the original widgets in a bounded scrolling area; collapsing does not reset settings or draw new observations. The parameter toggle works on desktop as well. Window resizing only changes CSS visibility and retains the same widget instances.

窄屏或短窗口默认展示紧凑吸顶栏，完整参数默认展开，仍可手动收起；展开区域限制高度并可内部滚动。收起不会清空参数或重新抽样。桌面也可以收起参数。窗口缩放只改变显示规则，不创建另一套参数。

The script is an executable regression specification. Its presence does not mean it has been run successfully: browser access must be available, and any failure needs investigation before claiming visual validation.

脚本是可执行的回归检查方案；文件存在不代表已执行通过。需在允许浏览器访问的环境中运行，并检查失败结果后才能确认视觉验证完成。

Check English and Chinese at 390px, 820px, and a short desktop window: the Parameters switch, resampling button, display options, and comparison popover must wrap without overlap. Distribution labels and selects should share a row on narrow windows; popovers remain accessible while parameters are collapsed.

The toolbar breakpoint uses the panel content width (680px), not viewport width. Verify a wide window with the sidebar expanded as well as a phone: Parameters/Resample occupy the first row and Display/Compare the second on compact panels. At larger panel widths, the three actions align to the right. Fixed distribution parameters must remain readable in the selector; aligned axes must be explicitly identified near the figures.
