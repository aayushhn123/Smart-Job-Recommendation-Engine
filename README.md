⚡ HireMind — AI-Powered Job Recommendation Engine
<div align="center">
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
Upload your resume → get matched to live jobs → close skill gaps → get AI coaching.
🚀 Live Demo · 📖 Setup · 🔑 API Keys
</div>
---
✨ Features
Feature	Description
📄 Resume Parser	Extracts skills, contact info, education, experience from any PDF
🔍 Live Job Matching	Fetches real jobs from Himalayas API + JSearch (Google for Jobs)
📊 Match Scoring	DSA-powered scoring: skill overlap + title match + frequency analysis
📉 Skill Gap Analysis	Shows exactly which skills are missing across your top job matches
✍️ AI Cover Letters	Groq LLaMA 3.3 writes personalised cover letters per job
🎯 Interview Prep	AI generates role-specific interview questions + answering tips
🗺️ Learning Roadmap	30-60-90 day personalised plan to close skill gaps
💬 Career Coach Chat	Persistent chat with an AI career coach aware of your resume
📦 Export	Download resume data, job matches, full report, cover letters
---
🔑 API Keys
Required
Key	Where to get	Cost
GROQ_API_KEY	console.groq.com	Free (no credit card)
Optional
Key	Where to get	Cost
RAPIDAPI_KEY	rapidapi.com → JSearch	Free tier: 10 req/month
> The app works **without any API keys** using the Himalayas free job API.
> Add Groq to unlock AI features. Add RapidAPI for more job sources.
---
🚀 Deploy on Streamlit Cloud
1. Push to GitHub
```bash
git init
git add hiremind_app.py requirements.txt README.md .gitignore
git commit -m "🚀 Initial HireMind commit"
git remote add origin https://github.com/YOUR_USERNAME/hiremind.git
git push -u origin main
```
2. Deploy
Go to share.streamlit.io
Click New app → connect your repo
Set Main file path: `hiremind_app.py`
Click Advanced settings → paste your secrets:
```toml
GROQ_API_KEY = "gsk_your_key_here"
RAPIDAPI_KEY = "your_key_here"   # optional
```
Click Deploy!
---
💻 Run Locally
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
---
📁 File Structure
```
hiremind/
├── hiremind_app.py          ← Main application (single file)
├── requirements.txt         ← 4 dependencies
├── README.md                ← This file
├── .gitignore               ← Excludes secrets.toml
└── secrets.toml.template    ← Copy to .streamlit/secrets.toml
```
---
🏗️ Architecture
```
Resume PDF
    ↓
pdfplumber → raw text
    ↓
parse_resume() → structured dict
    │
    ├─→ Skills (200+ keyword matching, DSA: longest-match + word boundaries)
    ├─→ Contact (regex patterns)
    ├─→ Education (degree keyword search)
    ├─→ Experience (date range counting)
    └─→ Job Titles (keyword heuristics)
         ↓
Himalayas API + JSearch API → live job listings
    ↓
compute_match() → skill overlap score (0-100)
    │   ├─ Skill intersection score (0-70 pts)
    │   ├─ Title keyword score (0-20 pts)
    │   └─ Description frequency score (0-10 pts)
    ↓
rank_jobs() → sorted by score, deduplicated
    ↓
Groq LLaMA 3.3 → Cover letters · Interview prep · Roadmap · Chat
```
---
🗺️ Roadmap
[x] Resume PDF parsing (any format)
[x] 200+ skill extraction across 7 categories
[x] Live job fetching (Himalayas + JSearch)
[x] DSA-powered match scoring
[x] Skill gap analysis & visualisation
[x] AI cover letter generation (Groq)
[x] Interview prep questions (Groq)
[x] 30-60-90 day learning roadmap (Groq)
[x] Persistent career coach chat (Groq)
[x] Full data export (JSON + Markdown)
[ ] LinkedIn profile import
[ ] Salary benchmarking
[ ] Application tracker
[ ] Email job alerts
---
📄 License
MIT — free to use, modify, and deploy.
---
<div align="center">
Built with ⚡ Streamlit · Groq LLaMA 3.3 · Himalayas API · JSearch
</div>
