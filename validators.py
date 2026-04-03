import json


# 🔹 Planner Validation
def validate_plan(plan_input):
    # If already dict → use directly
    if isinstance(plan_input, dict):
        plan = plan_input
    else:
        try:
            plan = json.loads(plan_input)
        except:
            raise ValueError("Invalid JSON from planner")

    required_keys = ["audience", "sections", "seo_keywords"]

    for key in required_keys:
        if key not in plan:
            raise ValueError(f"Planner output missing key: {key}")

    if not isinstance(plan["sections"], list) or len(plan["sections"]) == 0:
        raise ValueError("Planner sections invalid")

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