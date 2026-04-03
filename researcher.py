from google import genai
import os
from dotenv import load_dotenv
from logger import logger
import time

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# 🔹 Retry wrapper
def safe_generate(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Retry {attempt+1}/{retries} failed:", str(e))
            time.sleep(delay)
    raise Exception("All retries failed")


# 🔹 Clean + extract JSON
def extract_json(text):
    import re
    import json

    if not text:
        raise Exception("Empty response from Gemini")

    # remove markdown
    text = re.sub(r"```json|```", "", text).strip()

    # try direct parse first
    try:
        return json.loads(text)
    except:
        pass

    # try extracting array first
    array_match = re.search(r"\[.*\]", text, re.DOTALL)
    if array_match:
        try:
            return {"topics": json.loads(array_match.group(0))}
        except:
            pass

    # fallback: extract object
    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except:
            pass

    logger.info("JSON PARSE FAILED")

    raise Exception("Unable to parse JSON")

def calculate_score(t):
    try:
        return (
            0.3 * t.get("demand_score", 5) +
            0.3 * t.get("intent_score", 5) +
            0.2 * t.get("uniqueness_score", 5) +
            0.2 * t.get("monetization_score", 5)
        )
    except Exception:
        return 5  # fallback safe score

# 🔹 Main agent
def researcher_agent():
    prompt = """
    You are an expert travel content strategist.

    Generate 5 high-quality travel blog topics.

    Return ONLY valid JSON:

    {
    "topics": [
        {
        "title": "...",
        "reason": "...",
        "target_audience": "...",

        "demand_score": number between 0-10,
        "intent_score": number between 0-10,
        "uniqueness_score": number between 0-10,
        "monetization_score": number between 0-10
        }
    ]
    }

    Scoring Rules:

    - demand_score:
    High if people are actively searching this topic

    - intent_score:
    High if topic solves a clear problem (itinerary, budget, guide)

    - uniqueness_score:
    High if NOT generic (avoid "top 10 places")

    - monetization_score:
    High if it can include hotels, transport, affiliate opportunities

    Rules:
    - Avoid generic topics
    - Prefer niche, practical, high-intent topics
    - Focus on India and Southeast Asia

    Return ONLY valid JSON. No markdown. No explanation.
    """

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return extract_json(response.text)