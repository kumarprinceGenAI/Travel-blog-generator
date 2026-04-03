from google import genai
import os
from dotenv import load_dotenv
import json
from utils import safe_generate

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def writer_agent(plan: dict):

    prompt = f"""
You are a travel blogger who writes REAL, EXPERIENCE-DRIVEN blogs.

You must NOT sound generic.

---

 BLOG CONTEXT

Intent: {plan.get("intent")}
Persona: {plan.get("persona")}
Audience: {plan.get("audience")}
Tone: {plan.get("tone")}

---

LOCAL CONTEXT (MANDATORY)

Currency: {plan.get("local_context", {}).get("currency")}
Budget Range: {plan.get("local_context", {}).get("budget_range")}
Transport: {plan.get("local_context", {}).get("transport_examples")}
Notes: {plan.get("local_context", {}).get("practical_notes")}
---
MANDATORY:
- Use INR (₹)
- Include at least 2 insider tips
- Include “mistakes to avoid” section
- Include local transport details
- Avoid generic tone
---

 STRUCTURE

{json.dumps(plan.get("sections"), indent=2)}

---

 WRITING RULES (STRICT)

- Write like you have personally visited the place
- Use ₹ (INR) only (NO USD)
- Mention REAL locations (not generic words)
- Include:
  - practical costs
  - routes
  - timings
  - mistakes to avoid
- Add small personal observations
- Avoid phrases like:
  - "famous for"
  - "known for"
  - "offers something for everyone"

- Add problem-solving:
  - what can go wrong
  - what to avoid
  - better alternatives
- ADD STRONG OPINIONS
   - Include at least 2 bold or non-obvious opinions
   - Challenge common travel advice

- ADD FAQ SECTION AT END
   Include 3–5 questions like:
   - Is Kerala good in monsoon?
   - Is houseboat worth it?
   - What is daily budget?

- ADD NATURAL INTERNAL LINKS
   - Mention related topics naturally inside content
---

 OUTPUT

- 1500–2000 words
- Proper headings (H1, H2)
- Natural paragraphs (NOT bullet dump)
- Engaging + practical

Write the FULL blog.

Return ONLY blog content.
"""

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return response.text