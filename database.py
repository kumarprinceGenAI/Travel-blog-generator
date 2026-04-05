import sqlite3
import os


DB_PATH = os.getenv("DB_PATH", "blogs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 🔥 CRITICAL FIX
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Blogs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        slug TEXT,
        blog TEXT,
        html TEXT,
        seo TEXT,
        images TEXT,
        created_at TEXT
    )
    """)

    # ✅ Metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        score REAL,
        iterations INTEGER,
        status TEXT,
        created_at TEXT,
        content_length INTEGER,
        error_count INTEGER,
        improved BOOLEAN,
        time_taken REAL,
        improvement_delta REAL
    )
    """)

    # ✅ Topic embeddings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        embedding BLOB
    )
    """)

    # ✅ Versioning
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blog_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        iteration INTEGER,
        content TEXT,
        created_at TEXT
    )
    """)





    conn.commit()
    conn.close()