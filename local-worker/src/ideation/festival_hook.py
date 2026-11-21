"""
MeraDomain Social Agent - Business Calendar & Festival Hooks
"""

from datetime import datetime
from typing import Optional, Dict, Any

BUSINESS_CALENDAR = [
    {
        "name": "Q1 Strategic Kickoff",
        "month": 1,
        "day_range": (1, 15),
        "angle": "Setting digital benchmarks: Why ambitious brands overhaul their tech stack at the start of the year.",
        "hook": "New Year, Same Outdated Tech Stack? Here is how leading brands stay ahead in 2026."
    },
    {
        "name": "Indian Financial Year End (FY Close)",
        "month": 3,
        "day_range": (15, 31),
        "angle": "Maximizing digital ROI and tax-advantaged IT infrastructure investments before March 31.",
        "hook": "Smart Indian enterprises deploy capital into revenue-generating web assets before FY close."
    },
    {
        "name": "World Creativity & Innovation Day",
        "month": 4,
        "day_range": (18, 24),
        "angle": "Engineering meets aesthetics: The art of high-converting bespoke UI/UX design.",
        "hook": "Good design is pretty. Great digital architecture prints revenue."
    },
    {
        "name": "Mid-Year Digital Audit",
        "month": 6,
        "day_range": (15, 30),
        "angle": "Is your website delivering on its Q1 promise? Core Web Vitals and conversion audit season.",
        "hook": "Mid-year check: If your mobile site takes > 3 seconds to load, you're leaving money on the table."
    },
    {
        "name": "Festive Season Readiness (Diwali & D2C)",
        "month": 9,
        "day_range": (1, 30),
        "angle": "Preparing headless e-commerce stores for peak festive traffic surges without checkout crashes.",
        "hook": "Peak festive traffic is coming. Can your e-commerce store handle 10,000 concurrent checkouts?"
    },
    {
        "name": "Diwali & New Year Business Launch",
        "month": 10,
        "day_range": (15, 31),
        "angle": "Auspicious new business launches: Starting the new financial year with custom digital flagships.",
        "hook": "Shubh Aarambh: Build, Launch, and Grow your brand's digital presence this festive season."
    },
    {
        "name": "Black Friday & Cyber Week",
        "month": 11,
        "day_range": (20, 30),
        "angle": "Zero-downtime conversion architecture for international and cross-border commerce.",
        "hook": "Conversion architecture: How sub-second checkout speeds lift Black Friday sales by 30%."
    }
]

def get_current_festival_hook() -> Optional[Dict[str, Any]]:
    today = datetime.now()
    month = today.month
    day = today.day

    for event in BUSINESS_CALENDAR:
        if event["month"] == month:
            start_day, end_day = event["day_range"]
            if start_day <= day <= end_day:
                return event

    return None
