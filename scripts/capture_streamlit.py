"""Capture the running Streamlit UI with installed Microsoft Edge.

Run after starting Streamlit: uv run --with playwright python scripts/capture_streamlit.py
"""

import re
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "screenshots"
OUTPUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1900}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8501/", wait_until="domcontentloaded")
    page.locator(".hero h1").wait_for(timeout=30000)
    page.screenshot(path=OUTPUT / "streamlit_search.png", full_page=True)

    page.get_by_text("Benchmarks", exact=True).click()
    page.get_by_text(re.compile(r"The [\d,]+-document run")).wait_for(timeout=30000)
    page.locator(".result-card").first.wait_for(state="detached", timeout=30000)
    page.locator('[data-testid="stImage"] img').first.wait_for(timeout=30000)
    page.wait_for_function("Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)", timeout=30000)
    page.screenshot(path=OUTPUT / "streamlit_benchmarks.png", full_page=True)
    browser.close()

print(f"Saved screenshots in {OUTPUT}")
