"""
MeraDomain Social Agent - Portfolio Wins & Authority Content Catalog
Source: https://meradomain.in (Build. Launch. Grow.)
"""

import random
from typing import Dict, Any, List

PORTFOLIO_WINS: List[Dict[str, Any]] = [
    {
        "id": "nextjs_enterprise_flagship",
        "title": "Sub-Second Next.js 15 Enterprise Portal",
        "category": "Technology & Innovation",
        "industry": "B2B & Enterprise Software",
        "metrics": "99 Performance Score • Sub-400ms TTFB • 44% Inbound Lead Lift",
        "problem": "Legacy corporate website was bogged down by slow monolith architecture, high server costs, and poor mobile rendering.",
        "solution": "Architected a custom headless Next.js 15 web application with React Server Components, edge-cached static generation, and automated lead ingestion.",
        "takeaway": "Enterprise web platforms must treat performance as a core revenue driver, not a design afterthought.",
        "cta": "Explore Bespoke Web Architecture at meradomain.in"
    },
    {
        "id": "luxury_headless_ecommerce",
        "title": "Headless E-Commerce Flagship with Seamless Checkout",
        "category": "Problem and Solution Content",
        "industry": "D2C Luxury Retail",
        "metrics": "3.8x Mobile Conversion Rate • 62% Drop in Cart Abandonment",
        "problem": "Generic theme was slow, lacked luxury brand personality, and suffered checkout drop-offs on mobile networks in India.",
        "solution": "Built a bespoke, micro-interactive storefront with instant visual swatches, fluid cart slide-over, and instant UPI/Stripe checkout flows.",
        "takeaway": "Luxury buyers demand tactile, frictionless digital shopping experiences that feel as premium as the product itself.",
        "cta": "Transform Your E-Commerce Store at meradomain.in"
    },
    {
        "id": "ai_agent_operations",
        "title": "Autonomous AI Inbound Lead Qualifier Agent",
        "category": "AI Automation",
        "industry": "Consulting & High-Ticket B2B",
        "metrics": "24/7 Instant Qualification • 78% Response Time Reduction",
        "problem": "Sales teams were losing high-intent leads because inquiries came in after hours or went unaddressed for hours.",
        "solution": "Integrated an autonomous AI Agent that instantly qualifies leads, handles initial Q&A, and schedules consultations directly onto the calendar.",
        "takeaway": "Modern sales engines don't sleep. AI agents capture intent at the exact moment a prospect is paying attention.",
        "cta": "Deploy Custom AI Agents with meradomain.in"
    },
    {
        "id": "bespoke_vs_templates",
        "title": "Why Fast-Growing Brands Ditch Template Sites",
        "category": "Educational Content",
        "industry": "Founders & Executive Leadership",
        "metrics": "Zero Plugin Bloat • Complete Brand Differentiation • 100% Core Web Vitals",
        "problem": "Off-the-shelf templates look identical to competitors, come with 40+ unneeded plugins, and create security/maintenance headaches.",
        "solution": "Tailored code architectures engineered from scratch around the brand's unique conversion funnels and visual design tokens.",
        "takeaway": "Your website is your premier 24/7 executive office. Never let a generic $50 template represent a multi-million-rupee vision.",
        "cta": "Build Your Flagship Web Presence with meradomain.in"
    },
    {
        "id": "mobile_app_flutter",
        "title": "Cross-Platform Flutter Flagship for High Retention",
        "category": "Mobile Engineering",
        "industry": "Fintech & On-Demand Services",
        "metrics": "Single Codebase iOS + Android • 60 FPS Native Motion • 4.9 App Store Rating",
        "problem": "Maintaining separate Swift and Kotlin codebases doubled development cost and caused feature-parity delays.",
        "solution": "Engineered a unified Flutter mobile application with offline-first caching, biometrics authentication, and smooth custom haptics.",
        "takeaway": "A single, well-architected cross-platform codebase delivers native performance while slashing delivery time in half.",
        "cta": "Engineer Native Mobile Apps at meradomain.in"
    }
]

def get_random_portfolio_win() -> Dict[str, Any]:
    return random.choice(PORTFOLIO_WINS)

def get_portfolio_win_by_id(win_id: str) -> Dict[str, Any]:
    for win in PORTFOLIO_WINS:
        if win["id"] == win_id:
            return win
    return PORTFOLIO_WINS[0]
