import sqlite3
import numpy as np
from database import get_connection




# -------------------------------
# 1. SCORE DISTRIBUTION
# -------------------------------
def get_score_distribution():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM metrics")
    scores = [row[0] for row in cursor.fetchall() if row[0] is not None]

    conn.close()

    dist = {
        "7-8": 0,
        "8-9": 0,
        "9+": 0
    }

    for s in scores:
        if 7 <= s < 8:
            dist["7-8"] += 1
        elif 8 <= s < 9:
            dist["8-9"] += 1
        elif s >= 9:
            dist["9+"] += 1

    return dist


# -------------------------------
# 2. REGRESSION DETECTION
# -------------------------------
def detect_regression(window=5):
    conn = get_connection()
    cursor = conn.cursor()

    # Recent scores
    cursor.execute("""
        SELECT score FROM metrics
        WHERE score IS NOT NULL
        ORDER BY id DESC
        LIMIT ?
    """, (window,))
    recent = [row[0] for row in cursor.fetchall()]

    # Previous window
    cursor.execute("""
        SELECT score FROM metrics
        WHERE score IS NOT NULL
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (window, window))
    previous = [row[0] for row in cursor.fetchall()]

    conn.close()

    if len(recent) < window or len(previous) < window:
        return {"status": "not_enough_data"}

    avg_recent = sum(recent) / len(recent)
    avg_previous = sum(previous) / len(previous)

    if avg_recent < avg_previous:
        return {
            "regression": True,
            "previous_avg": round(avg_previous, 2),
            "recent_avg": round(avg_recent, 2),
            "drop": round(avg_previous - avg_recent, 2)
        }

    return {
        "regression": False,
        "previous_avg": round(avg_previous, 2),
        "recent_avg": round(avg_recent, 2)
    }


# -------------------------------
# 3. COMPONENT PERFORMANCE
# -------------------------------
def component_performance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT iterations, improved, error_count
        FROM metrics
    """)

    rows = cursor.fetchall()
    conn.close()

    total = len(rows)

    if total == 0:
        return {"status": "no_data"}

    improvements = sum(1 for r in rows if r[1])
    total_iterations = sum(r[0] for r in rows if r[0] is not None)
    total_errors = sum(r[2] for r in rows if r[2] is not None)

    return {
        "total_runs": total,
        "improvement_rate": round(improvements / total, 2),
        "avg_iterations": round(total_iterations / total, 2),
        "avg_errors": round(total_errors / total, 2)
    }


# -------------------------------
# 4. SCORE STABILITY
# -------------------------------
def score_stability():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM metrics WHERE score IS NOT NULL")
    scores = [row[0] for row in cursor.fetchall()]

    conn.close()

    if len(scores) < 2:
        return {"status": "not_enough_data"}

    return {
        "mean": round(float(np.mean(scores)), 2),
        "variance": round(float(np.var(scores)), 2)
    }


# -------------------------------
# 5. RUN ALL ANALYTICS
# -------------------------------
def run_all_analytics():
    return {
        "score_distribution": get_score_distribution(),
        "regression": detect_regression(),
        "component_performance": component_performance(),
        "stability": score_stability()
    }


# -------------------------------
# CLI ENTRY
# -------------------------------
if __name__ == "__main__":
    results = run_all_analytics()

    print("\n📊 SYSTEM ANALYTICS\n")

    print("Score Distribution:")
    print(results["score_distribution"], "\n")

    print("Regression Check:")
    print(results["regression"], "\n")

    print("Component Performance:")
    print(results["component_performance"], "\n")

    print("Score Stability:")
    print(results["stability"], "\n")