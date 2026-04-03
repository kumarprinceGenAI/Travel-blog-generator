import sqlite3
from datetime import datetime

DB_NAME = "blogs.db"


def save_metrics(
    topic=None,
    score=None,
    iterations=None,
    status="success",
    content_length=None,
    error_count=None,
    improved=None,
    time_taken=None
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO metrics (
        topic, score, iterations, status,
        content_length, error_count, improved, time_taken,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        topic,
        score,
        iterations,
        status,
        content_length,
        error_count,
        improved,
        time_taken,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_metrics_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ✅ Success metrics
    cursor.execute("""
    SELECT COUNT(*), AVG(score)
    FROM metrics
    WHERE status = 'success'
    """)
    total_success, avg_score = cursor.fetchone()

    cursor.execute("""
    SELECT AVG(iterations)
    FROM metrics
    WHERE status = 'success'
    """)
    avg_iterations = cursor.fetchone()[0]

    cursor.execute("""
    SELECT AVG(content_length), AVG(error_count)
    FROM metrics
    WHERE status = 'success'
    """)
    avg_length, avg_errors = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*) FROM metrics
    WHERE improved = 1
    """)
    improved_count = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM metrics
    WHERE status = 'success'
    """)
    total_runs = cursor.fetchone()[0]

    improvement_rate = (improved_count / total_runs * 100) if total_runs else 0

    # ✅ Failures
    cursor.execute("""
    SELECT COUNT(*)
    FROM metrics
    WHERE status = 'failure'
    """)
    failures = cursor.fetchone()[0]

    conn.close()

    return {
        "total_success": total_success or 0,
        "average_score": round(avg_score or 0, 2),
        "average_iterations": round(avg_iterations or 0, 2),
        "average_content_length": int(avg_length or 0),
        "average_error_count": round(avg_errors or 0, 2),
        "improvement_rate": round(improvement_rate, 2),
        "failures": failures or 0
    }