import sqlite3
from datetime import datetime
import json
from database import init_db
from logger import logger

DB_NAME = "blogs.db"

# Ensure DB exists
init_db()


def save_blog(data: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO blogs (topic, blog, html, seo, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("topic"),
        data.get("blog"),
        data.get("html"),
        json.dumps(data.get("seo")),  # store SEO as string
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    logger.info("Blog saved to DB")


def get_blogs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, topic, created_at FROM blogs ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": r[0],
            "topic": r[1],
            "created_at": r[2]
        }
        for r in rows
    ]


def get_blog(blog_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, topic, blog, html, seo, created_at
    FROM blogs WHERE id = ?
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
        "created_at": row[5]
    }

def get_latest_blog():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT topic, blog, html, seo
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
        "seo": row[3]
    }