def validate_content_quality(blog: str):
    errors = []

    blog_lower = blog.lower()

    if "₹" not in blog:
        errors.append("Missing INR currency reference (₹)")

    if "insider tips" not in blog_lower:
        errors.append("Missing 'Insider Tips' section")

    if "mistakes to avoid" not in blog_lower:
        errors.append("Missing 'Mistakes to Avoid' section")

    if "budget" not in blog_lower:
        errors.append("Missing budget section")

    if len(blog.split()) < 1000:
        errors.append("Blog too short (min 1000 words)")

    return errors   # 🔥 NO raise