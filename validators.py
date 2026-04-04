import json


REQUIRED_PLAN_KEYS = [
    "intent",
    "persona",
    "audience",
    "blog_type",
    "tone",
    "sections",
    "local_context",
    "seo_keywords"
]


def validate_plan(plan: dict):
    if not isinstance(plan, dict):
        print("[Validator] Invalid plan → using fallback")
        plan = {}

    for key in REQUIRED_PLAN_KEYS:
        if key not in plan:
            print(f"[Validator] Missing key → {key}")

            if key == "sections":
                plan[key] = []

            elif key == "local_context":
                plan[key] = {
                    "currency": "INR (₹)",
                    "budget_range": "",
                    "transport_examples": "",
                    "practical_notes": ""
                }

            elif key == "seo_keywords":
                # 🔥 FIXED → keep STRUCTURE
                plan[key] = {
                    "primary_keyword": "",
                    "secondary_keywords": [],
                    "long_tail_keywords": []
                }

            else:
                plan[key] = ""

    return plan


# 🔹 Writer Validation
def validate_blog(blog: str):
    if not blog or len(blog) < 800:
        raise ValueError("Blog too short or empty")

    if "##" not in blog:
        raise ValueError("Blog missing structure (headings)")

    return blog


# 🔹 Reviewer Validation
def validate_review(review: dict):
    required = [
        "content_score",
        "seo_score",
        "readability_score",
        "uniqueness_score",
        "verdict"
    ]

    for key in required:
        if key not in review:
            raise ValueError(f"Reviewer missing: {key}")

    for score_key in required[:-1]:
        score = review[score_key]
        if not (0 <= score <= 10):
            raise ValueError(f"Invalid score: {score_key}")

    return review