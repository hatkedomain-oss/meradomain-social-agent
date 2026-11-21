"""
MeraDomain Social Agent - Local Worker Configuration
Brand: MeraDomain (https://meradomain.in • Build. Launch. Grow.)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Load .env from local-worker or root directory
load_dotenv(BASE_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "MeraDomain Social AI Worker"
    BASE_DIR: Path = BASE_DIR
    ASSETS_DIR: Path = BASE_DIR / "assets"
    BRAND_DIR: Path = ASSETS_DIR / "brand"
    FONTS_DIR: Path = ASSETS_DIR / "fonts"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    
    # Browser session profiles path (can reuse parent or local)
    BROWSER_PROFILES_DIR: Path = ROOT_DIR.parent / "data" / "browser_profiles"
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Optional fallback LLM providers
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    # cPanel Web App REST API Credentials
    CPANEL_API_URL: str = os.getenv("CPANEL_API_URL", "https://social.meradomain.in/api")
    CPANEL_API_KEY: str = os.getenv("CPANEL_API_KEY", "md_sec_live_9a72df81c8b74635a821038")

    # MeraDomain Standard Business Identity (NAP)
    BRAND_PROFILE = {
        "name": "MeraDomain",
        "tagline": "Build. Launch. Grow.",
        "website": "https://meradomain.in",
        "supersite_url": "https://www.meradomain.com",
        "email": "sales@meradomain.in",
        "phone": "+91-9717075888",
        "address": "Connaught Place, New Delhi, Delhi, India - 110001",
        "city": "New Delhi",
        "state": "Delhi",
        "country": "India",
        "pincode": "110001",
        "stats": {
            "projects_delivered": "200+",
            "rating": "4.8★",
            "experience": "20+ Years"
        },
        "services": [
            "Bespoke Website Design and Next.js Development",
            "High-Converting E-commerce Flagships (Headless & Shopify)",
            "Mobile Application Development (Flutter & React Native)",
            "Custom Web Applications & Enterprise Software Portals",
            "Autonomous AI Agents & Business Automation",
            "Digital Transformation & Cloud Infrastructure"
        ],
        "social_links": {
            "linkedin": "https://www.linkedin.com/company/meradomain",
            "instagram": "https://www.instagram.com/meradomain",
            "facebook": "https://www.facebook.com/meradomain"
        }
    }

settings = Settings()
settings.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
