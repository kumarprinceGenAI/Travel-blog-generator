from google import genai
import os
from dotenv import load_dotenv
import json
from utils import safe_generate

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def writer_agent(plan: dict):

    keywords = plan.get("keywords", {})
    primary = keywords.get("primary_keyword", "")
    secondary = keywords.get("secondary_keywords", [])
    long_tail = keywords.get("long_tail_keywords", [])

    prompt = f"""
You are a travel blogger who writes REAL, EXPERIENCE-DRIVEN blogs.

---

BLOG CONTEXT

Intent: {plan.get("intent")}
Persona: {plan.get("persona")}
Audience: {plan.get("audience")}
Tone: {plan.get("tone")}

---

SEO REQUIREMENTS (STRICT)

Primary Keyword: {primary}
Secondary Keywords: {secondary}
Long Tail Keywords: {long_tail}

RULES:
- Primary keyword:
  ✔ H1
  ✔ first 100 words
  ✔ at least 2 H2s

- Secondary:
  ✔ natural usage

- Long-tail:
  ✔ FAQ section

DO NOT keyword stuff.

---

LOCAL CONTEXT (MANDATORY)

Currency: {plan.get("local_context", {}).get("currency")}
Budget Range: {plan.get("local_context", {}).get("budget_range")}
Transport: {plan.get("local_context", {}).get("transport_examples")}
Notes: {plan.get("local_context", {}).get("practical_notes")}

MANDATORY:
- Use ₹
- Include insider tips
- Include mistakes to avoid
- Include transport details

---

STRUCTURE

{json.dumps(plan.get("sections"), indent=2)}

---

WRITING RULES (STRICT)

- Write like personal experience
- Include:
  ✔ costs
  ✔ routes
  ✔ timing
  ✔ mistakes

- ADD STRONG OPINIONS
- ADD NON-OBVIOUS INSIGHTS

- Avoid:
  "famous for"
  "known for"

---

STRUCTURE RULES

- H1 → keyword
- H2 → problems
- H3 → breakdown
- Add FAQ section (3–5)
- Add quick answer snippet

---

OUTPUT

- 1500–2000 words
- Proper headings
- Natural flow

Return ONLY blog.
"""

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return response.text