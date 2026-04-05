import sqlite3
import pickle
from database import get_connection
from embedding import get_embedding, cosine_similarity




def get_related_topics(current_topic, top_k=3):
    conn = get_connection()
    cursor = conn.cursor()

    current_emb = get_embedding(current_topic)

    if current_emb is None:
        print("[Linking] ❌ No embedding for current topic")
        return []

    cursor.execute("SELECT topic, embedding FROM topic_embeddings")
    rows = cursor.fetchall()

    scored = []

    for topic, emb_blob in rows:
        if topic == current_topic:
            continue

        try:
            emb = pickle.loads(emb_blob)
            sim = cosine_similarity(current_emb, emb)

            scored.append((topic, sim))
        except:
            continue

    conn.close()

    scored.sort(key=lambda x: x[1], reverse=True)

    top_topics = [t[0] for t in scored[:top_k]]

    print(f"[Linking] 🔎 Found {len(scored)} candidates")
    print(f"[Linking] ✅ Selected top {len(top_topics)} topics:")
    for t, s in scored[:top_k]:
        print(f"   → {t} (similarity: {round(s, 2)})")

    return top_topics


def inject_internal_links(blog_text, related_topics):
    if not related_topics:
        print("[Linking] ⚠️ No related topics → skipping injection")
        return blog_text

    print(f"[Linking] 🔗 Injecting {len(related_topics)} internal links")

    links_section = "\n\n---\n\n### Related Guides\n"

    for topic in related_topics:
        print(f"[Linking] ➕ Adding link → {topic}")
        links_section += f"- {topic}\n"

    return blog_text + links_section