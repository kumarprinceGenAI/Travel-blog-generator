
from datetime import datetime
from database import get_connection
from logger import logger
import time
from psycopg2.extras import Json

# -----------------------------
# SLUG GENERATOR
# -----------------------------
def generate_slug(topic: str):
    return (
        topic.lower()
        .replace(" ", "-")
        .replace(",", "")
        .replace(":", "")
    )[:100]


# -----------------------------
# SAVE BLOG
# -----------------------------
def save_blog(data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    slug = generate_slug(data.get("topic", ""))

    # ✅ ensure uniqueness
    cursor.execute(
        "SELECT COUNT(*) as count FROM blogs WHERE slug = %s",
        (slug,)
    )
    existing = cursor.fetchone()["count"]

    if existing:
        slug = f"{slug}-{int(time.time())}"

    images = data.get("images", [])
    seo = data.get("seo", {})

    cursor.execute("""
    INSERT INTO blogs (topic, blog, html, seo, slug, images, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get("topic"),
        data.get("blog"),
        data.get("html") or "",
        Json(seo),          # ✅ JSONB direct
        slug,
        Json(images),       # ✅ JSONB direct
        datetime.now()
    ))

    conn.commit()
    conn.close()

    logger.info("Blog saved with slug + images")


# -----------------------------
# GET BLOGS
# -----------------------------
def get_blogs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, topic, created_at, slug
    FROM blogs
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "topic": r["topic"],
            "created_at": r["created_at"],
            "slug": r["slug"]
        }
        for r in rows
    ]


# -----------------------------
# GET BLOG BY ID
# -----------------------------
def get_blog(blog_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM blogs WHERE id = %s
    """, (blog_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "topic": row["topic"],
        "blog": row["blog"],
        "html": row["html"],
        "seo": row["seo"] or {},
        "created_at": row["created_at"],
        "slug": row["slug"],
        "images": row["images"] or []
    }


# -----------------------------
# GET LATEST BLOG
# -----------------------------
def get_latest_blog():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT topic, blog, html, seo, images
    FROM blogs
    ORDER BY id DESC
    LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {}

    return {
        "topic": row["topic"],
        "blog": row["blog"],
        "html": row["html"],
        "seo": row["seo"] or {},
        "images": row["images"] or []
    }


# -----------------------------
# GET BLOG BY SLUG
# -----------------------------
def get_blog_by_slug(slug: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM blogs WHERE slug = %s
    """, (slug,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "topic": row["topic"],
        "slug": row["slug"],
        "html": row["html"],
        "images": row["images"] or [],
        "seo": row["seo"] or {},
        "created_at": row["created_at"]
    }