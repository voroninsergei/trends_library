# flake8: noqa

"""
crawler.py

This module provides functions to fetch trending search topics from Google Trends.
"""

from typing import List, Dict, Optional
import datetime
from pytrends.request import TrendReq


def fetch_trending_searches(country_code: str = "US", category: Optional[str] = None) -> List[Dict]:
    """
    Fetch current trending searches for a given ISO alpha-2 country code.

    Args:
        country_code: Two-letter country code for which to fetch trends.
        category: Optional Google Trends category to filter by.

    Returns:
        A list of dictionaries containing trend information.
    """
    # Initialize PyTrends
    pytrends = TrendReq(hl=country_code, tz=360)
    # trending_searches returns a DataFrame with trending search terms.
    trending_df = pytrends.trending_searches(pn=country_code)
    now = datetime.datetime.utcnow().isoformat()
    trends: List[Dict] = []
    for title in trending_df[0].tolist():
        trends.append({
            "country": country_code,
            "category": category,
            "title": title,
            "traffic_value": None,
            "ts_collected": now,
        })
    return trends
