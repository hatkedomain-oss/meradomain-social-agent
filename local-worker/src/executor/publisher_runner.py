"""
MeraDomain Social Agent - Production Execution Runner
Automates browser publishing for Facebook, LinkedIn, Instagram, and GMB
using authenticated persistent browser profiles.
"""

import os
import sys
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import httpx

try:
    from config import settings
except ImportError:
    try:
        from ..config import settings
    except ImportError:
        from ...config import settings

try:
    from ..sync.cpanel_client import CpanelClient
except ImportError:
    from src.sync.cpanel_client import CpanelClient

logger = logging.getLogger("publisher_runner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ExecutionRunner:
    def __init__(self):
        self.client = CpanelClient()
        self.screenshots_dir = settings.BASE_DIR / "outputs" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        # Point to persistent profiles
        self.profiles_dir = settings.BROWSER_PROFILES_DIR

    async def run_due_publishing_cycle(self) -> int:
        """Queries cPanel for approved due posts and executes them."""
        logger.info("Connecting to cPanel queue for due approved posts...")
        try:
            due_posts = self.client.fetch_due_posts()
        except Exception as e:
            logger.error(f"Failed to query cPanel API: {e}")
            return 0

        if not due_posts:
            logger.info("No approved posts currently due for publication.")
            return 0

        logger.info(f"Found {len(due_posts)} post(s) ready to publish.")
        published_count = 0

        for post in due_posts:
            post_id = post["id"]
            platform = post["platform"]
            logger.info(f"\n=======================================================")
            logger.info(f"  Dispatching Post #{post_id} to [{platform.upper()}]")
            logger.info(f"=======================================================")

            # Download or locate media image
            media_path = await self._resolve_media_file(post)

            try:
                if platform == "facebook":
                    success, post_url, err = await self._publish_facebook(post, media_path)
                elif platform == "linkedin":
                    success, post_url, err = await self._publish_linkedin(post, media_path)
                elif platform == "instagram":
                    success, post_url, err = await self._publish_instagram(post, media_path)
                elif platform == "gmb":
                    success, post_url, err = await self._publish_gmb(post, media_path)
                else:
                    success, post_url, err = False, "", f"Unsupported platform: {platform}"

                if success:
                    self.client.mark_published(post_id, post_url)
                    logger.info(f"[SUCCESS] Post #{post_id} marked as PUBLISHED: {post_url}")
                    published_count += 1
                else:
                    self.client.mark_failed(post_id, err or "Publishing failed")
                    logger.warning(f"[FAILED] Post #{post_id}: {err}")

            except Exception as e:
                logger.error(f"Unexpected error publishing Post #{post_id}: {e}")
                self.client.mark_failed(post_id, str(e))

            # Clean up temp media if downloaded
            if media_path and "temp_" in media_path.name:
                try:
                    media_path.unlink()
                except Exception:
                    pass

        return published_count

    async def _resolve_media_file(self, post: Dict[str, Any]) -> Optional[Path]:
        """Resolves local media file or downloads from cPanel public URL."""
        media_url = post.get("media_url", "")
        if not media_url:
            return None

        # Check local outputs directory first
        filename = media_url.split("/")[-1]
        local_cand = settings.OUTPUTS_DIR / filename
        if local_cand.exists():
            return local_cand

        # Check parent banners or carousels
        parent_cand = settings.BASE_DIR.parent / "data" / "banners" / filename
        if parent_cand.exists():
            return parent_cand

        # Download from web URL
        if media_url.startswith("http"):
            try:
                temp_file = Path(tempfile.gettempdir()) / f"temp_{filename}"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.get(media_url)
                    if res.status_code == 200:
                        temp_file.write_bytes(res.content)
                        return temp_file
            except Exception as e:
                logger.warning(f"Could not download remote media {media_url}: {e}")

        return None

    async def _publish_facebook(self, post: Dict[str, Any], media_path: Optional[Path]) -> Tuple[bool, str, str]:
        """Publishes post + image to Facebook Page using saved session."""
        profile_path = self.profiles_dir / "facebook"
        page_id = "629831713740050"  # MeraDomain Facebook Page ID
        message = post["post_text"]
        if post.get("hashtags"):
            message += "\n\n" + post["hashtags"]

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                str(profile_path),
                headless=False,  # Visible or headless
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await context.new_page()

            target_url = f"https://www.facebook.com/{page_id}"
            logger.info(f"Navigating to Facebook Page: {target_url}...")
            await page.goto(target_url, timeout=35000, wait_until="domcontentloaded")
            await asyncio.sleep(4)

            # Check login state
            content = await page.content()
            if "login" in page.url or ('name="email"' in content and 'name="pass"' in content):
                await context.close()
                return False, "", "Facebook session expired. Please sign into Facebook once in Chrome."

            # Switch to Page profile if needed
            switch_btn = await page.query_selector('div[role="button"]:has-text("Switch Now"), button:has-text("Switch Now")')
            if switch_btn and await switch_btn.is_visible():
                logger.info("Switching to Page management profile...")
                try:
                    await switch_btn.click()
                    await asyncio.sleep(4)
                except Exception:
                    pass

            # Find 'What's on your mind' or 'Create post'
            composer = None
            for sel in [
                'div[role="button"]:has-text("What\'s on your mind")',
                'div[role="button"]:has-text("Photo/video")',
                'div[aria-label*="What\'s on your mind" i]'
            ]:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    composer = el
                    break

            if not composer:
                # Try navigating to feed
                await page.goto("https://www.facebook.com/", timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(3)
                composer = await page.query_selector('div[role="button"]:has-text("What\'s on your mind")')

            if not composer:
                screenshot = self.screenshots_dir / f"fb_fail_{post['id']}.png"
                await page.screenshot(path=str(screenshot))
                await context.close()
                return False, "", "Could not locate Facebook post composer."

            await composer.click()
            await asyncio.sleep(3)

            # Find dialog
            dialog = await page.query_selector('div[role="dialog"]')
            if not dialog:
                dialog = page

            # Attach media if available
            if media_path and media_path.exists():
                file_input = await dialog.query_selector('input[type="file"]')
                if not file_input:
                    photo_icon = await dialog.query_selector('div[aria-label*="Photo/video" i], div[role="button"]:has-text("Photo/video")')
                    if photo_icon:
                        await photo_icon.click()
                        await asyncio.sleep(2)
                    file_input = await dialog.query_selector('input[type="file"]')

                if file_input:
                    await file_input.set_input_files(str(media_path))
                    logger.info("Attached image file. Waiting for preview...")
                    await asyncio.sleep(5)

            # Enter post text
            text_box = await dialog.query_selector('div[role="textbox"], div[contenteditable="true"]')
            if text_box:
                await text_box.click()
                await page.keyboard.type(message, delay=10)
                await asyncio.sleep(2)

            # Click Post button
            post_btn = await dialog.query_selector('div[aria-label="Post"][role="button"], div[role="button"]:has-text("Post"), button:has-text("Post")')
            if post_btn and await post_btn.is_visible():
                await post_btn.click()
                logger.info("Clicked Post button. Waiting 8s for submission...")
                await asyncio.sleep(8)
                await context.close()
                return True, f"https://www.facebook.com/{page_id}", ""

            await context.close()
            return False, "", "Could not click the Facebook Post submit button."

    async def _publish_linkedin(self, post: Dict[str, Any], media_path: Optional[Path]) -> Tuple[bool, str, str]:
        """Publishes post + image to LinkedIn company/personal feed."""
        profile_path = self.profiles_dir / "linkedin"
        message = post["post_text"]
        if post.get("hashtags"):
            message += "\n\n" + post["hashtags"]

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                str(profile_path),
                headless=False,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await context.new_page()

            # Target MeraDomain company admin or main feed
            company_url = "https://www.linkedin.com/company/3539218/admin/page-posts/published/"
            logger.info(f"Navigating to LinkedIn Company Page: {company_url}...")
            try:
                await page.goto(company_url, timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(3)
            except Exception:
                await page.goto("https://www.linkedin.com/feed/", timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(3)

            # Check if session expired
            content = await page.content()
            if "login" in page.url or 'id="username"' in content or "Sign in" in await page.title():
                await context.close()
                return False, "", "LinkedIn session expired. Run 'python launch_li_login.py' once to authenticate."

            # Click 'Start a post'
            start_btn = None
            for sel in [
                'button:has-text("Create a post")',
                'button:has-text("Start a post")',
                'div.share-box-feed-entry__trigger',
                'button.share-box-feed-entry__trigger'
            ]:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    start_btn = el
                    break

            if not start_btn:
                screenshot = self.screenshots_dir / f"li_fail_{post['id']}.png"
                await page.screenshot(path=str(screenshot))
                await context.close()
                return False, "", "Could not find 'Start a post' button on LinkedIn."

            await start_btn.click()
            await asyncio.sleep(3)

            # Dialog container
            dialog = await page.query_selector('div[role="dialog"], div.share-box-modal')
            if not dialog:
                dialog = page

            # Attach media if available
            if media_path and media_path.exists():
                file_input = await dialog.query_selector('input[type="file"]')
                if not file_input:
                    # Look for media icon button
                    media_btn = await dialog.query_selector('button[aria-label*="Add media" i], button[aria-label*="photo" i]')
                    if media_btn:
                        await media_btn.click()
                        await asyncio.sleep(2)
                    file_input = await page.query_selector('input[type="file"]')

                if file_input:
                    await file_input.set_input_files(str(media_path))
                    await asyncio.sleep(3)
                    # Click 'Next' on image preview if prompted
                    next_btn = await dialog.query_selector('button:has-text("Next"), div[role="button"]:has-text("Next")')
                    if next_btn and await next_btn.is_visible():
                        await next_btn.click()
                        await asyncio.sleep(2)

            # Enter post text
            text_editor = await dialog.query_selector('div[role="textbox"], div[contenteditable="true"], div.ql-editor')
            if text_editor:
                await text_editor.click()
                await page.keyboard.type(message, delay=10)
                await asyncio.sleep(2)

            # Click Post button
            submit_btn = await dialog.query_selector('button:has-text("Post"), button.share-actions__primary-action')
            if submit_btn and await submit_btn.is_visible():
                await submit_btn.click()
                logger.info("Clicked LinkedIn Post button. Waiting 6s...")
                await asyncio.sleep(6)
                await context.close()
                return True, "https://www.linkedin.com/company/meradomain", ""

            await context.close()
            return False, "", "Could not click LinkedIn submit button."

    async def _publish_instagram(self, post: Dict[str, Any], media_path: Optional[Path]) -> Tuple[bool, str, str]:
        """Publishes to Instagram via Meta Business Suite or web composer."""
        profile_path = self.profiles_dir / "facebook"
        message = post["post_text"]
        if post.get("hashtags"):
            message += "\n\n" + post["hashtags"]

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                str(profile_path),
                headless=False,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await context.new_page()

            # Meta Business Suite Composer
            composer_url = "https://business.facebook.com/latest/composer"
            logger.info(f"Navigating to Meta Business Suite: {composer_url}...")
            try:
                await page.goto(composer_url, timeout=35000, wait_until="domcontentloaded")
                await asyncio.sleep(5)
            except Exception:
                await context.close()
                return False, "", "Meta Business Suite is unreachable."

            if "login" in page.url:
                await context.close()
                return False, "", "Meta Business session expired. Please log into Facebook in Chrome."

            # If image exists, attach
            if media_path and media_path.exists():
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(str(media_path))
                    await asyncio.sleep(4)

            # Fill caption
            caption_box = await page.query_selector('div[role="textbox"], textarea[placeholder*="text" i]')
            if caption_box:
                await caption_box.click()
                await page.keyboard.type(message, delay=10)
                await asyncio.sleep(2)

            # Click Publish
            pub_btn = await page.query_selector('div[role="button"]:has-text("Publish"), button:has-text("Publish")')
            if pub_btn and await pub_btn.is_visible():
                await pub_btn.click()
                await asyncio.sleep(6)
                await context.close()
                return True, "https://www.instagram.com/meradomain", ""

            await context.close()
            return False, "", "Could not click Publish button in Meta Business Suite."

    async def _publish_gmb(self, post: Dict[str, Any], media_path: Optional[Path]) -> Tuple[bool, str, str]:
        """Publishes local SEO update to Google Business Profile."""
        profile_path = self.profiles_dir / "gmb"
        profile_path.mkdir(parents=True, exist_ok=True)
        message = post["post_text"]

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                str(profile_path),
                headless=False,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await context.new_page()

            logger.info("Navigating to Google Business Profile manager...")
            await page.goto("https://business.google.com/", timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(4)

            if "accounts.google.com" in page.url or "signin" in page.url:
                await context.close()
                return False, "", "Google Business session not signed in. Please log in with your Google Workspace account."

            # Click 'Add update'
            add_update_btn = await page.query_selector('button:has-text("Add update"), div[role="button"]:has-text("Add update")')
            if add_update_btn and await add_update_btn.is_visible():
                await add_update_btn.click()
                await asyncio.sleep(3)

                # Attach photo
                if media_path and media_path.exists():
                    f_input = await page.query_selector('input[type="file"]')
                    if f_input:
                        await f_input.set_input_files(str(media_path))
                        await asyncio.sleep(3)

                # Description
                desc_input = await page.query_selector('textarea, div[role="textbox"]')
                if desc_input:
                    await desc_input.click()
                    await page.keyboard.type(message, delay=10)
                    await asyncio.sleep(2)

                # CTA button selection if available
                # Click Post
                submit = await page.query_selector('button:has-text("Post"), div[role="button"]:has-text("Post")')
                if submit and await submit.is_visible():
                    await submit.click()
                    await asyncio.sleep(5)
                    await context.close()
                    return True, "https://www.google.com/maps/place/MeraDomain", ""

            await context.close()
            return False, "", "Could not complete GMB update. Please ensure Google Business session is active."

def run_publisher_sync():
    runner = ExecutionRunner()
    asyncio.run(runner.run_due_publishing_cycle())

if __name__ == "__main__":
    run_publisher_sync()
