#!/usr/bin/env python3
"""
Script to fetch a trending topic from Google Trends and generate a news
article using OpenAI. The result is saved as an HTML file in the
`docs/articles` directory and the main `docs/index.html` is updated to
link to the new article. If the OpenAI API key is missing or the API
call fails, a fallback article is generated so that the GitHub Action
still succeeds.
"""

import os
import datetime
from typing import List

import openai
from pytrends.request import TrendReq

# Retrieve API key from environment. We defer validation until runtime to
# avoid raising exceptions on import if the key is missing.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def fetch_trending_search() -> str:
    """Return the top trending search term for the United States.

    If the Google Trends request fails for any reason, return a generic
    fallback topic instead of propagating the exception. This ensures
    downstream logic always has a string to work with.
    """
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        df = pytrends.trending_searches(pn="united_states")
        return df.iat[0, 0]
    except Exception:
        return "World news"


def generate_article(prompt: str) -> str:
    """Generate a 4–5 paragraph news article about ``prompt`` using OpenAI.

    The API key is set just before making the request. If any error
    occurs during the API call, let the caller handle the exception.
    """
    openai.api_key = OPENAI_API_KEY
    messages = [
        {
            "role": "system",
            "content": "You are a journalist who writes concise news articles.",
        },
        {
            "role": "user",
            "content": (
                f"Write a 4-5-paragraph news article about '{prompt}'. "
                "Include a headline and subheadings. Keep it factual and neutral."
            ),
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def create_html(title: str, body: str, date: str) -> str:
    """Return an HTML document for the article.

    This function replaces newline characters in the body with ``<br>``
    tags so that paragraphs are separated when rendered in the browser.
    """
    body_html = body.replace("\n", "<br>")
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        f"  <title>{title}</title>\n"
        f"  <meta name=\"description\" content=\"{title}\">\n"
        "</head>\n"
        "<body>\n"
        f"  <h1>{title}</h1>\n"
        f"  <p><em>{date}</em></p>\n"
        f"  {body_html}\n"
        "</body>\n"
        "</html>\n"
    )


def update_index(index_path: str, title: str, slug_filename: str, date: str) -> None:
    """Create or update the ``index.html`` file with a link to the new article.

    The link is inserted before the closing ``</ul>`` tag. If the ``index.html``
    does not exist, a minimal page with a list is created.
    """
    link = f'<li><a href="articles/{slug_filename}">{title} ({date})</a></li>\n'
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as fh:
            index_content = fh.read()
    else:
        index_content = (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head><meta charset=\"UTF-8\"><title>Latest News</title></head>\n"
            "<body>\n"
            "<h1>Latest News</h1>\n"
            "<ul>\n</ul>\n"
            "</body>\n"
            "</html>\n"
        )
    if link not in index_content:
        if "</ul>" in index_content:
            index_content = index_content.replace("</ul>", f"{link}</ul>")
        else:
            # If somehow </ul> is missing, append the link near the end of body
            index_content = index_content.replace("</body>", f"<ul>\n{link}</ul></body>")
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(index_content)


def main() -> None:
    """Main entry point for generating and saving the daily news article."""
    trend = fetch_trending_search()

    # Generate article text using OpenAI if a key is configured.
    if OPENAI_API_KEY:
        try:
            article_text = generate_article(trend)
        except Exception as exc:
            article_text = (
                f"News update for {trend}\n\n"
                f"An error occurred while generating the article: {exc}.\n"
                "Please check your API configuration and try again."
            )
    else:
        article_text = (
            f"News update for {trend}\n\n"
            "Automatic article generation is disabled because the "
            "OPENAI_API_KEY environment variable is not set. "
            "Please add this secret in your repository settings to enable "
            "AI-generated news."
        )

    # Determine article title and slug.
    lines: List[str] = [ln for ln in article_text.split("\n") if ln.strip()]
    title: str = lines[0] if lines else trend.title()
    raw_slug = title.lower()
    for ch in [" ", ",", ".", ":", "?", "!", ";", "\n"]:
        raw_slug = raw_slug.replace(ch, "-")
    slug = "".join(c for c in raw_slug if c.isalnum() or c == "-").strip("-")[:50]

    today = datetime.datetime.utcnow().date().isoformat()
    articles_dir = os.path.join("docs", "articles")
    os.makedirs(articles_dir, exist_ok=True)
    article_filename = f"{today}-{slug}.html"

    html_content = create_html(title, article_text, today)
    article_path = os.path.join(articles_dir, article_filename)
    with open(article_path, "w", encoding="utf-8") as fh:
        fh.write(html_content)

    # Update index.html
    index_path = os.path.join("docs", "index.html")
    update_index(index_path, title, article_filename, today)


if __name__ == "__main__":
    main()
