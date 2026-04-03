from fastapi import FastAPI, HTTPException
from graph import graph
from storage import get_blogs, get_blog
from metrics import get_metrics_summary

app = FastAPI()


#  Health check
@app.get("/")
def home():
    return {"message": "Travel Blog Generator API is running"}


#  Manual blog generation (keep this)
@app.post("/generate-blog")
def generate_blog():
    result = graph.invoke({})

    return {
        "topic": result.get("topic"),
        "blog": result.get("blog"),
        "html": result.get("html"),
        "seo": result.get("seo")
    }


#  NEW: Get all blogs (summary)
@app.get("/blogs")
def fetch_blogs():
    blogs = get_blogs()

    return [
        {
            "id": b["id"],
            "topic": b["topic"],
            "created_at": b["created_at"]
        }
        for b in blogs
    ]


# NEW: Get single blog (full content)
@app.get("/blog/{blog_id}")
def fetch_blog(blog_id: int):
    blog = get_blog(blog_id)

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog

@app.get("/metrics")
def metrics():
    return get_metrics_summary()

@app.get("/latest-blog")
def latest_blog():
    from storage import get_latest_blog
    return get_latest_blog()