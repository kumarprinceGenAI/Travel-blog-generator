from google import genai
import os
from dotenv import load_dotenv
import numpy as np
import logging
import time

load_dotenv()
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def get_embedding(text: str, retries=3, delay=1):
    if not text:
        return None

    for attempt in range(retries):
        try:
            response = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text
            )

            # 🔒 SAFE CHECK
            if not response or not response.embeddings:
                logger.error("[Embedding] Empty response")
                return None

            values = response.embeddings[0].values

            if not values:
                logger.error("[Embedding] No values in response")
                return None

            vec = np.array(values)

            # 🔥 Normalize (important for cosine)
            norm = np.linalg.norm(vec)
            if norm == 0:
                return None

            return vec / norm

        except Exception as e:
            logger.warning(f"[Embedding Retry {attempt+1}] {str(e)}")
            time.sleep(delay)

    logger.error("[Embedding] Failed after retries")
    return None


def cosine_similarity(a, b):
    try:
        if a is None or b is None:
            return 0

        return float(np.dot(a, b))  # already normalized
    except Exception:
        return 0