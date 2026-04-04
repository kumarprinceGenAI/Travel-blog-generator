from google import genai
import os
from dotenv import load_dotenv
from utils import safe_generate
from researcher import extract_json
from metrics import get_top_topics

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def planner_agent(topic: str):
    top_topics = get_top_topics(limit=3)
    top_topics_text = "\n".join([f"- {t}" for t in top_topics]) if top_topics else "None"

    prompt = f"""
You are a professional travel content strategist and SEO expert.

Your job is to create a HIGH-RANKING blog plan (not generic).

TOPIC:
{topic}

--- SUCCESSFUL PATTERNS ---
{top_topics_text}

Use them to understand:
- structure
- specificity
- practical depth

DO NOT repeat them.

---

CRITICAL REQUIREMENTS (NON-NEGOTIABLE):

1. DEFINE SEARCH INTENT
- informational / itinerary / budget / comparison

2. DEFINE TARGET PERSONA
- budget / solo / couple / digital nomad

3. LOCALIZATION
- INR (₹)
- India audience

4. PRACTICAL CONTENT
- routes, costs, timings

5. EXPERIENCE EDGE
- mistakes
- insider tips
- non-obvious advice

6. AVOID GENERIC CONTENT

7. REAL PROBLEMS
- crowds, scams, transport issues

---

STRUCTURE QUALITY RULES:

- Avoid:
  "Top Places", "Things to Do"

- Prefer:
  "2-Day Optimized Itinerary"
  "Transport Hacks Locals Use"

Each section must:
✔ solve a problem
✔ be actionable

---

KEYWORD RULES (VERY IMPORTANT):

- ONE primary keyword (exact search query)
- 3–5 secondary keywords
- 3–5 long-tail keywords

ALSO:
- Combine all keywords into "seo_keywords"
- Include primary + secondary + long-tail
---

OUTPUT FORMAT (STRICT JSON):

{{
"intent": "...",
"persona": "...",
"audience": "...",
"blog_type": "...",
"tone": "...",

"keywords": {{
  "primary_keyword": "...",
  "secondary_keywords": ["...", "..."],
  "long_tail_keywords": ["...", "..."]
}},

"seo_keywords": ["...", "..."],

"sections": [
  {{
  "title": "...",
  "goal": "...",
  "points": ["...", "..."]
  }}
],

"local_context": {{
  "currency": "INR (₹)",
  "budget_range": "...",
  "transport_examples": "...",
  "practical_notes": "..."
}}
}}

STRICT RULES:
Return STRICT JSON ONLY.
DO NOT include explanations.
- NO markdown
- ONLY JSON
"""

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return extract_json(response.text)