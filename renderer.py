import markdown
import logging

logger = logging.getLogger(__name__)


import re

import re
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_headings(html):
    return re.findall(r"(<h[2-3][^>]*>.*?</h[2-3]>)", html, re.DOTALL)


def inject_images(html: str, images: list):
    if not images:
        return html

    headings = extract_headings(html)

    logger.info(f"[Renderer] Headings found: {len(headings)}")
    logger.info(f"[Renderer] Images received: {len(images)}")

    for i, heading in enumerate(headings):
        if i >= len(images):
            break

        img = images[i]

        if not isinstance(img, dict):
            logger.warning(f"[Renderer] Invalid image format at index {i}")
            continue

        url = img.get("url")
        title = img.get("title", "travel image")

        if not url:
            logger.warning(f"[Renderer] Missing URL at index {i}")
            continue

        clean_title = re.sub(r"^#+\s*", "", title)

        image_tag = f"""
        <div class="blog-image">
            <img src="{url}" alt="{clean_title}"
            style="width:100%;border-radius:10px;margin:15px 0;" loading="lazy"/>
        </div>
        """

        idx = html.find(heading)
        if idx != -1:
            insert_pos = idx + len(heading)
            html = html[:insert_pos] + image_tag + html[insert_pos:]
            logger.info(f"[Renderer] ✅ Injected image {i+1}")

    if "<img" not in html:
        logger.warning("[Renderer] ⚠️ No images injected — fallback triggered")

        for img in images[:3]:
            if isinstance(img, dict) and img.get("url"):
                html += f"""
                <div class="blog-image">
                    <img src="{img.get("url")}" alt="fallback"
                    style="width:100%;border-radius:10px;margin:15px 0;" loading="lazy"/>
                </div>
                """

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