import sqlite3
from datetime import datetime

DB_NAME = "blogs.db"


def save_version(topic, iteration, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO blog_versions (topic, iteration, content, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        topic,
        iteration,
        content,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()