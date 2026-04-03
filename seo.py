from google import genai
import os
from dotenv import load_dotenv
from utils import safe_generate

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def seo_agent(blog: str):
    prompt = f"""
You are an SEO expert for travel blogs.

Given this blog:

{blog}

Generate:

1. SEO Title (max 60 characters)
2. Meta Description (max 160 characters)
3. URL Slug
4. Primary Keyword
5. Secondary Keywords (5)
6. Suggested internal linking ideas (real, not placeholders)

Keep it practical and usable.
"""

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))
    return response.text