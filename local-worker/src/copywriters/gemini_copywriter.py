"""
MeraDomain Social Agent - Gemini AI Platform Copywriter
Generates tailored copywriting for LinkedIn, Instagram, Facebook, and Google Business Profile.
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx
try:
    from config import settings
except ImportError:
    try:
        from ..config import settings
    except ImportError:
        from ...config import settings

logger = logging.getLogger("gemini_copywriter")
logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Lead Digital Brand Strategist and Social Media Director for MeraDomain (https://meradomain.in • "Build. Launch. Grow.").

ABOUT MERADOMAIN:
- Premier digital engineering studio specializing in bespoke web development (Next.js, React Server Components), high-converting e-commerce flagships (Headless Shopify), cross-platform mobile apps (Flutter), enterprise custom software, and autonomous AI automation agents.
- Based in Connaught Place, New Delhi, India. Serving forward-thinking Indian and international enterprises.
- Core Identity: High-performance engineering, luxury Swiss aesthetics, conversion rate architecture, zero template bloat.

YOUR MISSION:
Given a portfolio win or tech trend, synthesize a cohesive multi-channel campaign with distinct, platform-optimized copywriting across our 4 core networks:

1. LINKEDIN (B2B Thought Leadership):
   - Hook: Provocative executive or engineering insight.
   - Body: Problem, technical breakdown, quantifiable business ROI. Use clean line breaks and bullet points.
   - Tone: Visionary, analytical, peer-level executive.
   - Hashtags: 3-5 high-relevance B2B tags (e.g., #WebEngineering #Nextjs #B2B #MeraDomain #BuildLaunchGrow).
   - CTA: Direct reference to meradomain.in.

2. INSTAGRAM (Visual-First & High Engagement):
   - Hook: Bold, scroll-stopping statement in the first 2 lines.
   - Body: Slide breakdown concept (e.g. Slide 1 to 5) or high-energy narrative.
   - Tone: Modern, aspirational, dynamic.
   - CTA: "Save this post for your next website overhaul 📌 • Link in bio to book an engineering consult."
   - Hashtags: 15-20 curated tags (#webdesign #nextjs #ecommerce #delhincr #delhibusiness #meradomain #appdevelopment).

3. FACEBOOK (Community & Practical Business Growth):
   - Hook: Relatable business dilemma faced by founders or MSMEs.
   - Body: Conversational storytelling showing the real-world impact of custom digital engineering over generic templates.
   - Tone: Warm, authoritative, practical.
   - CTA: Direct link to https://meradomain.in with a clear invitation to discuss projects.

4. GOOGLE BUSINESS PROFILE (Local SEO & Direct Action):
   - Focus: Local SEO ranking signals for Delhi NCR & India.
   - Keywords: Web design company in Connaught Place New Delhi, Next.js development, custom software, AI agents.
   - Length: Concise, punchy 100-150 words highlighting reliability, 20+ years expertise, 200+ projects delivered.
   - CTA Type: "LEARN_MORE" or "CALL_NOW".
   - CTA Link: "https://meradomain.in".

Return your response ONLY as valid, parsable JSON matching this schema:
{
  "campaign_title": "string",
  "topic": "string",
  "visual_headline": "string (Short, punchy 4-7 words for graphic plate)",
  "visual_subheadline": "string (10-15 words subtitle for graphic plate)",
  "visual_category": "string (e.g. Engineering, Architecture, E-Commerce, Case Study)",
  "channels": {
    "linkedin": {
      "post_text": "string",
      "hashtags": "string",
      "cta_link": "https://meradomain.in"
    },
    "instagram": {
      "post_text": "string",
      "hashtags": "string",
      "cta_link": "https://meradomain.in"
    },
    "facebook": {
      "post_text": "string",
      "hashtags": "string",
      "cta_link": "https://meradomain.in"
    },
    "gmb": {
      "post_text": "string",
      "cta_type": "LEARN_MORE",
      "cta_link": "https://meradomain.in"
    }
  }
}
"""

