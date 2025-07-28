"""
publisher.py: Module for publishing articles to the CMS.

This module defines functions to send generated articles to a RESTful CMS endpoint.
"""

import os
from typing import Dict, Any

import requests

# Base URL and token for the CMS (e.g., Strapi). These should be configured in environment variables.
CMS_BASE_URL = os.getenv("CMS_BASE_URL", "http://localhost:1337")
CMS_TOKEN = os.getenv("CMS_TOKEN")


def publish_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publish an article to the CMS via the /articles REST endpoint.

    Args:
        article_data: A dictionary containing article content and metadata formatted for the CMS.

    Returns:
        The JSON response from the CMS if the request is successful.

    Raises:
        requests.HTTPError: If the CMS responds with an error status code.
    """
    url = f"{CMS_BASE_URL}/articles"
    headers = {
        "Authorization": f"Bearer {CMS_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=article_data, headers=headers)
    # Raise an HTTPError if the response contains an unsuccessful status code
    response.raise_for_status()
    return response.json()
