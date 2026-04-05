import sqlite3
from datetime import datetime
from database import get_connection


def save_metrics(
    topic=None,
    score=None,
    iterations=None,
    status="success",
    content_length=None,
    error_count=None,
    improved=None,
    time_taken=None,
    improvement_delta=None   
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO metrics (
            topic, score, iterations, status,
            content_length, error_count, improved, time_taken,
            improvement_delta,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
    topic,
    score,
    iterations,
    status,
    content_length,
    error_count,
    improved,
    time_taken,
    improvement_delta,
    datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()


def get_metrics_summary():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Basic success metrics
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

    # 🔥 Get all scores (needed for advanced metrics)
    cursor.execute("""
    SELECT score FROM metrics
    WHERE status = 'success'
    ORDER BY created_at DESC
    """)
    scores = [row[0] for row in cursor.fetchall()]

    # 🔥 SCORE DISTRIBUTION
    low = len([s for s in scores if s < 8])
    medium = len([s for s in scores if 8 <= s < 9])
    high = len([s for s in scores if s >= 9])

    # 🔥 IMPROVEMENT RATE (REAL)
    cursor.execute("""
    SELECT COUNT(*) FROM metrics
    WHERE improvement_delta > 0
    """)
    improved_actual = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM metrics
    WHERE improvement_delta IS NOT NULL
    """)
    total_improvable = cursor.fetchone()[0]

    improvement_rate = (
        (improved_actual / total_improvable) * 100
        if total_improvable else 0
    )

    # 🔥 VARIANCE (STABILITY)
    import numpy as np
    variance = float(np.var(scores)) if scores else 0

    # 🔥 REGRESSION DETECTION
    recent_scores = scores[:5]
    previous_scores = scores[5:10]

    recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0
    previous_avg = sum(previous_scores) / len(previous_scores) if previous_scores else 0

    regression = False
    if previous_scores and (recent_avg < previous_avg - 0.3):
        regression = True

    # 🔥 FAILURES
    cursor.execute("""
    SELECT COUNT(*)
    FROM metrics
    WHERE status = 'failure'
    """)
    failures = cursor.fetchone()[0]

    conn.close()

    # 🔥 SYSTEM STATUS (INTELLIGENCE LAYER)
    if regression:
        status = "regression_detected"
    elif variance > 0.5:
        status = "unstable"
    elif avg_score and avg_score >= 9:
        status = "excellent"
    elif avg_score and avg_score >= 8:
        status = "good"
    else:
        status = "needs_improvement"

    return {
        "total_success": total_success or 0,
        "average_score": round(avg_score or 0, 2),
        "average_iterations": round(avg_iterations or 0, 2),
        "average_content_length": int(avg_length or 0),
        "average_error_count": round(avg_errors or 0, 2),

        # 🔥 NEW
        "score_distribution": {
            "low (<8)": low,
            "medium (8-9)": medium,
            "high (9+)": high
        },
        "improvement_rate": round(improvement_rate, 2),
        "variance": round(variance, 3),
        "regression_detected": regression,
        "recent_avg": round(recent_avg, 2),
        "previous_avg": round(previous_avg, 2),

        "failures": failures or 0,
        "status": status
    }

def get_top_topics(limit=3):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT topic
    FROM metrics
    WHERE score >= 8.8 AND status = 'success'
    ORDER BY score DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [r[0] for r in rows]

def get_low_performing_topics(limit=3):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT topic
    FROM metrics
    WHERE score <= 7.5 AND status = 'success'
    ORDER BY score ASC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [r[0] for r in rows]