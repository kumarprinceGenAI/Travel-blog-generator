from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from planner import planner_agent
from writer import writer_agent
from reviewer import reviewer_agent
from improver import improver_agent
from seo import seo_agent
from researcher import researcher_agent, calculate_score
from image_agent import generate_images_for_blog

from memory import is_duplicate, save_topic, is_semantic_duplicate
from storage import save_blog

from logger import logger
from validators import validate_plan, validate_blog, validate_review
from retry import retry
from metrics import save_metrics
from versioning import save_version
from content_validator import validate_content_quality
import time
from embedding import get_embedding
import pickle
import sqlite3
from linking_engine import get_related_topics, inject_internal_links
from renderer import render_html
from database import get_connection


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
    initial_score: float
    final_score: float
    images:list


# =========================
# NODES
# =========================

def image_node(state):
    logger.info("Image generation started")

    try:
        images = generate_images_for_blog(state["blog"])

        if images:
            state["images"] = images
            logger.info(f"[Images] Attached {len(images)} images")
        else:
            state["images"] = []
            logger.warning("[Images] No images attached")

    except Exception as e:
        logger.error(f"[Images] Failed: {str(e)}")
        state["images"] = []

    return state

def is_overused_theme(title: str):
    title_lower = title.lower()

    keywords = ["visa", "budget", "digital nomad"]

    return any(k in title_lower for k in keywords)


