from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from planner import planner_agent
from writer import writer_agent
from reviewer import reviewer_agent
from improver import improver_agent
from seo import seo_agent
from researcher import researcher_agent, calculate_score

from memory import is_duplicate, save_topic
from storage import save_blog

from logger import logger
from validators import validate_plan, validate_blog, validate_review
from retry import retry
from metrics import save_metrics
from versioning import save_version
from content_validator import validate_content_quality
import time


# =========================
# STATE
# =========================
class BlogState(TypedDict, total=False):
    topic: str
    plan: dict
    blog: str
    review: dict
    seo: dict
    html: str
    iterations: int
    validation_errors: list
    start_time: float


# =========================
# NODES
# =========================

def researcher_node(state):
    logger.info("Researcher started")

    data = researcher_agent()
    topics = data.get("topics", [])

    if not topics:
        logger.error("No topics returned by researcher")
        return state

    unique_topics = [
        t for t in topics if not is_duplicate(t.get("title"))
    ]

    if not unique_topics:
        logger.warning("No unique topics found, skipping run")
        return state

    # 🔥 Score topics
    for t in unique_topics:
        t["final_score"] = calculate_score(t)

    best_topic = max(unique_topics, key=lambda x: x["final_score"])

    logger.info(
        f"Selected Topic: {best_topic['title']} | Score: {best_topic['final_score']}"
    )

    state["topic"] = best_topic["title"]
    state["topic_meta"] = best_topic
    state["iterations"] = 0

    return state


def planner_node(state):
    logger.info(f"Planner running for topic: {state['topic']}")

    raw_plan = retry(
        lambda: planner_agent(state["topic"]),
        name="planner"
    )

    state["plan"] = validate_plan(raw_plan)

    return state


def writer_node(state):
    logger.info("Writer generating blog")

    try:
        blog = retry(
            lambda: writer_agent(state["plan"]),
            name="writer",
            validate=validate_blog
        )

        state["blog"] = blog

        # 🔥 Collect validation issues (NON-BLOCKING)
        errors = validate_content_quality(blog)
        state["validation_errors"] = errors

    except Exception as e:
        logger.error(f"Writer failed completely: {str(e)}")
        raise Exception(f"Writer failed: {str(e)}")

    # 🔥 Save initial version
    if state["blog"]:
        save_version(
            topic=state["topic"],
            iteration=0,
            content=state["blog"]
        )

    return state


def reviewer_node(state):
    logger.info("Reviewer evaluating blog")

    state["review"] = retry(
        lambda: reviewer_agent(state["blog"]),
        name="reviewer",
        validate=validate_review
    )

    logger.info(f"Reviewer scores: {state['review']}")

    return state


def improver_node(state):
    if not state.get("blog"):
        logger.error("Improver skipped: no blog available")
        return state

    logger.info("Improver refining blog")

    errors = state.get("validation_errors")
    errors_text = " | ".join(errors) if errors else None  # ✅ FIX

    try:
        improved = retry(
            lambda: improver_agent(
                state["blog"],
                state["review"],
                errors_text
            ),
            name="improver",
            validate=validate_blog
        )

        # ✅ Update blog
        state["blog"] = improved
        state["iterations"] = state.get("iterations", 0) + 1

        # 🔥 Re-validate after improvement (CRITICAL FIX)
        new_errors = validate_content_quality(improved)
        state["validation_errors"] = new_errors

        # ✅ Save improved version
        save_version(
            topic=state["topic"],
            iteration=state["iterations"],
            content=improved
        )

    except Exception as e:
        logger.warning(f"Improver failed, keeping original blog | Error: {str(e)}")

    return state


def seo_node(state):
    logger.info("SEO started")

    state["seo"] = retry(
        lambda: seo_agent(state["blog"]),
        name="seo"
    )

    return state


def render_node(state):
    logger.info("Rendering HTML")

    from renderer import render_html
    state["html"] = render_html(state["blog"])

    return state


def save_node(state):
    if not state.get("blog"):
        logger.error("Skipping save: blog missing")
        return state

    if not state.get("html"):
        logger.warning("HTML missing, generating fallback")

        from renderer import render_html
        state["html"] = render_html(state["blog"])

    logger.info("Saving blog to database")

    data = {
        "topic": state.get("topic"),
        "blog": state.get("blog"),
        "html": state.get("html"),
        "seo": state.get("seo"),
    }

    save_blog(data)

    # 🔥 SAVE METRICS (UPGRADED)
    if state.get("review"):
        score = (
            state["review"]["content_score"] +
            state["review"]["seo_score"] +
            state["review"]["readability_score"] +
            state["review"]["uniqueness_score"]
        ) / 4

        blog_text = state.get("blog", "")
        validation_errors = state.get("validation_errors") or []

        content_length = len(blog_text.split())
        error_count = len(validation_errors)
        improved = state.get("iterations", 0) > 0
        start_time = state.get("start_time")
        time_taken = round(time.time() - start_time, 2) if start_time else None
        save_metrics(
            topic=state["topic"],
            score=score,
            iterations=state.get("iterations", 0),
            status="success",
            content_length=content_length,
            error_count=error_count,
            improved=improved,
            time_taken=time_taken
        )

        logger.info(
            f"Metrics | Score: {score} | Iter: {state.get('iterations')} | "
            f"Len: {content_length} | Errors: {error_count} | Time: {time_taken}s"
        )

    logger.info("Blog saved to DB")

    save_topic(state.get("topic"))

    return state


def decision_node(state):
    r = state["review"]

    score = (
        r["content_score"] +
        r["seo_score"] +
        r["readability_score"] +
        r["uniqueness_score"]
    ) / 4

    iterations = state.get("iterations", 0)

    logger.info(f"Avg Score: {score} | Iterations: {iterations}")

    if iterations == 0:
        return "improver"
    
    if score >= 9.2:
        logger.info("High-quality blog → skipping improver")
        return "seo"

    if score < 9.2 and iterations < 2:
        return "improver"

    logger.info(f"FINAL RESULT | Score: {score} | Iterations: {iterations}")
    return "seo"


# =========================
# GRAPH BUILD
# =========================

builder = StateGraph(BlogState)

builder.add_node("researcher", researcher_node)
builder.add_node("planner", planner_node)
builder.add_node("writer", writer_node)
builder.add_node("reviewer", reviewer_node)
builder.add_node("improver", improver_node)
builder.add_node("seo", seo_node)
builder.add_node("renderer", render_node)
builder.add_node("save", save_node)

builder.add_edge(START, "researcher")
builder.add_edge("researcher", "planner")
builder.add_edge("planner", "writer")
builder.add_edge("writer", "reviewer")

builder.add_conditional_edges(
    "reviewer",
    decision_node,
    {
        "improver": "improver",
        "seo": "seo"
    }
)

builder.add_edge("improver", "reviewer")
builder.add_edge("seo", "renderer")
builder.add_edge("renderer", "save")
builder.add_edge("save", END)

graph = builder.compile()