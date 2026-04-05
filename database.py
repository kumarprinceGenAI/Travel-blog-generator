import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set")

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",  # 🔥 REQUIRED for Supabase
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Blogs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id SERIAL PRIMARY KEY,
        topic TEXT,
        slug TEXT UNIQUE,
        blog TEXT,
        html TEXT,
        seo JSONB,
        images JSONB,
        created_at TIMESTAMP
    )
    """)

    # ✅ Metrics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id SERIAL PRIMARY KEY,
        topic TEXT,
        score FLOAT,
        iterations INTEGER,
        status TEXT,
        created_at TIMESTAMP,
        content_length INTEGER,
        error_count INTEGER,
        improved BOOLEAN,
        time_taken FLOAT,
        improvement_delta FLOAT
    )
    """)

    # ✅ Topic embeddings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_embeddings (
        id SERIAL PRIMARY KEY,
        topic TEXT,
        embedding BYTEA
    )
    """)

    # ✅ Versioning
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blog_versions (
        id SERIAL PRIMARY KEY,
        topic TEXT,
        iteration INTEGER,
        content TEXT,
        created_at TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()