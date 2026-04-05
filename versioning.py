from datetime import datetime
from database import get_connection



def save_version(topic, iteration, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO blog_versions (topic, iteration, content, created_at)
    VALUES (%s, %s, %s, %s)
    """, (
        topic,
        iteration,
        content,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()