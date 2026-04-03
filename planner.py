from google import genai
import os
from dotenv import load_dotenv
from utils import safe_generate
from researcher import extract_json 

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def planner_agent(topic: str):
    prompt = f"""
        You are a professional travel content strategist and SEO expert.

        Your job is to create a HIGH-RANKING blog plan (not generic).

        TOPIC:
        {topic}

        ---

        CRITICAL REQUIREMENTS (NON-NEGOTIABLE):

        1. DEFINE SEARCH INTENT
        - Choose one: informational / itinerary / budget / comparison
        - Make topic more specific and rankable

        2. DEFINE TARGET PERSONA
        Choose ONE:
        - budget traveler
        - solo traveler
        - couple traveler
        - digital nomad

        3. LOCALIZATION (VERY IMPORTANT)
        - Assume audience is from India
        - Use INR (₹) context
        - Include real-world travel details (costs, transport, timing)

        4. MAKE CONTENT PRACTICAL
        - Include real places, routes, tips
        - Avoid generic content
        5. ADD EXPERIENCE + EDGE
        - Include at least 1 section that:
            - highlights mistakes travelers make
            - gives insider/local tips
            - includes non-obvious advice

        6. AVOID GENERIC CONTENT
        - If sections look like common travel blogs, make them more unique

        7. INCLUDE REAL-WORLD PROBLEMS
        - heat, crowds, pricing traps, transport issues
        ---

         OUTPUT FORMAT (STRICT JSON ONLY):

        {{
        "intent": "...",
        "persona": "...",
        "audience": "...",
        "blog_type": "...",
        "tone": "...",

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
        }},

        "seo_keywords": ["...", "..."]
        }}

        ---

        STRICT RULES:
        - NO markdown
        - NO explanations
        - ONLY valid JSON
        - Avoid generic phrases like "famous for"
        """

    response = safe_generate(lambda: client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ))

    
    return extract_json(response.text)