"""Opt-in browser regression for a running local preview (see docs/browser-checks.md)."""

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", type=Path, default=Path("figs/browser-checks"))
    args = parser.parse_args()
    if urlparse(args.url).hostname not in {"localhost", "127.0.0.1", "::1"}:
        parser.error("Use a local preview; this script changes session controls.")
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(15000)
        labs = {
            "distributions": ("Distributions & boxplots", "分布与箱型图", "dist_resample"),
            "tails": ("Skewness, kurtosis & tails", "偏度、峰度与尾部", "tail_resample"),
            "clt": ("Large numbers & the CLT", "大数定律与 CLT", "clt_resample"),
            "entropy": ("Microstates & entropy", "微观态与熵", "ent_shuffle"),
        }
        for lab, (english, chinese, action) in labs.items():
            page.goto(f"{args.url}/?lang=en&lab={lab}")
            expect(page.get_by_role("heading", name=english, exact=True)).to_be_visible()
            for language, heading, code in [("中文", chinese, "zh"), ("English", english, "en")]:
                page.get_by_role("button", name=language, exact=True).click()
                expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
                # Clicking the selected language must not deselect it.
                page.get_by_role("button", name=language, exact=True).click()
                page.locator(f".st-key-{action}").get_by_role("button").click()
                expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
                expect(page).to_have_url(re.compile(rf"[?&]lab={lab}(?:&|$)"))
                expect(page).to_have_url(re.compile(rf"[?&]lang={code}(?:&|$)"))
                expect(page.get_by_role("radio", checked=True)).to_have_count(1)

        # Views inside popovers must survive the frontend's translated labels.
        for lab, choice, display_key, view_key, action in [
            (
                "distributions",
                "Central 99% interval",
                "display_distributions",
                "dist_view",
                "dist_resample",
            ),
            ("clt", "Standardized means", "display_clt", "clt_view", "clt_resample"),
        ]:
            page.goto(f"{args.url}/?lang=en&lab={lab}")
            page.locator(f".st-key-{display_key}").get_by_role("button").click()
            page.get_by_role("button", name=choice, exact=True).click()
            page.keyboard.press("Escape")
            page.get_by_role("button", name="中文", exact=True).click()
            page.locator(f".st-key-{action}").get_by_role("button").click()
            page.get_by_role("button", name="English", exact=True).click()
            page.locator(f".st-key-{display_key}").get_by_role("button").click()
            expect(
                page.locator(f".st-key-{view_key}").get_by_role("button", name=choice)
            ).to_have_attribute("aria-pressed", "true")
            page.keyboard.press("Escape")

        # Check both languages at phone, narrow-window and short-desktop sizes.
        for width, height in [(390, 844), (820, 900), (1280, 650)]:
            page.set_viewport_size({"width": width, "height": height})
            for lab, (english, chinese, action) in labs.items():
                for lang, heading in [("en", english), ("zh", chinese)]:
                    page.goto(f"{args.url}/?lang={lang}&lab={lab}")
                    expect(page.get_by_role("heading", name=heading, exact=True)).to_be_visible()
                    toolbar = page.locator(f".st-key-control_toolbar_{lab}")
                    toggle = toolbar.get_by_role("checkbox")
                    expect(toggle).to_be_checked()
                    expect(page.locator(f".st-key-control_body_{lab}_open")).to_be_visible()
                    body = (
                        page.locator(f".st-key-control_body_{lab}_open")
                        .locator("..")
                        .bounding_box()
                    )
                    assert body and body["height"] <= height * 0.36 + 24

                    # Top-level actions must occupy separate boxes after wrapping.
                    items = [
                        toolbar.locator(f".st-key-panel_toggle_{lab}"),
                        toolbar.locator(f".st-key-{action}"),
                    ]
                    if lab != "entropy":
                        items.append(toolbar.locator(f".st-key-display_{lab}"))
                    if lab in {"distributions", "clt"}:
                        items.append(toolbar.locator(f".st-key-comparison_{lab}"))
                    boxes = []
                    for item in items:
                        expect(item).to_be_visible()
                        box = item.bounding_box()
                        assert box
                        for previous in boxes:
                            overlap_x = min(
                                box["x"] + box["width"], previous["x"] + previous["width"]
                            ) - max(box["x"], previous["x"])
                            overlap_y = min(
                                box["y"] + box["height"], previous["y"] + previous["height"]
                            ) - max(box["y"], previous["y"])
                            assert overlap_x <= 0 or overlap_y <= 0, (box, previous)
                        boxes.append(box)
                    page.screenshot(
                        path=str(args.output / f"{lab}-{lang}-{width}x{height}-open.png")
                    )
                    toggle.uncheck()
                    expect(page.locator(f".st-key-control_body_{lab}_closed")).to_be_hidden()
                    if lab != "entropy":
                        toolbar.locator(f".st-key-display_{lab}").get_by_role("button").click()
                        page.keyboard.press("Escape")
                    page.get_by_test_id("stMain").evaluate("el => { el.scrollTop = 650; }")
                    expect(toolbar).to_be_visible()
                    box = toolbar.bounding_box()
                    assert box and 45 <= box["y"] < 130, box
                    toolbar.locator(f".st-key-{action}").get_by_role("button").click()
                    expect(page).to_have_url(re.compile(rf"[?&]lab={lab}(?:&|$)"))
                    assert page.evaluate(
                        "document.documentElement.scrollWidth <= window.innerWidth"
                    )
                    page.screenshot(
                        path=str(args.output / f"{lab}-{lang}-{width}x{height}-closed.png")
                    )

        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(f"{args.url}/?lang=en&lab=distributions")
        expect(page.locator(".st-key-control_toolbar_distributions")).to_be_visible()
        expect(page.locator(".st-key-panel_toggle_distributions")).to_be_hidden()
        expect(page.locator(".st-key-control_body_distributions_open")).to_be_visible()
        page.screenshot(path=str(args.output / "desktop.png"))
        browser.close()
    print(f"Browser regression passed; screenshots: {args.output.resolve()}")


if __name__ == "__main__":
    main()
