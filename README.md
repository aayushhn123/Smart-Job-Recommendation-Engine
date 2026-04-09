# ⚡ HireMind — AI-Powered Job Recommendation Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F55036?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" />
  <img src="https://img.shields.io/badge/Status-Production-22C55E?style=flat-square" />
</p>

<p align="center">
  <strong>Upload any PDF resume → auto-detect your domain → fetch live jobs → score every match → close skill gaps → get AI coaching.</strong>
</p>

<p align="center">
  <a href="https://smart-job-recommendation-engine.streamlit.app/">🚀 Live Demo</a> &nbsp;·&nbsp;
  <a href="#-setup">⚙️ Setup</a> &nbsp;·&nbsp;
  <a href="#-api-keys">🔑 API Keys</a> &nbsp;·&nbsp;
  <a href="#-architecture">🏗️ Architecture</a>
</p>

---

## ✨ What HireMind Does

HireMind is a **DSA-powered** (no heavy ML) job recommendation engine built entirely with Streamlit. It parses your resume, understands your domain, fetches live job listings, scores each one against your profile, and uses Groq's free LLaMA 3.3 model to generate cover letters, interview prep, and personalised learning roadmaps.

---

## 🗂️ Feature Overview

### 👤 Tab 1 — Resume Profile
- Parses **any PDF layout** — single column, multi-column, tables, graphics-heavy
- Extracts contact info (name, email, phone, LinkedIn, GitHub, website) using regex pattern matching
- Detects skills across **7 categories and 200+ keywords** using longest-match regex with word boundary anchors
- Identifies education, degrees, institutions, CGPA from any formatting
- Detects job titles using role-keyword heuristics
- Extracts professional summary via section-header detection with fallback to long-sentence heuristic
- **Smart experience detection** — distinguishes work experience dates from education dates; correctly labels students/freshers as `Fresher` instead of miscounting degree years as work experience
- **Resume Completeness Score** (0–100) across 6 dimensions with per-section breakdown
- **ATS Keyword Counter** — counts action verbs (built, led, improved, deployed...) and flags weak resume language
- Quick-win improvement tips auto-generated from completeness analysis

### 🔍 Tab 2 — Live Job Matches
- **Auto-detects your domain** from 9 domain signal clusters (ML Engineer, Data Scientist, Data Analyst, Data Engineer, AI/LLM Engineer, DevOps, Frontend, Backend, Computer Vision)
- Builds a **smart search query** — e.g. a Data Science resume auto-generates `"Data Scientist machine learning deep learning"` not a vague title
- Fetches live jobs from two sources simultaneously:
  - **Himalayas API** — free, no authentication needed, remote-first jobs globally
  - **JSearch / Google for Jobs** via RapidAPI — optional, pulls from LinkedIn, Indeed, Glassdoor (free tier: 10 req/month)
- Results cached for 1 hour to avoid unnecessary API calls
- **Relevance filter** — hard-rejects off-domain jobs (customer service, retail, driver...) before scoring; accepts any job with skill overlap or tech-sounding title
- **DSA Match Scoring** (0–100) with transparent breakdown:
  - Skill overlap score (0–70 pts) — set intersection of resume skills vs JD skills
  - Title keyword score (0–20 pts) — your skills appearing in the job title
  - Description frequency score (0–10 pts) — matched skill frequency in JD text
- Score breakdown shown per card: `Skill: Xpt  Title: Ypt  Freq: Zpt`
- Jobs sorted by score; 🟢 strong (≥60%) / 🟡 partial (30–59%) / 🔴 low (<30%) visual grouping
- Per-job: matched skills, missing skills, salary, employment type, posting date, source, apply link
- **AI Cover Letter** — one-click, personalised per job, downloadable `.txt`
- **AI Interview Prep** — 8 role-specific questions (technical, behavioural STAR, situational, skill-gap) with answering tips

### 📊 Tab 3 — Skill Gap Analysis
- Aggregates missing and matched skills across your top 10 matched jobs
- **Missing skills** ranked by urgency (how many jobs require them) with 🔴/🟡/⚪ urgency indicators
- **Strongest assets** — your skills that appear most across job descriptions
- **Category coverage bars** — how well each skill category is covered across top matches
- **AI 30-60-90 Day Learning Roadmap** — names exact free resources, estimated hours per skill, and a portfolio project idea for each gap skill

