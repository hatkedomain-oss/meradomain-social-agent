"""
Unit tests for Pillow Branded Visual Engine
"""

import sys
from pathlib import Path
from PIL import Image
import pytest

# Ensure local-worker root is in sys.path
WORKER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKER_DIR))

from src.visuals.template_engine import render_social_plate
from src.visuals.branding_tokens import DIM_SQUARE, DIM_PORTRAIT, DIM_LANDSCAPE

def test_render_square_plate():
    path = render_social_plate(
        headline="Sub-Second Next.js 15 Enterprise Portal",
        subheadline="Achieved 99 Performance Score & 44% Lead Lift",
        category="Case Study",
        aspect="square",
        output_filename="test_square.png"
    )
    assert path.exists()
    with Image.open(path) as img:
        assert img.size == DIM_SQUARE

def test_render_portrait_plate():
    path = render_social_plate(
        headline="Headless E-Commerce Flagship",
        subheadline="3.8x Mobile Conversion Rate with Custom Checkout",
        category="E-Commerce",
        aspect="portrait",
        output_filename="test_portrait.png"
    )
    assert path.exists()
    with Image.open(path) as img:
        assert img.size == DIM_PORTRAIT

def test_render_landscape_plate():
    path = render_social_plate(
        headline="Autonomous AI Customer Inbound Agents",
        subheadline="24/7 Instant Lead Qualification on Auto-Pilot",
        category="AI Automation",
        aspect="landscape",
        output_filename="test_landscape.png"
    )
    assert path.exists()
    with Image.open(path) as img:
        assert img.size == DIM_LANDSCAPE
