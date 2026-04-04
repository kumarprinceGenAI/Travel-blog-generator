import sqlite3
import pickle

from embedding import get_embedding, cosine_similarity

DB_NAME = "blogs.db"

SIM_THRESHOLD = 0.85


# ✅ EXISTING (unchanged)
def is_duplicate(topic: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM blogs WHERE LOWER(topic) = LOWER(?) LIMIT 1",
        (topic,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None


# 🔥 NEW — SEMANTIC DUPLICATE
def is_semantic_duplicate(topic: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    new_emb = get_embedding(topic)

    if new_emb is None:
        print("[Semantic Dedup] Skipping due to embedding failure")
        return False

    cursor.execute("SELECT embedding FROM topic_embeddings")
    rows = cursor.fetchall()

    for (emb_blob,) in rows:
        try:
            existing_emb = pickle.loads(emb_blob)
            sim = cosine_similarity(new_emb, existing_emb)

            if sim > SIM_THRESHOLD:
                print(f"[Semantic Dedup] Duplicate detected | Similarity: {sim:.2f}")
                conn.close()
                return True
        except:
            continue

    conn.close()
    return False


def save_topic(topic: str):
    # no-op (already saved via save_blog)
    return