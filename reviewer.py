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

Your job is to evaluate if this blog can COMPETE with top Google results.

---

 EVALUATION CRITERIA

1. CONTENT QUALITY
- Depth, usefulness, practical value

2. SEO QUALITY
- Clear intent, keyword usage, structure

3. READABILITY
- Flow, clarity, engagement

4. UNIQUENESS (MOST IMPORTANT)
- Does it feel real or generic?
- Does it include experience, opinions, insights?

---

 STRICT SCORING RULE (VERY IMPORTANT)

You MUST follow this distribution:

- 9–10 → ONLY if exceptional, unique, expert-level (rare)
- 8–8.5 → good but still somewhat safe/generic
- 7–7.5 → average content
- <7 → poor or generic

 Most blogs should be between 7–8.5  
 Do NOT give 9+ easily  

---

 EXAMPLES OF SCORING (VERY IMPORTANT)

Example 1:
- Blog is detailed but slightly generic and safe
→ content_score: 7.5
→ uniqueness_score: 7
→ verdict: needs_improvement

Example 2:
- Blog has good tips but lacks strong opinions and edge
→ content_score: 8
→ uniqueness_score: 7.5
→ verdict: needs_improvement

Example 3:
- Blog is highly original, opinionated, and better than competitors
→ content_score: 9
→ uniqueness_score: 9
→ verdict: good

 IMPORTANT:
Most blogs should match Example 1 or 2, NOT Example 3.

---

 PENALTIES (APPLY STRICTLY)

If ANY of these exist:

- generic tone → uniqueness_score ≤ 7
- no strong opinions → reduce content_score by 1–2
- no controversial/non-obvious insights → uniqueness_score ≤ 7
- lacks mistakes/tips → content_score ≤ 7
- intro weak → reduce content_score by 1
- feels AI-generated → uniqueness_score ≤ 6
- no FAQ → seo_score ≤ 7
- No ₹ → seo_score max 6
- No tips → content_score max 7
- No mistakes → uniqueness_score max 7

---

 AVERAGE SCORE CALCULATION (MANDATORY)

Average = (content_score + seo_score + readability_score + uniqueness_score) / 4

You MUST calculate this before giving verdict.

---

 VERDICT RULE (ONLY RULE)

- If average < 8.5 → "needs_improvement"
- If average ≥ 8.5 → "good"

---

 OUTPUT FORMAT (STRICT JSON)

{{
  "content_score": number between 0 and 10,
  "seo_score": number between 0 and 10,
  "readability_score": number between 0 and 10,
  "uniqueness_score": number between 0 and 10,
  "verdict": "good" or "needs_improvement",
  "feedback": [
    "specific issue",
    "specific issue"
  ]
}}

---

Blog:
{blog}

Return ONLY valid JSON.
No markdown.
No explanation.
"""

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return extract_json(response.text)