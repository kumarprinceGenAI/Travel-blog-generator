from google import genai
import os
from dotenv import load_dotenv
import numpy as np
import logging

load_dotenv()
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# 🔥 USE ONLY GOOGLE EMBEDDING
def get_embedding(text: str):
    try:
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text
        )

        return np.array(response.embeddings[0].values)

    except Exception as e:
        logger.error(f"[Embedding] Failed: {str(e)}")
        return None  # safe fallback handled upstream


def cosine_similarity(a, b):
    try:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    except Exception:
        return 0