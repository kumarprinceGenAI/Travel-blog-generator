from google import genai
import os
from dotenv import load_dotenv
from logger import logger
import time
from metrics import get_top_topics, get_low_performing_topics
from signals import get_pain_points_real, get_trend_signal_real, normalize_signals

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# 🔹 Retry wrapper
def safe_generate(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Retry {attempt+1}/{retries} failed: {str(e)}")
            time.sleep(delay)
    raise Exception("All retries failed")


# 🔹 Clean + extract JSON
def extract_json(text):
    import re
    import json

    if not text:
        print("[JSON ERROR] Empty response")
        return {}

    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except:
        pass

    array_match = re.search(r"\[.*\]", text, re.DOTALL)
    if array_match:
        try:
            return {"topics": json.loads(array_match.group(0))}
        except:
            pass

    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except:
            pass

    print("[JSON FIX FAILED] Raw output:", text[:200])  # 🔥 ADD THIS
    return {}  # 🔥 CRITICAL: no exception


# 🔹 Scoring function (unchanged)
def calculate_score(t):
    try:
        return (
            0.3 * t.get("demand_score", 5) +
            0.3 * t.get("intent_score", 5) +
            0.2 * t.get("uniqueness_score", 5) +
            0.2 * t.get("monetization_score", 5)
        )
    except Exception:
        return 5



def extract_patterns(topics):
    patterns = []

    for t in topics:
        t_lower = t.lower()

        if "solo" in t_lower:
            patterns.append("solo travel")
        if "budget" in t_lower:
            patterns.append("budget travel")
        if "itinerary" in t_lower:
            patterns.append("itinerary-based")
        if "guide" in t_lower:
            patterns.append("practical guide")
        if "digital nomad" in t_lower:
            patterns.append("digital nomad lifestyle")
        if "safety" in t_lower:
            patterns.append("safety-focused")

    return list(set(patterns))


# 🔹 Main agent
def researcher_agent():
    top_topics = get_top_topics(limit=3)
    low_topics = get_low_performing_topics(limit=3)

    # 🔹 Format safely
    top_topics_text = "\n".join([f"- {t}" for t in top_topics]) if top_topics else "None"
    low_topics_text = "\n".join([f"- {t}" for t in low_topics]) if low_topics else "None"

    trends = normalize_signals(get_trend_signal_real())
    pain_points = normalize_signals(get_pain_points_real())

    trend_text = "\n".join([f"- {t}" for t in trends]) if trends else "None"
    pain_text = "\n".join([f"- {p}" for p in pain_points]) if pain_points else "None"

    logger.info(f"[Researcher] Trends Used:\n{trend_text}")
    logger.info(f"[Researcher] Pain Points Used:\n{pain_text}")

    # 🔥 NEW — Pattern extraction
    patterns = extract_patterns(top_topics)
    patterns_text = ", ".join(patterns) if patterns else "None"

    prompt = f"""
    You are an expert travel content strategist.

    Generate 5 high-quality travel blog topics.

    --- CURRENT TREND SIGNALS ---
    These travel trends are currently popular:
    {trend_text}

    Use them as OPTIONAL signals, not strict rules.

    --- USER PAIN POINTS ---
    These are common travel problems:
    {pain_text}

    Prefer topics that directly solve these problems when relevant.

    --- HIGH-PERFORMING PATTERNS ---
    These topics performed well:
    {top_topics_text}

    Use them as inspiration for patterns (intent, structure), NOT for repetition.

    --- LOW-PERFORMING PATTERNS ---
    These topics performed poorly:
    {low_topics_text}

    Avoid similar patterns, angles, or generic structures.

    --- LEARNED PATTERNS ---
    These patterns worked well:
    {patterns_text}

    Prefer these patterns, but apply them to NEW destinations and contexts.

    --- TREND BIAS ---
    Prefer topics aligned with:
    - seasonal travel (summer, monsoon, winter)
    - visa-friendly destinations for Indians
    - budget optimization due to rising travel costs
    - remote work / digital nomad trends

    Do NOT force trends if not relevant.

    --- DIVERSITY CONSTRAINT (VERY IMPORTANT) ---
    - Do NOT generate all topics around the same theme (e.g., visa, budget, or digital nomad)
    - Ensure diversity across:
    • destinations
    • travel styles (budget, luxury, culture, adventure)
    • user intent (itinerary, guide, comparison, experience)
    - At least 2 topics MUST NOT be related to current trends

    --- SIGNAL USAGE RULE ---
    - Trends and pain points are guidance signals, NOT strict instructions
    - Do NOT over-prioritize trending themes
    - If trends conflict with uniqueness or usefulness, prefer uniqueness

    --- ANTI-REPETITION RULE ---
    - Avoid repeating themes like:
    • visa guides
    • budget travel
    • digital nomad lifestyle
    - If one topic uses a trend, others must explore different angles

    --- QUALITY FILTER ---
    Reject topics that:
    - are generic even if trending
    - repeat common blog formats
    - do not solve a clear user problem

    --- INSTRUCTIONS ---
    - Generate NEW topics (do NOT repeat existing ones)
    - Maintain diversity across topics
    - Prefer problem-solving, high-intent topics
    - Avoid generic topics like "top 10 places"

    Return ONLY valid JSON:

    {{
    "topics": [
        {{
        "title": "...",
        "reason": "...",
        "target_audience": "...",

        "demand_score": number between 0-10,
        "intent_score": number between 0-10,
        "uniqueness_score": number between 0-10,
        "monetization_score": number between 0-10
        }}
    ]
    }}

    Scoring Rules:

    - demand_score:
    High if topic matches real search intent (itinerary, cost, guide, safety)

    - intent_score:
    High if topic solves a clear user problem (NOT informational fluff)

    - uniqueness_score:
    High if it is specific, niche, or under-covered

    - monetization_score:
    High if it naturally includes hotels, transport, tools, or bookings

    IMPORTANT:
    Topics with vague or generic framing should score LOW.

    Focus on India and Southeast Asia.

    Return ONLY valid JSON. No markdown. No explanation.
    """

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    data = extract_json(response.text)

    # 🔥 NEW — Ranking topics by score
    topics = data.get("topics", [])
    topics = sorted(topics, key=lambda t: calculate_score(t), reverse=True)

    data["topics"] = topics

    return data