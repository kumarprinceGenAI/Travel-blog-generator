from google import genai
import os
from dotenv import load_dotenv
from utils import safe_generate

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_json(text):
    import re
    import json

    if not text:
        print("[JSON ERROR] Empty response")
        return None

    # 🔥 remove markdown wrappers
    text = re.sub(r"```json|```", "", text).strip()

    # 🔥 extract JSON block safely
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        print("[JSON ERROR] No JSON object found")
        return None

    text = match.group(0)

    # 🔥 FIX COMMON LLM BREAKS
    try:
        return json.loads(text)
    except:
        pass

    # 🔧 FIX 1: single quotes → double quotes
    fixed = text.replace("'", '"')

    # 🔧 FIX 2: remove trailing commas
    fixed = re.sub(r",\s*}", "}", fixed)
    fixed = re.sub(r",\s*]", "]", fixed)

    # 🔧 FIX 3: fix broken strings like: it'
    fixed = re.sub(r'(?<!\\)"([^"]*?)\n', r'"\1"', fixed)

    try:
        return json.loads(fixed)
    except:
        print("[JSON FIX FAILED] Raw output:", text[:200])
        return None


def reviewer_agent(blog: str):
    prompt = f"""
You are a VERY STRICT travel blog reviewer.

---

EVALUATION CRITERIA

1. CONTENT QUALITY
2. SEO QUALITY
3. READABILITY
4. UNIQUENESS (MOST IMPORTANT)

---

SEO STRICT CHECKS

- Keyword in H1
- Keyword in intro
- 2+ keyword H2s
- FAQ section
- snippet-friendly section

If missing → seo_score ≤ 7

---

PENALTIES

- generic tone → uniqueness ≤ 7
- no opinions → reduce content_score
- no insights → uniqueness ≤ 7
- no FAQ → seo_score ≤ 7
- no ₹ → seo_score ≤ 6

---

SCORING RULE

- 9–10 → rare
- 8–8.5 → good
- 7–7.5 → average

---

VERDICT RULE

- avg < 8.5 → needs_improvement
- avg ≥ 8.5 → good

---

STRICT ENFORCEMENT:

If the blog feels even slightly generic:
→ uniqueness_score MUST be ≤ 7

If content lacks strong opinions or edge:
→ content_score MUST be ≤ 8

If you give score ≥ 9:
→ you MUST justify with a VERY RARE reason

If unsure:
→ default to 7–8 range

---

If you give:
- uniqueness_score ≥ 9
- content_score ≥ 9

You MUST ensure:
- strong opinions present
- non-obvious insights present
- personal tone present

Else → reduce score

---

OUTPUT (STRICT JSON ONLY)

Rules:
- Use DOUBLE quotes only
- No trailing commas
- No text outside JSON
- Ensure valid JSON format

{{
  "content_score": number,
  "seo_score": number,
  "readability_score": number,
  "uniqueness_score": number,
  "verdict": "good|needs_improvement",
  "feedback": ["...", "..."]
}}

---

Blog:
{blog}

Return ONLY JSON.
"""

    def generate():
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        parsed = extract_json(response.text)

        # 🔴 STRICT STRUCTURE VALIDATION
        required_keys = [
            "content_score",
            "seo_score",
            "readability_score",
            "uniqueness_score",
            "verdict",
            "feedback"
        ]

        if not parsed or not all(k in parsed for k in required_keys):
            raise ValueError("Invalid reviewer JSON structure")

        return parsed

    return safe_generate(generate)