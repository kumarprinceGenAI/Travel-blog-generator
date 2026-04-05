import json
from datetime import datetime
from database import get_connection, init_db
from logger import logger
import time




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
# SAVE BLOG (FIXED)
# -----------------------------
def save_blog(data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    slug = generate_slug(data.get("topic", ""))

    # ensure uniqueness
    existing = cursor.execute(
        "SELECT COUNT(*) FROM blogs WHERE slug = ?", (slug,)
    ).fetchone()[0]

    if existing:
        slug = f"{slug}-{int(time.time())}"

    images = data.get("images", [])
    images_json = json.dumps(images)

    cursor.execute("""
    INSERT INTO blogs (topic, blog, html, seo, slug, images, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("topic"),
        data.get("blog"),
        data.get("html") or "",
        json.dumps(data.get("seo") or {}),
        slug,
        images_json,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    logger.info("Blog saved with slug + images")


# -----------------------------
# GET BLOGS (LIST)
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
            "id": r[0],
            "topic": r[1],
            "created_at": r[2],
            "slug": r[3]
        }
        for r in rows
    ]


# -----------------------------
# GET SINGLE BLOG
# -----------------------------
def get_blog(blog_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, topic, blog, html, seo, created_at, slug, images
    FROM blogs
    WHERE id = ?
    """, (blog_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "topic": row[1],
        "blog": row[2],
        "html": row[3],
        "seo": json.loads(row[4]) if row[4] else {},
        "created_at": row[5],
        "slug": row[6],
        "images": json.loads(row[7]) if row[7] else []
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
        "topic": row[0],
        "blog": row[1],
        "html": row[2],
        "seo": json.loads(row[3]) if row[3] else {},
        "images": json.loads(row[4]) if row[4] else []
    }

def get_blog_by_slug(slug: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM blogs WHERE slug = ?
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
        "images": json.loads(row["images"]) if row["images"] else [],
        "seo": json.loads(row["seo"]) if row["seo"] else {},
        "created_at": row["created_at"]
    }