from google import genai
import os
from dotenv import load_dotenv
from utils import safe_generate
from researcher import extract_json

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


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

OUTPUT

{{
  "content_score": number,
  "seo_score": number,
  "readability_score": number,
  "uniqueness_score": number,
  "verdict": "...",
  "feedback": ["...", "..."]
}}

---

Blog:
{blog}

Return ONLY JSON.
"""

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return extract_json(response.text)