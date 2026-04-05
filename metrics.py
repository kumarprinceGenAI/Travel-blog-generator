from datetime import datetime
from database import get_connection
import numpy as np


# -----------------------------
# SAVE METRICS
# -----------------------------
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
            improvement_delta, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        datetime.now()
    ))

    conn.commit()
    conn.close()


# -----------------------------
# METRICS SUMMARY
# -----------------------------
def get_metrics_summary():
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Total success + avg score
    cursor.execute("""
        SELECT COUNT(*) as count, AVG(score) as avg
        FROM metrics
        WHERE status = 'success'
    """)
    row = cursor.fetchone()
    total_success = row["count"]
    avg_score = row["avg"]

    # ✅ Avg iterations
    cursor.execute("""
        SELECT AVG(iterations) as avg
        FROM metrics
        WHERE status = 'success'
    """)
    avg_iterations = cursor.fetchone()["avg"]

    # ✅ Avg length + errors
    cursor.execute("""
        SELECT AVG(content_length) as avg_length,
               AVG(error_count) as avg_errors
        FROM metrics
        WHERE status = 'success'
    """)
    row = cursor.fetchone()
    avg_length = row["avg_length"]
    avg_errors = row["avg_errors"]

    # 🔥 Get all scores
    cursor.execute("""
        SELECT score FROM metrics
        WHERE status = 'success'
        ORDER BY created_at DESC
    """)
    scores = [row["score"] for row in cursor.fetchall()]

    # 🔥 Distribution
    low = len([s for s in scores if s < 8])
    medium = len([s for s in scores if 8 <= s < 9])
    high = len([s for s in scores if s >= 9])

    # 🔥 Improvement rate
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM metrics
        WHERE improvement_delta > 0
    """)
    improved_actual = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM metrics
        WHERE improvement_delta IS NOT NULL
    """)
    total_improvable = cursor.fetchone()["count"]

    improvement_rate = (
        (improved_actual / total_improvable) * 100
        if total_improvable else 0
    )

    # 🔥 Variance
    variance = float(np.var(scores)) if scores else 0

    # 🔥 Regression detection
    recent_scores = scores[:5]
    previous_scores = scores[5:10]

    recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0
    previous_avg = sum(previous_scores) / len(previous_scores) if previous_scores else 0

    regression = False
    if previous_scores and (recent_avg < previous_avg - 0.3):
        regression = True

    # 🔥 Failures
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM metrics
        WHERE status = 'failure'
    """)
    failures = cursor.fetchone()["count"]

    conn.close()

    # 🔥 System status
    if regression:
        status_label = "regression_detected"
    elif variance > 0.5:
        status_label = "unstable"
    elif avg_score and avg_score >= 9:
        status_label = "excellent"
    elif avg_score and avg_score >= 8:
        status_label = "good"
    else:
        status_label = "needs_improvement"

    return {
        "total_success": total_success or 0,
        "average_score": round(avg_score or 0, 2),
        "average_iterations": round(avg_iterations or 0, 2),
        "average_content_length": int(avg_length or 0),
        "average_error_count": round(avg_errors or 0, 2),

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
        "status": status_label
    }


# -----------------------------
# TOP TOPICS
# -----------------------------
def get_top_topics(limit=3):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic
        FROM metrics
        WHERE score >= 8.8 AND status = 'success'
        ORDER BY score DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [r["topic"] for r in rows]


# -----------------------------
# LOW PERFORMING TOPICS
# -----------------------------
def get_low_performing_topics(limit=3):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic
        FROM metrics
        WHERE score <= 7.5 AND status = 'success'
        ORDER BY score ASC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [r["topic"] for r in rows]