def researcher_node(state):
    logger.info("Researcher started")

    data = researcher_agent()
    topics = data.get("topics", [])

    if not topics:
        logger.error("No topics returned by researcher")
        return state

    # 🔥 UPDATED: Hybrid duplicate filtering (exact + semantic)
    unique_topics = []

    for t in topics:
        title = t.get("title")

        if is_duplicate(title):
            logger.info(f"[Dedup] Exact duplicate skipped: {title}")
            continue

        if is_semantic_duplicate(title):
            logger.info(f"[Semantic Dedup] Skipping similar topic: {title}")
            continue

        unique_topics.append(t)

    if not unique_topics:
        logger.warning("No unique topics found, skipping run")
        return state

    # ✅ Score topics
    for t in unique_topics:
        t["final_score"] = calculate_score(t)

    # 🔥 split topics into balanced groups
    diverse_topics = [t for t in unique_topics if not is_overused_theme(t["title"])]
    trend_topics = [t for t in unique_topics if is_overused_theme(t["title"])]

    # 🔥 LOG for visibility
    logger.info(f"[Researcher] Diverse Topics: {[t['title'] for t in diverse_topics]}")
    logger.info(f"[Researcher] Trend Topics: {[t['title'] for t in trend_topics]}")

    # 🔥 allow strong trend topics if much better
    best_diverse = max(diverse_topics, key=lambda x: x["final_score"]) if diverse_topics else None
    best_trend = max(trend_topics, key=lambda x: x["final_score"]) if trend_topics else None

    if best_diverse and best_trend:
        if best_trend["final_score"] - best_diverse["final_score"] > 0.7:
            logger.info("[Researcher] Selecting HIGH-SCORE TREND topic")
            best_topic = best_trend
        else:
            logger.info("[Researcher] Selecting BALANCED DIVERSE topic")
            best_topic = best_diverse

    elif best_diverse:
        logger.info("[Researcher] Selecting DIVERSE topic")
        best_topic = best_diverse

    else:
        logger.info("[Researcher] Fallback to TREND topic")
        best_topic = best_trend

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

    if not raw_plan:
        logger.warning("[Planner] Empty output → using fallback")
        raw_plan = {}

    # 🔥 BACKWARD COMPAT FIX (STRUCTURE SAFE)
    if "seo_keywords" not in raw_plan:
        kw = raw_plan.get("keywords", {})

        raw_plan["seo_keywords"] = {
            "primary_keyword": kw.get("primary_keyword", ""),
            "secondary_keywords": kw.get("secondary_keywords", []),
            "long_tail_keywords": kw.get("long_tail_keywords", [])
        }

    # 🔥 FINAL SAFE VALIDATION
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

    r = state["review"]

    required_keys = [
    "content_score",
    "seo_score",
    "readability_score",
    "uniqueness_score"
]

    if not r or any(k not in r for k in required_keys):
        logger.error("[Reviewer] Invalid response → applying fallback")

        r = {
            "content_score": 6.5,
            "seo_score": 6.5,
            "readability_score": 7.0,
            "uniqueness_score": 6.5,
            "verdict": "needs_improvement",
            "feedback": ["Fallback applied due to invalid reviewer output"]
        }

        state["review"] = r
    
    score = (
        r["content_score"] +
        r["seo_score"] +
        r["readability_score"] +
        r["uniqueness_score"]
    ) / 4

    if "initial_score" not in state:
        state["initial_score"] = score

    # 🔥 ALWAYS UPDATE FINAL SCORE
    state["final_score"] = score

    logger.info(f"Reviewer scores: {state['review']} | Avg: {score}")

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

    html = render_html(
        state.get("blog"),
        state.get("images")
    )

    if not html:
        logger.error("HTML generation failed")
        state["html"] = ""
    else:
        state["html"] = html

    logger.info(f"[Renderer] HTML length: {len(state['html'])}")

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

    

    # 🔥 INTERNAL LINKING (NEW)

    print(f"[Linking] 🚀 Starting internal linking for topic: {state.get('topic')}")
    related = get_related_topics(state["topic"])

    if related:
        state["blog"] = inject_internal_links(state["blog"], related)
    print(f"[Linking] ✅ Internal linking completed")

    

    data = {
    "topic": state.get("topic"),
    "blog": state.get("blog"),
    "html": state.get("html"),
    "seo": state.get("seo"),
    "images": state.get("images", [])   # 🔥 THIS WAS MISSING
        }
    save_blog(data)

    embedding = get_embedding(state["topic"])

    if embedding is not None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO topic_embeddings (topic, embedding) VALUES (%s, %s)",
            (state["topic"], pickle.dumps(embedding))
        )

        conn.commit()
        conn.close()

    # 🔥 SAVE METRICS (FINAL VERSION)
    if state.get("review"):
        r = state["review"]

        score = (
            r["content_score"] +
            r["seo_score"] +
            r["readability_score"] +
            r["uniqueness_score"]
        ) / 4

        blog_text = state.get("blog", "")
        validation_errors = state.get("validation_errors") or []

        content_length = len(blog_text.split())
        error_count = len(validation_errors)
        improved = state.get("iterations", 0) > 0

        # 🔥 TIME
        start_time = state.get("start_time")
        time_taken = round(time.time() - start_time, 2) if start_time else None

        # 🔥 IMPROVEMENT TRACKING
        initial_score = state.get("initial_score")
        final_score = state.get("final_score")

        improvement_delta = (
            round(final_score - initial_score, 3)
            if initial_score is not None and final_score is not None
            else None
        )

        save_metrics(
            topic=state["topic"],
            score=score,
            iterations=state.get("iterations", 0),
            status="success",
            content_length=content_length,
            error_count=error_count,
            improved=improved,
            time_taken=time_taken,
            improvement_delta=improvement_delta
        )

        logger.info(
            f"Metrics | Score: {score} | Iter: {state.get('iterations')} | "
            f"Len: {content_length} | Errors: {error_count} | "
            f"Delta: {improvement_delta} | Time: {time_taken}s"
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

    
    if score >= 9.0:
        logger.info("High-quality blog → skipping improver")
        return "seo"
    
    if iterations < 2:
        logger.info("Sending to improver")
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
builder.add_node("images",image_node,)

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
builder.add_edge("seo", "images")
builder.add_edge("images","renderer")
builder.add_edge("renderer", "save")
builder.add_edge("save", END)

graph = builder.compile()