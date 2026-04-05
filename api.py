from fastapi import FastAPI, HTTPException
from graph import graph
from storage import get_blogs, get_blog, get_latest_blog, get_blog_by_slug
from metrics import get_metrics_summary
from scheduler import run_job
from database import init_db,get_connection
from fastapi.responses import HTMLResponse

app = FastAPI()


# =========================
# ✅ DB INIT (CORRECT WAY)
# =========================
@app.on_event("startup")
def startup():
    init_db()


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok"}
    except:
        return {"status": "db_error"}


# =========================
# GENERATE BLOG
# =========================

@app.post("/generate-blog")
def generate_blog():
    try:
        success = run_job()
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Blog generation failed"
            )

        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    
# =========================
# GET ALL BLOGS (SUMMARY)
# =========================
@app.get("/blogs")
def fetch_blogs():
    blogs = get_blogs()

    return [
        {
            "id": b["id"],
            "topic": b["topic"],
            "created_at": b["created_at"],
            "slug": b["slug"]   # ✅ FIXED
        }
        for b in blogs
    ]


# =========================
# GET SINGLE BLOG
# =========================


# @app.get("/blog/{blog_id}", response_class=HTMLResponse)
# def fetch_blog(blog_id: int):
#     blog = get_blog(blog_id)

#     if not blog:
#         raise HTTPException(status_code=404, detail="Blog not found")

#     return blog.get("html", "")


# =========================
# METRICS
# =========================
@app.get("/metrics")
def metrics():
    return get_metrics_summary()


# =========================
# LATEST BLOG
# =========================


@app.get("/latest-blog", response_class=HTMLResponse)
def latest_blog():
    blog = get_latest_blog()

    if not blog:
        return "<h1>No blogs available</h1>"

    return blog.get("html", "")


@app.get("/blog/{slug}")
def fetch_blog(slug: str):
    blog = get_blog_by_slug(slug)

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog