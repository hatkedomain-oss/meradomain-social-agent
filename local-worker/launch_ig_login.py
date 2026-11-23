"""
MeraDomain AI Studio - One-Time Instagram Login Launcher.
Opens a visible Chromium window so you can sign into Instagram once.
The session is saved permanently in data/browser_profiles/instagram.
"""

import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
PROFILE_DIR = ROOT_DIR.parent / "data" / "browser_profiles" / "instagram"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    print("==================================================================")
    print("  MeraDomain AI Studio - Instagram Authentication")
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
        await page.goto("https://www.instagram.com/accounts/login/")

        print("\n>>> INSTRUCTIONS:")
        print("1. Log in to your @meradomain Instagram account.")
        print("2. If 2FA is prompted, approve it on your phone/email.")
        print("3. Once you see your Instagram feed or profile, simply CLOSE the window.")
        print("4. The AI worker will then publish to Instagram automatically!")
        print("------------------------------------------------------------------\n")

        while True:
            await asyncio.sleep(2)
            if not browser.pages or len(browser.pages) == 0:
                break

if __name__ == "__main__":
    asyncio.run(main())
