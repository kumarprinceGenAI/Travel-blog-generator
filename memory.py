import sqlite3

DB_NAME = "blogs.db"


def is_duplicate(topic: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # exact match (fast + reliable baseline)
    cursor.execute(
        "SELECT 1 FROM blogs WHERE LOWER(topic) = LOWER(?) LIMIT 1",
        (topic,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None


def save_topic(topic: str):
    # 🔥 NO-OP (topic already saved via save_blog)
    return