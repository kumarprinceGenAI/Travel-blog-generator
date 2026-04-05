import markdown
import logging

logger = logging.getLogger(__name__)


import re

import re
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_headings(html):
    return re.findall(r"<h[2-3][^>]*>(.*%s)</h[2-3]>", html)


def inject_images(html: str, images: list):
    if not images:
        return html

    headings = extract_headings(html)

    for img in images:
        title = img.get("title")
        url = img.get("url")

        if not title or not url:
            continue

        image_tag = f"""
        <img src="{url}" alt="{title}"
        style="width:100%;border-radius:10px;margin:15px 0;" />
        """

        # 🔍 STEP 1: Find best matching heading
        best_match = None
        best_score = 0

        for h in headings:
            score = similarity(title, h)
            if score > best_score:
                best_score = score
                best_match = h

        # 🎯 STEP 2: Threshold match
        if best_score > 0.6:
            pattern = rf"(<h[2-3][^>]*>\s*{re.escape(best_match)}\s*</h[2-3]>)"
            html = re.sub(pattern, r"\1" + image_tag, html, count=1)
            logger.info(f"[Renderer] ✅ Injected → {best_match} (score: {round(best_score,2)})")
        else:
            logger.warning(f"[Renderer] ❌ No good match → {title} (best: {round(best_score,2)})")

    return html


def render_html(blog_text: str, images: list = None):
    """
    Convert markdown → HTML and inject images
    """

    try:
        html = markdown.markdown(blog_text)

        if images:
            html = inject_images(html, images)

        logger.info("[Renderer] HTML rendering complete")
        return html

    except Exception as e:
        logger.error(f"[Renderer] Rendering failed: {str(e)}")
        return "<p>Rendering error</p>"