import markdown

def render_html(blog_text: str):
    html = markdown.markdown(blog_text)
    return html