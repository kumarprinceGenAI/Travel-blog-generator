import sqlite3

DB_NAME = "blogs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ✅ Blogs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        blog TEXT,
        html TEXT,
        seo TEXT,
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
        created_at TEXT
    )
    """)

    # ✅ Topic Embeddings table (NEW)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        embedding BLOB
    )
    """)

    # 🔥 SAFE COLUMN ADDITIONS (NO BREAKAGE)
    try:
        cursor.execute("ALTER TABLE metrics ADD COLUMN content_length INTEGER")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE metrics ADD COLUMN error_count INTEGER")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE metrics ADD COLUMN improved BOOLEAN")
    except:
        pass

    try:
        cursor.execute("ALTER TABLE metrics ADD COLUMN time_taken REAL")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE metrics ADD COLUMN improvement_delta REAL")
    except:
        pass

    # ✅ Versioning table
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