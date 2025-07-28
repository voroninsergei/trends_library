# flake8: noqa

"""
creator.py: Module to generate images for trending topics using DALL\u00b7E 3.
"""

import os
from typing import Dict, Any

import openai



# Initialize the OpenAI API key from environment variables. Requires OPENAI_API_KEY to be set.
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_image(prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
    """
    Generate an image for a given prompt using the DALL\u00b7E 3 model.

    Args:
        prompt: Text description for the desired image.
        size: Desired resolution of the generated image (default "1024x1024").

    Returns:
        A dictionary containing the URL of the generated image and an alt-text.
    """
    response = openai.Image.create(  # noqa: E501
        prompt=prompt,
        n=1,
        size=size,
        model="dall-e-3",
    )
    image_url = response["data"][0]["url"]
    # Use the prompt itself truncated to 125 characters as alt-text per specification.
    alt_text = (prompt[:125] + "...") if len(prompt) > 125 else prompt
    return {
        "prompt": prompt,
        "image_url": image_url,
        "alt_text": alt_text,
    }
