# 🚀 Autonomous AI Travel Blog Generator  
### Production-Grade Multi-Agent GenAI System

---

## 🌐 Live Demo
# API
👉 https://travel-blog-generator.onrender.com/docs
# UI
---

## 🧠 TL;DR

This is a **self-improving AI system** that:

- Discovers high-value topics  
- Generates long-form blogs  
- Critiques its own output  
- Improves weak content  
- Publishes SEO-optimized HTML  
- Runs automatically (4x/day)  

👉 No human in the loop.

---

## ⚡ Why This Project Exists

Most “GenAI apps” are:

- Prompt → Output → Done ❌  

This system is different:

Think → Plan → Write → Critique → Improve → Publish

It mimics **real editorial workflows** — not toy demos.

---

## 🏗️ System Architecture

GitHub Actions (Scheduler)
            ↓
     FastAPI Backend
            ↓
     LangGraph Orchestration
            ↓
   Multi-Agent Execution Engine
            ↓
 PostgreSQL (Supabase Storage)

---

## 🔄 Core Engine: LangGraph Workflow

        ┌──────────────┐
        │  Researcher  │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │   Planner    │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │    Writer    │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │   Reviewer   │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Improver (↺) │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │  SEO Agent   │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Image Engine │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ HTML Renderer│
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │   Storage    │
        └──────────────┘

---

## 🧠 Key Design Decisions

### 1. Multi-Agent Architecture
- Separation of responsibilities  
- Easier debugging and scaling  

### 2. Self-Evaluation Loop

If score < threshold → improve → re-evaluate

- Prevents low-quality output  
- Mimics real editorial workflows  

### 3. Anti-Generic Enforcement
- Penalizes generic tone  
- Forces opinions + insights  

### 4. Structured Scoring System
Evaluates:
- Content quality  
- SEO  
- Readability  
- Uniqueness  

### 5. PostgreSQL Storage
- Uses JSONB for structured data  
- Stores blogs, HTML, images, SEO, metrics  

### 6. Automated Scheduling
- GitHub Actions cron (4x/day)  
- Retry + timeout + concurrency control  

---

## ⚙️ Tech Stack

| Layer | Technology |
|------|------------|
| Backend | FastAPI |
| Orchestration | LangGraph |
| LLM | Google Gemini |
| Database | PostgreSQL (Supabase) |
| Scheduler | GitHub Actions |
| Deployment | Render |

---

## 🔐 Security

Protected endpoint:

POST /generate-blog

Uses:

x-api-key: CRON_SECRET

---

## 📊 Observability

Tracks:
- Scores (content, SEO, etc.)
- Iterations
- Improvement delta
- Execution time
- Errors

---

## ⚠️ Limitations

- LLM JSON output can break → repair layer used  
- Image matching is heuristic  
- No alerting system yet  
- No queue system  

---

## 🔮 Roadmap

### Short Term
- Failure alerts  
- Better deduplication  

### Mid Term
- Queue system (Celery/Redis)  
- Observability dashboard  

### Long Term
- Multi-domain content  
- Reinforcement learning loop  

---

## 📡 API

### Health
GET /

### Generate Blog
POST /generate-blog
Header: x-api-key

### Blogs
GET /blogs

### Latest Blog
GET /latest-blog

---

## ⚡ Setup

### Clone

git clone <repo>
cd project

### Install

pip install -r requirements.txt

### Environment

DATABASE_URL=postgres_url
GOOGLE_API_KEY=your_key
CRON_SECRET=your_secret

### Run

uvicorn api:app --reload

---

## 🧪 Execution Flow

1. Scheduler triggers API  
2. Researcher finds topics  
3. Planner structures blog  
4. Writer generates content  
5. Reviewer scores  
6. Improver refines (if needed)  
7. SEO + Images added  
8. HTML rendered  
9. Stored in DB  

---

## 👨‍💻 What This Demonstrates

- Multi-agent orchestration  
- Real-world GenAI system design  
- LLM reliability engineering  
- Backend + AI integration  
- Production thinking  

---

## ⭐ Final Thought

Most people build AI demos.

This is a **system**.

It doesn’t just generate content —  
it **thinks, evaluates, and improves itself**.
