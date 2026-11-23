"""
MeraDomain AI Studio - One-Time Google Business Profile (GMB) Login Launcher.
Opens a visible Chromium window so you can sign into Google once.
The session is saved permanently in data/browser_profiles/gmb.
"""

import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
PROFILE_DIR = ROOT_DIR.parent / "data" / "browser_profiles" / "gmb"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    print("==================================================================")
    print("  MeraDomain AI Studio - Google Business Profile Authentication")
    print("==================================================================")
    print(f"Browser profile directory: {PROFILE_DIR}")
    print("Opening Chromium window...")

    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 850},
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto("https://business.google.com/")

        print("\n>>> INSTRUCTIONS:")
        print("1. Log into your Google Account that owns or manages MeraDomain.")
        print("2. Approve 2FA / prompt on your phone if requested.")
        print("3. Once you see your Google Business dashboard, simply CLOSE the window.")
        print("4. The AI worker will then post updates directly to Google Business Profile!")
        print("------------------------------------------------------------------\n")

        while True:
            await asyncio.sleep(2)
            if not browser.pages or len(browser.pages) == 0:
                break

if __name__ == "__main__":
    asyncio.run(main())
