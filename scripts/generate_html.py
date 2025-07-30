#!/usr/bin/env python3
import os
import datetime
import openai
from pytrends.request import TrendReq

# Retrieve API key from environment
#
# Use os.getenv instead of indexing into os.environ directly. This avoids a
# KeyError at import time if OPENAI_API_KEY is not set. We validate the key in
# main() and provide a clear error message if it is missing.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def fetch_trending_search() -> str:
    """Fetch the top trending search term from Google Trends (United States).

    The pytrends library returns a pandas.DataFrame with the trending terms in
    column 0. The previous implementation returned the entire column as a
    Series, which is not what callers expect. Here we select the first row of
    the first column to get a single string. If pytrends fails for any reason,
    we fall back to a generic topic.
    """
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        df = pytrends.trending_searches(pn="united_states")
        # Use iat to access the first cell as a plain Python string.
        return df.iat[0, 0]
    except Exception:
        # Fall back to a generic topic if Google Trends fails
        return "World news"

def generate_article(prompt: str) -> str:
    """Generate a 4–5 paragraph news article about the given prompt using OpenAI.

    The API key is set just before making the request. If the API call fails,
    the exception will propagate so that the caller can handle it appropriately.
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
    """Return an HTML document for the article."""
    body_html = body.replace('\n', '<br>')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="description" content="{title}">
</head>
<body>
    <h1>{title}</h1>
    <p><em>{date}</em></p>
    {body_html}
</body>
</html>
"""

def main() -> None:
    """Entry point for the script.

    Orchestrate fetching a trending topic, generating an article (or
    placeholder text when OpenAI API access is unavailable), writing
    the resulting HTML file, and updating the index page. If the
    ``OPENAI_API_KEY`` environment variable is not set or the API call
    fails, the script still produces a basic article about the trending
    topic to prevent the GitHub Action from failing.
    """

    # Determine the current trending search term. If Google Trends
    # cannot be reached, ``fetch_trending_search`` will fall back to a
    # generic topic.
    trend = fetch_trending_search()

    # Generate the article text. When the OpenAI API key is provided,
    # attempt to call the API; otherwise produce a simple message. Any
    # exceptions from the API call are caught to avoid crashing the run.
    if OPENAI_API_KEY:
        try:
            article_text = generate_article(trend)
        except Exception as exc:
            # If OpenAI API fails for any reason, create a fallback
            # article explaining the error to the reader.
            article_text = (
                f"News update for {trend}\n\n"
                f"An error occurred while generating the article: {exc}.\n"
                "Please check your API configuration and try again."
            )
    else:
        # When no API key is configured, produce a placeholder article.
        article_text = (
            f"News update for {trend}\n\n"
            "Automatic article generation is disabled because the "
            "OPENAI_API_KEY environment variable is not set. "
            "Please add this secret in your repository settings to enable "
            "AI-generated news."
        )

    # Extract the headline (first non-empty line) for the title and slug.
    lines = [ln for ln in article_text.split("\n") if ln.strip()]
    title = lines[0] if lines else trend.title()

    # Normalise the slug: lowercase, replace spaces with hyphens and remove punctuation.
    raw_slug = title.lower()
    for ch in [" ", ",", ".", ":", "?", "!", ";", "\n"]:
        raw_slug = raw_slug.replace(ch, "-")
    slug = "".join(c for c in raw_slug if c.isalnum() or c == "-")
    slug = slug.strip("-")[:50]

    today = datetime.datetime.utcnow().date().isoformat()

    # Write the article HTML to docs/articles.
    articles_dir = os.path.join("docs", "articles")
    os.makedirs(articles_dir, exist_ok=True)
    article_filename = f"{today}-{slug}.html"
    html_content = create_html(title, article_text, today)
    article_path = os.path.join(articles_dir, article_filename)
    with open(article_path, "w", encoding="utf-8") as fh:
        fh.write(html_content)

    # Build or update the index.html page.
    index_path = os.path.join("docs", "index.html")
    link = f'<li><a href="articles/{article_filename}">{title} ({today})</a></li>\n'
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as fh:
            index_content = fh.read()
    else:
        index_content = (
            "<!DOCTYPE html>\n"
            "<html><head><meta charset=\"UTF-8\"><title>Latest News</title></head><body>\n"
            "<h1>Latest News</h1>\n"
            "<ul>\n</ul>\n"
            "</body></html>\n"
        )

    # Insert the link before the closing </ul> if it's not already present.
    if link not in index_content:
        if "</ul>" not in index_content:
            index_content = index_content.replace("</body>", "</ul></body>")
        index_content = index_content.replace("</ul>", f"{link}</ul>")

    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(index_content)

if __name__ == "__main__":
    main()
