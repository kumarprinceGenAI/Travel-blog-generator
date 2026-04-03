from google import genai
import os
from dotenv import load_dotenv
from utils import safe_generate

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def improver_agent(blog: str, review: dict, errors: str = None):
    feedback = review.get("feedback", [])

    prompt = f"""
You are an exeprt travel content editor.

Your job is NOT to rewrite blindly.
Your job is to IMPROVE the blog based on SPECIFIC feedback, review and critical issues.

---

 ORIGINAL BLOG
{blog}

REVIEW
{review}
---

 REVIEW FEEDBACK (CRITICAL INPUT)
{feedback}

---

 YOUR TASK (VERY IMPORTANT)

Step 1: Identify weak areas based on feedback

Step 2: Improve ONLY those areas:
- strengthen intro (hook, bold claim)
- add strong opinions / non-obvious insights
- remove generic phrasing
- add practical details if missing
- improve uniqueness

Step 3: Keep:
- structure
- good sections
- useful content

---

 MANDATORY IMPROVEMENTS

You MUST:

1. Strengthen the introduction:
   - add a bold or contrarian statement
   - make reader curious immediately

2. Add at least 2 strong opinions:
   - challenge common advice
   - give insider perspective

3. Increase uniqueness:
   - add non-obvious tips
   - avoid safe content

4. If missing:
   - improve FAQ section
   - add stronger practical insights

---

 IMPORTANT RULES

- Do NOT rewrite everything
- Only improve weak parts
- Keep blog length similar
- Keep it natural and human

---

 OUTPUT

Return the FULL improved blog.

Do NOT explain changes.
Do NOT return JSON.
"""
    if errors:
      prompt += f"""

   --- CRITICAL ISSUES TO FIX ---
   {errors}

   You MUST fix ALL these issues.
   Do not ignore them.
   """

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    return response.text