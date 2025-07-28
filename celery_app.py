"""
Celery application and task definitions for the Trends Library project.

This module configures a Celery app and exposes tasks for:
- Collecting trending searches from Google Trends via PyTrends.
- Generating an article using GPT-4o and an accompanying image via DALL·E 3.
- Publishing the generated content to the CMS.

Set the `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` environment variables to
point to your message broker and result backend. Defaults to a local Redis
instance if not provided.
"""

from __future__ import annotations

import os
from typing import Optional, Dict

from celery import Celery

# Import modules for tasks. These imports are inside the Celery workers, so
# they should be efficient and free of side effects.
from trends_crawler.crawler import fetch_trending_searches
from article_generator.generator import generate_article
from image_creator.creator import generate_image
from publisher.publisher import publish_article


# Configure Celery
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Instantiate Celery application
celery_app = Celery(
    "tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)


@celery_app.task(name="tasks.collect_trends_task")
def collect_trends_task(country: str, category: str, period: Optional[str] = None) -> list[dict]:
    """Collect trending searches for the given country and category.

    Args:
        country: ISO alpha-2 country code (e.g., 'US', 'FR').
        category: Google Trends category identifier.
        period: Optional period string to pass through to the crawler.

    Returns:
        A list of trend dictionaries returned by the crawler.
    """

    return fetch_trending_searches(country=country, category=category, period=period)


@celery_app.task(name="tasks.generate_content_task")
def generate_content_task(params: Dict[str, str]) -> dict:
    """Generate an article and image for a trending topic and publish it.

    Args:
        params: A dictionary containing at least the keys 'country', 'category',
            and 'title'. The optional key 'period' may be provided for trend
            sampling purposes.

    Returns:
        The response from the publisher after posting the article.
    """

    country = params.get("country")
    category = params.get("category")
    title = params.get("title")
    period = params.get("period")

    # Generate article using the article generator. The function returns a dict
    # with article content and metadata.
    article_data = generate_article(
        trend_title=title,
        country=country,
        category=category,
    )

    # Generate accompanying image. Returns URL and alt text.
    image_url, alt_text = generate_image(prompt=title, size="1024x1024")

    # Compose payload for publisher. Merge article data with image and metadata.
    payload = {
        **article_data,
        "image_url": image_url,
        "alt_text": alt_text,
        "country": country,
        "category": category,
    }

    # Publish the article via the CMS. publish_article returns the CMS response.
    response = publish_article(payload)
    return response
