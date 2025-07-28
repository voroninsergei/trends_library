# flake8: noqa

"""
generator.py: Module to generate articles from trending topics using OpenAI GPT-4o.

This module provides a function to create long-form articles with structured sections and SEO metadata.
"""

import os
from typing import Dict, Any

import openai

# Initialize OpenAI API key from environment variables. You should set OPENAI_API_KEY in your runtime environment.
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_article(topic: str, language: str = "en") -> Dict[str, Any]:
    """
    Generate an article about the provided topic in the specified language.

    The article will include the following sections: Introduction, History, Situation,
    Impact, and FAQ. It will also return SEO metadata such as title, description and keywords.

    Args:
        topic: The trending topic to generate content about.
        language: ISO language code for the article language (default "en").

    Returns:
        A dictionary containing the generated article text and related metadata.
    """
    prompt = (
        f"Write a detailed long-form article (2000-4000 words) about '{topic}'. "
        f"The article should be written in {language} and include the following sections: "
        "Introduction, History, Situation, Impact, FAQ. "
        "Provide SEO metadata including a title, a short description, and relevant keywords."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes comprehensive articles based on given topics."},  # noqa: E501
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    content = response["choices"][0]["message"]["content"]
    return {
        "topic": topic,
        "language": language,
        "content": content,
    }