### 🤖 Tab 4 — AI Career Coach
- **Resume Review** — 5 specific, brutally honest improvement tips citing why each matters for ATS and recruiters
- **Persistent career coach chat** — context-aware of your resume (domain, skills, experience level); ask anything about salary negotiation, career transitions, interview strategies
- All AI features powered by **Groq LLaMA 3.3 70B** — free tier, no credit card required

### 📦 Tab 5 — Export
- **Resume JSON** — full parsed data including completeness scores and ATS keyword count
- **Job Matches JSON** — ranked list with score breakdowns, matched/missing skills, apply URLs
- **Full Markdown Report** — resume summary + skills + improvement tips + top 5 job matches
- **Raw extracted text** — full text pulled from the PDF for debugging

---

## 🔑 API Keys

| Key | Required | Where to Get | Cost |
|-----|----------|-------------|------|
| `GROQ_API_KEY` | **Recommended** | [console.groq.com](https://console.groq.com) | Free (no credit card) |
| `RAPIDAPI_KEY` | Optional | [RapidAPI → JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) | Free tier: 10 req/month |

> **The app works without any API keys** — Himalayas API is completely free and requires no authentication. Add a Groq key to unlock cover letters, interview prep, roadmaps, and the career coach chat.

---

## 🚀 Setup

### Option A — Streamlit Community Cloud (Recommended)

**1. Fork or push to GitHub**
```bash
git init
git add hiremind_app.py requirements.txt README.md .gitignore
git commit -m "feat: initial HireMind deploy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hiremind.git
git push -u origin main
```

**2. Deploy on Streamlit Cloud**
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **New app** → connect your GitHub repo
3. Set **Main file path** → `hiremind_app.py`
4. Click **Advanced settings** → paste into the Secrets field:
```toml
GROQ_API_KEY = "gsk_your_key_here"
RAPIDAPI_KEY = "your_key_here"   # optional
```
5. Click **Deploy** — live in ~60 seconds

### Option B — Run Locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/hiremind.git
cd hiremind

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up secrets
mkdir -p .streamlit
cp secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your actual keys

# 4. Run
streamlit run hiremind_app.py
```

App opens at `http://localhost:8501`

---

## 📦 Dependencies

```
streamlit>=1.32.0
pdfplumber>=0.10.3
groq>=0.9.0
requests>=2.31.0
```

Only 4 dependencies — everything else (`re`, `json`, `collections`) is Python stdlib.

---

## 📁 File Structure

```
hiremind/
├── hiremind_app.py          ← Entire application (single file, ~1120 lines)
├── requirements.txt         ← 4 dependencies
├── README.md                ← This file
├── .gitignore               ← Excludes .streamlit/secrets.toml
└── secrets.toml.template    ← Copy to .streamlit/secrets.toml locally
```

---

## 🏗️ Architecture

```
PDF Upload / Paste Text
         │
         ▼
 extract_text_from_pdf()
   pdfplumber — text + table extraction
   x_tolerance=3, y_tolerance=3 for robust parsing
         │
         ▼
     parse_resume()
   ├─ extract_contact_info()    — regex pattern matching (email, phone, LinkedIn, GitHub)
   ├─ extract_skills()          — longest-match regex, word boundaries, 200+ keywords
   ├─ extract_education()       — degree keywords + institution name patterns
   ├─ extract_years_experience()— explicit mention → work-context date ranges → Fresher fallback
   ├─ extract_job_titles()      — role-keyword heuristics on short lines
   └─ extract_summary()         — section header detection + long-sentence fallback
         │
         ▼
 compute_resume_completeness()
   6 dimensions → 0-100 score + tips + ATS keyword count
         │
         ▼
  detect_domain() — 9 skill-cluster signals → canonical job title
  build_smart_query() — title + top priority skills → focused search string
         │
         ▼
   Live Job APIs (cached 1hr)
   ├─ fetch_jobs_himalayas()  — free, no auth
   └─ fetch_jobs_jsearch()    — RapidAPI optional
         │
         ▼
     rank_jobs()
   ├─ is_relevant_job()  — off-domain filter + tech title check
   └─ compute_match()    — skill overlap (70pt) + title (20pt) + freq (10pt)
         │
         ▼
   Groq LLaMA 3.3 70B (optional)
   ├─ ai_cover_letter()      — per-job, personalised
   ├─ ai_interview_prep()    — 8 questions with answering tips
   ├─ ai_skill_roadmap()     — 30-60-90 day plan with named resources
   ├─ ai_resume_tips()       — 5 specific ATS-aware improvements
   └─ career coach chat      — context-aware persistent chat
```

---

## 🧠 How the Scoring Works

Every job gets a score out of 100 built from three components:

| Component | Max Points | How it's Calculated |
|-----------|-----------|---------------------|
| **Skill Overlap** | 70 | `len(your_skills ∩ job_skills) / len(job_skills) × 70` |
| **Title Match** | 20 | +5 per resume skill that appears in the job title (capped at 20) |
| **Frequency Bonus** | 10 | Average times matched skills appear in the job description (capped at 10) |

The score breakdown is shown on every job card so you know exactly why a job ranked where it did.

---

## 🐛 Known Fixes Applied

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| Experience showing `~6 yrs` for students | Date-range fallback was counting education dates (e.g. `2021-2024` Diploma) as work experience | 3-layer filter: inline EDU keyword check → context window check → Fresher fallback |
| Off-domain jobs (customer service, retail) appearing | Query was built from vague resume text; no relevance filter | `detect_domain()` identifies skill cluster → focused query; `is_relevant_job()` hard-rejects non-tech titles |
| `global flags not at the start` crash on Python 3.13 | Inline `(?i)` flags inside joined regex patterns | Removed all inline flags; pass `re.IGNORECASE` as argument to every `re.search()` call |
| `fetch_jobs_himalayas` silently not running | Function body was accidentally placed after a `return False` statement during an edit | Full clean rewrite separating all functions properly |

---

## 🗺️ Roadmap

| Status | Feature |
|--------|---------|
| ✅ Done | Resume PDF parsing (any format) |
| ✅ Done | 200+ skill extraction across 7 categories |
| ✅ Done | Student/fresher experience detection |
| ✅ Done | Resume completeness scoring (0-100) |
| ✅ Done | ATS keyword analysis |
| ✅ Done | Domain auto-detection (9 domains) |
| ✅ Done | Live job fetching (Himalayas + JSearch) |
| ✅ Done | DSA match scoring with transparency |
| ✅ Done | Off-domain job filtering |
| ✅ Done | Skill gap analysis with urgency indicators |
| ✅ Done | AI cover letter generation (Groq) |
| ✅ Done | AI interview prep (Groq) |
| ✅ Done | 30-60-90 day learning roadmap (Groq) |
| ✅ Done | Career coach chat (Groq) |
| ✅ Done | Full data export (JSON + Markdown) |
| 🔜 Planned | LinkedIn profile URL import |
| 🔜 Planned | Salary benchmarking by role + location |
| 🔜 Planned | Job application tracker |
| 🔜 Planned | Email job alerts |
| 🔜 Planned | Resume version comparison |

---

## ⚙️ Configuration Reference

All settings live in the sidebar at runtime. For Streamlit Cloud deployment, set them as secrets.

| Setting | Where | Description |
|---------|-------|-------------|
| `GROQ_API_KEY` | Secrets / Sidebar | Groq API key for all AI features |
| `RAPIDAPI_KEY` | Secrets / Sidebar | RapidAPI key for JSearch (optional) |
| Override Target Role | Sidebar | Overrides auto-detected domain for job search |
| Location | Sidebar | Preferred job location (default: Remote) |
| Max jobs to display | Sidebar slider | 5–25 jobs shown (default: 10) |

---

## 📄 License

MIT — free to use, modify, and deploy.

---

<p align="center">
  Built with ⚡ <strong>Streamlit</strong> &nbsp;·&nbsp; 🤖 <strong>Groq LLaMA 3.3 70B</strong> &nbsp;·&nbsp; 🌐 <strong>Himalayas API</strong> &nbsp;·&nbsp; 🔍 <strong>JSearch / Google for Jobs</strong>
</p>
