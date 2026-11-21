"""
MeraDomain Social Agent - Unified Worker CLI
Commands:
  python run_worker.py --generate [--sync]
  python run_worker.py --batch 5 [--sync]
  python run_worker.py --publish
"""

import sys
import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import settings
from src.ideation.portfolio_wins import get_random_portfolio_win, get_portfolio_win_by_id, PORTFOLIO_WINS
from src.ideation.festival_hook import get_current_festival_hook
from src.copywriters.gemini_copywriter import generate_multi_platform_campaign
from src.visuals.template_engine import render_social_plate
from src.sync.cpanel_client import CpanelClient
from src.executor.publisher_runner import ExecutionRunner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("worker_cli")

def build_campaign(win: dict, hook: dict = None, sync: bool = False):
    logger.info(f"Synthesizing campaign for: '{win['title']}'...")
    
    # 1. Generate multi-platform copy via Gemini
    campaign = generate_multi_platform_campaign(win, hook)
    
    # 2. Render branded visual plates
    headline = campaign.get("visual_headline", win["title"])
    subheadline = campaign.get("visual_subheadline", win["metrics"])
    category = campaign.get("visual_category", win["category"])
    
    timestamp = int(datetime.now().timestamp())
    square_plate = render_social_plate(headline, subheadline, category, aspect="square", output_filename=f"plate_sq_{timestamp}.png")
    landscape_plate = render_social_plate(headline, subheadline, category, aspect="landscape", output_filename=f"plate_ls_{timestamp}.png")
    
    logger.info(f"Rendered Visual Plates:\n  Square: {square_plate}\n  Landscape: {landscape_plate}")

    # 3. Construct API bundle
    client = CpanelClient()
    uploaded_sq_url = f"/uploads/{square_plate.name}"
    uploaded_ls_url = f"/uploads/{landscape_plate.name}"

    if sync:
        logger.info("Uploading visual assets to cPanel web server...")
        try:
            uploaded_sq_url = client.upload_media(square_plate)
            uploaded_ls_url = client.upload_media(landscape_plate)
            logger.info("Assets uploaded successfully.")
        except Exception as e:
            logger.warning(f"Could not upload via API ({e}). Using local relative path.")

    # Base schedule: staggered over next few days
    base_time = datetime.now() + timedelta(hours=3)

    posts_bundle = []
    channels = campaign.get("channels", {})

    # LinkedIn
    if "linkedin" in channels:
        posts_bundle.append({
            "platform": "linkedin",
            "post_text": channels["linkedin"]["post_text"],
            "hashtags": channels["linkedin"].get("hashtags", ""),
            "cta_link": channels["linkedin"].get("cta_link", "https://meradomain.in"),
            "cta_type": "LEARN_MORE",
            "media_url": uploaded_ls_url,
            "media_aspect": "landscape",
            "scheduled_at": (base_time + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Instagram
    if "instagram" in channels:
        posts_bundle.append({
            "platform": "instagram",
            "post_text": channels["instagram"]["post_text"],
            "hashtags": channels["instagram"].get("hashtags", ""),
            "cta_link": channels["instagram"].get("cta_link", "https://meradomain.in"),
            "cta_type": "VISIT_WEBSITE",
            "media_url": uploaded_sq_url,
            "media_aspect": "square",
            "scheduled_at": (base_time + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Facebook
    if "facebook" in channels:
        posts_bundle.append({
            "platform": "facebook",
            "post_text": channels["facebook"]["post_text"],
            "hashtags": channels["facebook"].get("hashtags", ""),
            "cta_link": channels["facebook"].get("cta_link", "https://meradomain.in"),
            "cta_type": "LEARN_MORE",
            "media_url": uploaded_sq_url,
            "media_aspect": "square",
            "scheduled_at": (base_time + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
        })

    # Google Business Profile (GMB)
    if "gmb" in channels:
        posts_bundle.append({
            "platform": "gmb",
            "post_text": channels["gmb"]["post_text"],
            "hashtags": "",
            "cta_link": channels["gmb"].get("cta_link", "https://meradomain.in"),
            "cta_type": channels["gmb"].get("cta_type", "LEARN_MORE"),
            "media_url": uploaded_sq_url,
            "media_aspect": "square",
            "scheduled_at": (base_time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        })

    payload = {
        "campaign": {
            "title": campaign.get("campaign_title", win["title"]),
            "topic": campaign.get("topic", win["category"]),
            "source_type": "PORTFOLIO_WIN",
            "notes": f"Generated via Gemini AI for {win['industry']}"
        },
        "posts": posts_bundle
    }

    if sync:
        logger.info("Syncing campaign to cPanel approval portal...")
        try:
            res = client.sync_campaign(payload)
            logger.info(f"Sync complete! Created Campaign #{res.get('campaign_id')} with {res.get('inserted_count')} pending posts.")
        except Exception as e:
            logger.error(f"Failed to sync campaign to cPanel: {e}")
    else:
        logger.info("Local dry-run complete. JSON payload preview:")
        print(json.dumps(payload, indent=2))

    return payload

def main():
    parser = argparse.ArgumentParser(description="MeraDomain AI Social Media Worker CLI")
    parser.add_argument("--generate", action="store_true", help="Generate a new campaign from portfolio wins")
    parser.add_argument("--win-id", type=str, help="Specific portfolio win ID")
    parser.add_argument("--batch", type=int, help="Batch generate N campaigns across portfolio topics")
    parser.add_argument("--publish", action="store_true", help="Run due publishing cycle for approved posts")
    parser.add_argument("--sync", action="store_true", help="Sync generated drafts and assets directly to cPanel")

    args = parser.parse_args()

    if args.publish:
        import asyncio
        runner = ExecutionRunner()
        asyncio.run(runner.run_due_publishing_cycle())
        return

    if args.batch:
        hook = get_current_festival_hook()
        for i in range(min(args.batch, len(PORTFOLIO_WINS))):
            win = PORTFOLIO_WINS[i]
            logger.info(f"\n--- Batch {i+1}/{args.batch} ---")
            build_campaign(win, hook, sync=args.sync)
        return

    if args.generate:
        hook = get_current_festival_hook()
        win = get_portfolio_win_by_id(args.win_id) if args.win_id else get_random_portfolio_win()
        build_campaign(win, hook, sync=args.sync)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
