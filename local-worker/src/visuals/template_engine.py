"""
MeraDomain Social Agent - Pillow Branded Visual Plate Engine
Generates 1:1, 4:5, and 1.91:1 high-resolution graphics for social publishing.
"""

from pathlib import Path
from typing import Tuple, Optional
import textwrap
from PIL import Image, ImageDraw, ImageFont

try:
    from config import settings
except ImportError:
    try:
        from ..config import settings
    except ImportError:
        from ...config import settings

try:
    from .branding_tokens import (
        BG_OBSIDIAN, BG_CARD, BG_CARD_LIGHT, GOLD_PRIMARY, GOLD_LIGHT,
        EMERALD_ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
        BORDER_CARD, DIM_SQUARE, DIM_PORTRAIT, DIM_LANDSCAPE
    )
except ImportError:
    from src.visuals.branding_tokens import (
        BG_OBSIDIAN, BG_CARD, BG_CARD_LIGHT, GOLD_PRIMARY, GOLD_LIGHT,
        EMERALD_ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
        BORDER_CARD, DIM_SQUARE, DIM_PORTRAIT, DIM_LANDSCAPE
    )

def get_best_font(font_size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Finds best available system or local font."""
    font_names = [
        "PlusJakartaSans-Bold.ttf" if bold else "PlusJakartaSans-Regular.ttf",
        "Inter-Bold.ttf" if bold else "Inter-Regular.ttf",
        "seguiui.ttf" if not bold else "segoeuib.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "Helvetica.ttc",
        "Arial.ttf"
    ]

    for name in font_names:
        # Check local fonts directory
        local_path = settings.FONTS_DIR / name
        if local_path.exists():
            try:
                return ImageFont.truetype(str(local_path), font_size)
            except Exception:
                pass

        # Check Windows system fonts
        win_path = Path("C:/Windows/Fonts") / name
        if win_path.exists():
            try:
                return ImageFont.truetype(str(win_path), font_size)
            except Exception:
                pass

    return ImageFont.load_default()

def render_social_plate(
    headline: str,
    subheadline: str,
    category: str = "Bespoke Web Engineering",
    metrics_badge: Optional[str] = None,
    aspect: str = "square",
    output_filename: Optional[str] = None
) -> Path:
    """
    Renders a premium MeraDomain branded plate in 1:1, 4:5, or 1.91:1.
    """
    if aspect == "portrait":
        width, height = DIM_PORTRAIT
    elif aspect == "landscape":
        width, height = DIM_LANDSCAPE
    else:
        width, height = DIM_SQUARE

    # 1. Base Canvas (Deep Obsidian)
    img = Image.new("RGB", (width, height), BG_OBSIDIAN)
    draw = ImageDraw.Draw(img)

    # 2. Subtle Luxury Grid Lines (Tech & Engineering Signature)
    grid_spacing = 90
    grid_color = (18, 24, 40)
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 3. Ambient Gold Accent Glow in Top-Right
    glow_color = (35, 29, 15)
    draw.ellipse([width - 300, -100, width + 200, 400], fill=glow_color)

    # 4. Central Executive Card Container
    padding_x = int(width * 0.08)
    padding_y = int(height * 0.08)
    card_rect = [padding_x, padding_y, width - padding_x, height - padding_y]
    draw.rounded_rectangle(card_rect, radius=24, fill=BG_CARD, outline=BORDER_CARD, width=2)

    # Subtle inner gold border line on the card
    draw.rounded_rectangle(
        [padding_x + 2, padding_y + 2, width - padding_x - 2, height - padding_y - 2],
        radius=22, outline=(40, 32, 16), width=1
    )

    # 5. MeraDomain Brand Header inside Card
    header_y = padding_y + 40
    header_x = padding_x + 50

    # Load Brand Logo Badge if available
    logo_path = settings.BRAND_DIR / "meradomain-logo-badge.png"
    if not logo_path.exists():
        logo_path = settings.BRAND_DIR / "meradomain-logo-white.png"

    logo_placed = False
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Resize proportionally to height ~52px
            aspect_ratio = logo.width / logo.height
            logo_height = 52
            logo_width = int(logo_height * aspect_ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            img.paste(logo, (header_x, header_y), logo)
            logo_placed = True
            header_x += logo_width + 25
        except Exception:
            pass

    # Header Brand Text
    font_brand = get_best_font(30, bold=True)
    draw.text((header_x, header_y + 4), "MeraDomain", font=font_brand, fill=TEXT_PRIMARY)

    font_tagline = get_best_font(18, bold=False)
    draw.text((header_x, header_y + 36), "Build. Launch. Grow.", font=font_tagline, fill=GOLD_PRIMARY)

    # Category Pill on Top Right
    font_cat = get_best_font(18, bold=True)
    cat_text = category.upper()
    cat_bbox = draw.textbbox((0, 0), cat_text, font=font_cat)
    cat_w = cat_bbox[2] - cat_bbox[0]
    pill_right = width - padding_x - 50
    pill_left = pill_right - cat_w - 30
    draw.rounded_rectangle([pill_left, header_y + 10, pill_right, header_y + 46], radius=18, fill=BG_CARD_LIGHT, outline=GOLD_PRIMARY, width=1)
    draw.text((pill_left + 15, header_y + 19), cat_text, font=font_cat, fill=GOLD_LIGHT)

    # 6. Headline (Auto-Wrapped, Bold Swiss Typography)
    content_y = header_y + 120
    font_headline = get_best_font(52 if height >= 1080 else 42, bold=True)
    
    # Wrap headline text according to card width
    wrap_chars = 24 if width == 1080 else 32
    wrapped_lines = textwrap.wrap(headline, width=wrap_chars)
    
    for line in wrapped_lines[:3]:  # max 3 lines
        draw.text((padding_x + 50, content_y), line, font=font_headline, fill=TEXT_PRIMARY)
        content_y += 66 if height >= 1080 else 54

    # 7. Subheadline / Core Narrative
    content_y += 20
    font_sub = get_best_font(26 if height >= 1080 else 22, bold=False)
    sub_lines = textwrap.wrap(subheadline, width=44 if width >= 1080 else 52)
    for line in sub_lines[:3]:
        draw.text((padding_x + 50, content_y), line, font=font_sub, fill=TEXT_SECONDARY)
        content_y += 38

    # 8. Performance Callout Box (Metrics / Takeaway)
    badge_text = metrics_badge or "✓ Next.js 15 Bespoke Engineering • 99+ Core Web Vitals"
    box_y = height - padding_y - 150
    box_rect = [padding_x + 50, box_y, width - padding_x - 50, box_y + 60]
    draw.rounded_rectangle(box_rect, radius=14, fill=BG_CARD_LIGHT, outline=(24, 60, 45), width=1)
    
    font_badge = get_best_font(20, bold=True)
    draw.text((padding_x + 75, box_y + 18), badge_text, font=font_badge, fill=EMERALD_ACCENT)

    # 9. Bottom Footer Bar (Website & Verification)
    footer_y = height - padding_y - 60
    font_footer = get_best_font(18, bold=True)
    draw.text((padding_x + 50, footer_y), "meradomain.in", font=font_footer, fill=GOLD_PRIMARY)

    draw.text((width - padding_x - 300, footer_y), "Connaught Place, New Delhi", font=get_best_font(16), fill=TEXT_MUTED)

    # Save output
    if not output_filename:
        import time
        output_filename = f"plate_{aspect}_{int(time.time())}.png"

    out_path = settings.OUTPUTS_DIR / output_filename
    img.save(out_path, format="PNG", quality=95)
    return out_path
