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

        # Check every panel at phone, narrow-window and short-desktop sizes.
        for width, height in [(390, 844), (820, 900), (1280, 650)]:
            page.set_viewport_size({"width": width, "height": height})
            for lab, (english, _, _) in labs.items():
                page.goto(f"{args.url}/?lang=en&lab={lab}")
                expect(page.get_by_role("heading", name=english, exact=True)).to_be_visible()
                compact = page.locator(f".st-key-compact_controls_{lab}")
                expect(compact).to_be_visible()
                expect(page.locator(f".st-key-control_body_{lab}_closed")).to_be_hidden()
                compact.get_by_role("checkbox", name="Parameters", exact=True).check()
                expect(page.locator(f".st-key-control_body_{lab}_open")).to_be_visible()
                body = page.locator(f".st-key-control_body_{lab}_open").locator("..").bounding_box()
                assert body and body["height"] <= height * 0.42 + 24
                compact.get_by_role("checkbox", name="Parameters", exact=True).uncheck()
                page.get_by_test_id("stMain").evaluate("el => { el.scrollTop = 650; }")
                expect(compact).to_be_visible()
                box = compact.bounding_box()
                assert box and 45 <= box["y"] < 130, box
                compact.get_by_role(
                    "button", name="Rearrange" if lab == "entropy" else "Resample", exact=True
                ).click()
                expect(page).to_have_url(re.compile(rf"[?&]lab={lab}(?:&|$)"))
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(args.output / f"{lab}-{width}x{height}.png"))

        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(f"{args.url}/?lang=en&lab=distributions")
        expect(page.locator(".st-key-compact_controls_distributions")).to_be_hidden()
        expect(page.locator(".st-key-control_body_distributions_closed")).to_be_visible()
        page.screenshot(path=str(args.output / "desktop.png"))
        browser.close()
    print(f"Browser regression passed; screenshots: {args.output.resolve()}")


if __name__ == "__main__":
    main()
