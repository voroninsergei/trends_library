#!/usr/bin/env python3
import os
import datetime
import openai
from pytrends.request import TrendReq

# Retrieve API key from environment
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def fetch_trending_search() -> str:
    """Fetch the top trending search term from Google Trends (United States)."""
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        df = pytrends.trending_searches(pn="united_states")
        return df[0]
    except Exception:
        # Google Trends sometimes returns 404; fall back to a generic term
        return "World news"

def generate_article(prompt: str) -> str:
    """Generate a 4–5 paragraph news article about the given prompt using OpenAI."""
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "system", "content": "You are a journalist who writes concise news articles."},
        {"role": "user", "content": f"Write a 4-5-paragraph news article about '{prompt}'. Include a headline and subheadings. Keep it factual and neutral."},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
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

def main():
    trend = fetch_trending_search()
    article = generate_article(trend)
    title = article.split("\n")[0]
    slug = title.lower().replace(" ", "-").replace(",", "")[:50]
    today = datetime.datetime.utcnow().date().isoformat()

    articles_dir = os.path.join("docs", "articles")
    os.makedirs(articles_dir, exist_ok=True)
    article_filename = f"{today}-{slug}.html"
    html_content = create_html(title, article, today)
    with open(os.path.join(articles_dir, article_filename), "w", encoding="utf-8") as f:
        f.write(html_content)

    index_path = os.path.join("docs", "index.html")
    link = f'<li><a href="articles/{article_filename}">{title} ({today})</a></li>\n'
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = [
            "<!DOCTYPE html>\n<html><head><meta charset=\"UTF-8\"><title>Latest News</title></head><body>\n",
            "<h1>Latest News</h1>\n<ul>\n",
        ]
    insert_pos = lines.index("<ul>\n") + 1 if "<ul>\n" in lines else len(lines)
    lines.insert(insert_pos, link)
    if not any("</ul>" in line for line in lines):
        lines.append("</ul></body></html>\n")
    with open(index_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
 
