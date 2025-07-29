#!/usr/bin/env python3
import os
import datetime
import openai
from pytrends.request import TrendReq

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def fetch_trending_search():
    pytrends = TrendReq(hl="en-US", tz=360)
    df = pytrends.trending_searches(pn="united_states")
    return df[0]  # берём самый популярный запрос

def generate_article(prompt):
    openai.api_key = OPENAI_API_KEY
    messages = [
        {"role": "system", "content": "You are a journalist who writes concise news articles."},
        {"role": "user", "content": f"Write a 4‑5‑paragraph news article about '{prompt}'. "
                                    "Include a headline and subheadings. Keep it factual and neutral."},
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content.strip()

def create_html(title, body, slug, date):
    # Простая HTML‑разметка
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="description" content="{title}">
</head>
<body>
    <h1>{title}</h1>
    <p><em>{date}</em></p>
    {body.replace('\n', '<br>')}
</body>
</html>"""
    return html

def main():
    trend = fetch_trending_search()
    article = generate_article(trend)
    title = article.split("\n")[0]
    slug = title.lower().replace(" ", "-").replace(",", "")[:50]
    today = datetime.datetime.utcnow().date().isoformat()
    content_html = create_html(title, article, slug, today)

    # пути для GitHub Pages
    articles_dir = os.path.join("docs", "articles")
    os.makedirs(articles_dir, exist_ok=True)
    article_filename = f"{today}-{slug}.html"
    with open(os.path.join(articles_dir, article_filename), "w", encoding="utf-8") as f:
        f.write(content_html)

    # обновление index.html
    index_path = os.path.join("docs", "index.html")
    link = f'<li><a href="articles/{article_filename}">{title} ({today})</a></li>\n'
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = f.readlines()
    else:
        index = ["<!DOCTYPE html>\n<html><head><meta charset=\"UTF-8\"><title>Latest News</title></head><body>\n",
                 "<h1>Latest News</h1>\n<ul>\n"]

    # вставляем ссылку в начало списка
    insert_pos = index.index("<ul>\n") + 1 if "<ul>\n" in index else len(index)
    index.insert(insert_pos, link)
    if index[-1].strip() != "</ul></body></html>":
        index.append("</ul></body></html>\n")
    with open(index_path, "w", encoding="utf-8") as f:
        f.writelines(index)

if __name__ == "__main__":
    main()
