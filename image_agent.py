from google import genai
import os
from dotenv import load_dotenv
import requests
import logging
import re

from utils import safe_generate

load_dotenv()

# 🔧 Logger
logger = logging.getLogger(__name__)

# 🔑 Clients
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


# --------------------------------------------------
# 🧠 STEP 1 — Extract Sections from Blog
# --------------------------------------------------
def extract_sections(blog: str):
    sections = re.split(r"(## .+)", blog)

    structured = []
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""

        structured.append({
            "title": title,
            "content": content
        })

    return structured


# --------------------------------------------------
# 🧠 STEP 2 — Generate Prompt per Section
# --------------------------------------------------
def generate_prompts_batch(sections):
    limited_sections = sections[:5]  # 🔥 LIMIT

    combined = "\n\n".join([
        f"{i+1}. {sec['title']}: {sec['content'][:150]}"
        for i, sec in enumerate(limited_sections)
    ])

    prompt = f"""
Generate image search queries for these travel blog sections.

{combined}

Rules:
- 1 query per section
- 3–6 words each
- visually descriptive
- no generic terms

Return ONLY JSON list:
["query1", "query2", ...]
"""

    try:
        response = safe_generate(lambda: client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        ))

        import json
        import re

        text = response.text.strip()
        text = re.sub(r"```json|```", "", text)

        queries = json.loads(text)

        if not isinstance(queries, list):
            raise Exception("Invalid format")

        return queries

    except Exception as e:
        logger.error(f"[Images] Batch prompt failed: {str(e)}")
        return ["travel landscape"] * len(limited_sections)


# --------------------------------------------------
# 🖼️ STEP 3 — Fetch Single Image from Pexels
# --------------------------------------------------
def fetch_single_image(query):
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    try:
        url = "https://api.pexels.com/v1/search"
        params = {
            "query": query,
            "per_page": 1
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            logger.warning(f"[Images] API failed for query: {query}")
            return None

        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            logger.warning(f"[Images] No image found for query: {query}")
            return None

        return photos[0]["src"]["large"]

    except Exception as e:
        logger.error(f"[Images] Fetch error: {str(e)}")
        return None


# --------------------------------------------------
# 🚀 STEP 4 — MAIN PIPELINE
# --------------------------------------------------
def generate_images_for_blog(blog: str):
    logger.info("[Images] 🚀 Starting smart image generation")

    try:
        sections = extract_sections(blog)

        if not sections:
            logger.warning("[Images] No sections found")
            return []

        # 🔥 Limit to top 5 sections
        sections = sections[:5]

        prompts = generate_prompts_batch(sections)
        logger.info(f"[Images] Prompts: {prompts}")

        image_data = []

        # -----------------------------
        # 🔹 PRIMARY IMAGE FETCH
        # -----------------------------
        for sec, prompt in zip(sections, prompts):
            url = fetch_single_image(prompt)

            clean_title = sec["title"].replace("#", "").strip()

            if not url:
                logger.warning(f"[Images] ❌ No image for → {prompt}")
            else:
                logger.info(f"[Images] ✅ Found image for → {prompt}")

            image_data.append({
                "title": clean_title,
                "url": url  # can be None (handled later)
            })

        # -----------------------------
        # 🔥 FALLBACK SYSTEM (CRITICAL)
        # -----------------------------
        fallback_queries = [
            "travel landscape scenic",
            "mountain travel adventure",
            "backpacker journey road",
            "nature scenic view travel",
            "travel lifestyle exploration"
        ]

        fallback_index = 0

        for img in image_data:
            if img["url"] is None:
                while fallback_index < len(fallback_queries):
                    fallback_query = fallback_queries[fallback_index]
                    fallback_index += 1

                    fallback_url = fetch_single_image(fallback_query)

                    if fallback_url:
                        img["url"] = fallback_url
                        img["title"] = img["title"] + " (fallback)"
                        logger.info(f"[Images] 🔁 Fallback added → {fallback_query}")
                        break

                if img["url"] is None:
                    logger.error(f"[Images] 🚨 Still no image after fallback for → {img['title']}")

        # -----------------------------
        # 🔥 HARD GUARANTEE (MIN 5 IMAGES)
        # -----------------------------
        while len(image_data) < 5:
            for fallback_query in fallback_queries:
                fallback_url = fetch_single_image(fallback_query)

                if fallback_url:
                    image_data.append({
                        "title": "General Travel (extra fallback)",
                        "url": fallback_url
                    })
                    logger.info(f"[Images] ➕ Extra fallback added → {fallback_query}")
                    break

            if len(image_data) >= 5:
                break

        logger.info(f"[Images] ✅ Total images: {len(image_data)}")

        return image_data

    except Exception as e:
        logger.error(f"[Images] ❌ Pipeline failed: {str(e)}")
        return []  # 🔒 Never break pipeline