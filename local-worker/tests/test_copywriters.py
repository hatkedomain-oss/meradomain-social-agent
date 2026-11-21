"""
Unit tests for Gemini Copywriting & Ideation Engine
"""

import sys
from pathlib import Path
import pytest

WORKER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKER_DIR))

from src.ideation.portfolio_wins import get_random_portfolio_win, PORTFOLIO_WINS
from src.ideation.festival_hook import get_current_festival_hook
from src.copywriters.gemini_copywriter import generate_multi_platform_campaign

def test_portfolio_catalog():
    assert len(PORTFOLIO_WINS) >= 5
    win = get_random_portfolio_win()
    assert "title" in win
    assert "problem" in win
    assert "solution" in win
    assert "metrics" in win

def test_generate_campaign_structure():
    win = PORTFOLIO_WINS[0]
    hook = get_current_festival_hook()
    campaign = generate_multi_platform_campaign(win, hook)

    assert "campaign_title" in campaign
    assert "channels" in campaign
    channels = campaign["channels"]

    # Verify all 4 required platforms are present
    assert "linkedin" in channels
    assert "instagram" in channels
    assert "facebook" in channels
    assert "gmb" in channels

    # Check LinkedIn requirements
    li = channels["linkedin"]
    assert len(li["post_text"]) > 50
    assert "#" in li["hashtags"]

    # Check GMB requirements
    gmb = channels["gmb"]
    assert len(gmb["post_text"]) > 30
    assert gmb.get("cta_type") in ["LEARN_MORE", "CALL_NOW", "VISIT_WEBSITE"]