def generate_multi_platform_campaign(portfolio_win: Dict[str, Any], festival_hook: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calls Gemini API or falls back to robust curated synthesis."""
    user_prompt = f"PORTFOLIO CASE STUDY:\nTitle: {portfolio_win.get('title')}\nCategory: {portfolio_win.get('category')}\nIndustry: {portfolio_win.get('industry')}\nMetrics: {portfolio_win.get('metrics')}\nProblem: {portfolio_win.get('problem')}\nSolution: {portfolio_win.get('solution')}\nKey Takeaway: {portfolio_win.get('takeaway')}\n"

    if festival_hook:
        user_prompt += f"\nTIMELY CALENDAR HOOK:\nEvent: {festival_hook.get('name')}\nAngle: {festival_hook.get('angle')}\nHook Idea: {festival_hook.get('hook')}\n"

    api_key = settings.GEMINI_API_KEY
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": SYSTEM_PROMPT + "\n\n" + user_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.6,
                    "responseMimeType": "application/json"
                }
            }

            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0]["content"]["parts"][0]["text"]
                        parsed = json.loads(raw_text)
                        logger.info("Successfully generated campaign via Gemini API")
                        return parsed
                else:
                    logger.warning(f"Gemini API returned status {res.status_code}: {res.text}. Falling back to template synthesis.")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}. Falling back to template synthesis.")

    # High-quality fallback synthesis if API key is not yet set or network issue
    return synthesize_fallback_campaign(portfolio_win, festival_hook)

def synthesize_fallback_campaign(win: Dict[str, Any], hook: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    title = win.get("title", "High-Performance Digital Architecture")
    metrics = win.get("metrics", "Sub-Second Load Times • 40%+ Lead Increase")
    problem = win.get("problem", "Outdated website templates throttling business growth.")
    solution = win.get("solution", "Tailored Next.js 15 web application engineered for maximum conversion.")

    return {
        "campaign_title": f"MeraDomain Case Study: {title}",
        "topic": win.get("category", "Web Engineering"),
        "visual_headline": title,
        "visual_subheadline": metrics,
        "visual_category": win.get("category", "Bespoke Engineering"),
        "channels": {
            "linkedin": {
                "post_text": f"Why do fast-scaling brands abandon off-the-shelf templates in 2026?\n\nBecause performance is directly correlated with enterprise revenue.\n\nCase in point: {title}.\n\n• The Bottleneck: {problem}\n• The Engineering: {solution}\n• The Measured Impact: {metrics}\n\nYour website is your premier 24/7 executive office. When ambitious clients evaluate your capabilities, an off-the-shelf $50 theme sends the wrong signal.\n\nAt MeraDomain (https://meradomain.in), we engineer bespoke digital platforms built on clean React Server Components, zero bloat, and sub-second edge delivery.\n\nBuild. Launch. Grow.",
                "hashtags": "#WebEngineering #Nextjs #B2B #MeraDomain #BuildLaunchGrow #EnterpriseSoftware",
                "cta_link": "https://meradomain.in"
            },
            "instagram": {
                "post_text": f"Is your website helping you win high-ticket clients or quietly costing you revenue? ⚡\n\nHere is how we overhauled {title} to achieve {metrics}.\n\nSwipe through the architecture breakdown ➔\n\n📌 Slide 1: The Problem — {problem}\n📌 Slide 2: Why templates fail under load\n📌 Slide 3: The Next.js 15 Bespoke Stack\n📌 Slide 4: Real metrics: {metrics}\n📌 Slide 5: The blueprint to scale your digital presence\n\nSave this for your next website overhaul.\n\nLink in bio (@meradomain) to schedule a consultation with our engineering team.",
                "hashtags": "#webdesign #customsoftware #agency #nextjs #delhincr #delhibusiness #meradomain #buildlaunchgrow #ecommerce #developer #startupindia",
                "cta_link": "https://meradomain.in"
            },
            "facebook": {
                "post_text": f"Every ambitious business reaches a point where generic website templates stop working.\n\nWe recently partnered with a leadership team facing this exact challenge: {problem}\n\nInstead of patching outdated plugins, our engineering team at MeraDomain built a tailor-made digital platform ({solution}).\n\nThe result? {metrics}.\n\nYour brand deserves digital infrastructure that converts visitors into long-term clients from the first click.\n\nReady to elevate your digital presence? Discover what bespoke engineering can do for your business at https://meradomain.in.\n\nBuild. Launch. Grow.",
                "hashtags": "#MeraDomain #WebDevelopment #BusinessGrowth #DelhiNCR #CustomSoftware #BuildLaunchGrow",
                "cta_link": "https://meradomain.in"
            },
            "gmb": {
                "post_text": f"Looking for top-tier website design and custom software development in Delhi NCR? MeraDomain (Connaught Place, New Delhi) specializes in high-converting Next.js web applications, mobile apps, and autonomous AI automation. Over 200+ projects delivered with 20+ years of digital excellence. Elevate your brand today.",
                "cta_type": "LEARN_MORE",
                "cta_link": "https://meradomain.in"
            }
        }
    }
