import streamlit as st
import pdfplumber
import re
import json
import requests
import time
from collections import defaultdict

st.set_page_config(
    page_title="HireMind",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════
# SKILL DATABASE
# ══════════════════════════════════════════════════════════════════════
SKILL_DB = {
    "💻 Languages": [
        "python","java","javascript","typescript","c++","c#","c","go","golang",
        "rust","swift","kotlin","ruby","php","scala","r","matlab","perl",
        "bash","shell","powershell","dart","haskell","lua","julia","elixir",
        "clojure","groovy","vba","cobol","fortran",
    ],
    "🌐 Frameworks": [
        "react","angular","vue","next.js","nuxt.js","svelte","django","flask",
        "fastapi","spring","spring boot","express","node.js","rails","laravel",
        "asp.net",".net","blazor","gatsby","remix","nestjs","koa","tornado","bottle",
    ],
    "🧠 AI / ML": [
        "machine learning","deep learning","neural networks","nlp","computer vision",
        "tensorflow","pytorch","keras","scikit-learn","sklearn","xgboost","lightgbm",
        "catboost","pandas","numpy","scipy","matplotlib","seaborn","plotly",
        "hugging face","transformers","langchain","openai","llm","generative ai",
        "reinforcement learning","cnn","rnn","lstm","bert","gpt","stable diffusion",
        "mlops","feature engineering",
    ],
    "🗄️ Databases": [
        "sql","mysql","postgresql","postgres","sqlite","oracle","mssql","mongodb",
        "redis","elasticsearch","cassandra","dynamodb","neo4j","firebase","supabase",
        "snowflake","bigquery","redshift","pinecone","chroma","weaviate","nosql",
    ],
    "☁️ Cloud & DevOps": [
        "aws","azure","gcp","google cloud","docker","kubernetes","k8s","terraform",
        "ansible","jenkins","github actions","gitlab ci","circleci","helm",
        "prometheus","grafana","nginx","apache","linux","ubuntu","devops","ci/cd",
        "microservices","serverless","lambda","ec2","s3",
    ],
    "🔧 Tools": [
        "git","github","gitlab","bitbucket","jira","confluence","notion","figma",
        "postman","swagger","graphql","rest api","grpc","kafka","rabbitmq","celery",
        "airflow","spark","hadoop","dbt","tableau","power bi","looker","excel",
        "jupyter","vscode","streamlit","gradio","vercel","netlify","heroku",
    ],
    "🤝 Soft Skills": [
        "leadership","communication","teamwork","problem solving","critical thinking",
        "project management","agile","scrum","kanban","collaboration","mentoring",
        "time management","analytical","research","presentation","negotiation",
        "stakeholder management","strategic thinking","decision making",
    ],
}

FLAT_SKILLS = {skill.lower(): cat for cat, skills in SKILL_DB.items() for skill in skills}

SECTION_PATTERNS = {
    "experience":     r"(work\s+experience|professional\s+experience|employment|experience|career\s+history|work\s+history)",
    "education":      r"(education|academic|qualification|degree|university|college|school)",
    "skills":         r"(skills|technical\s+skills|core\s+competencies|technologies|expertise|proficiencies)",
    "projects":       r"(projects|personal\s+projects|key\s+projects|notable\s+projects|portfolio)",
    "certifications": r"(certification|certificates|licenses|credentials|awards)",
    "summary":        r"(summary|profile|objective|about\s+me|overview|executive\s+summary|professional\s+summary)",
}

CONTACT_PATTERNS = {
    "email":    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
    "phone":    r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}",
    "linkedin": r"(?:linkedin\.com/in/|linkedin:\s*)([A-Za-z0-9\-_/]+)",
    "github":   r"(?:github\.com/|github:\s*)([A-Za-z0-9\-_]+)",
    "website":  r"https?://(?!linkedin|github)[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+",
}

# ══════════════════════════════════════════════════════════════════════
# RESUME PARSING ENGINE
# ══════════════════════════════════════════════════════════════════════
def extract_text_from_pdf(pdf_file) -> str:
    parts = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                t = page.extract_text(x_tolerance=3, y_tolerance=3)
                if t:
                    parts.append(t)
                for table in page.extract_tables():
                    for row in table:
                        if row:
                            parts.append(" | ".join(str(c) for c in row if c))
    except Exception:
        pass
    return "\n".join(parts)

def extract_contact_info(text: str) -> dict:
    contact = {}
    for key, pattern in CONTACT_PATTERNS.items():
        m = re.findall(pattern, text)
        if m:
            contact[key] = m[0] if isinstance(m[0], str) else m[0]
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            contact["name"] = line
            break
    return contact

def extract_skills(text: str) -> dict:
    text_lower = text.lower()
    found = defaultdict(list)
    matched = set()
    for skill in sorted(FLAT_SKILLS.keys(), key=len, reverse=True):
        if skill in matched:
            continue
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found[FLAT_SKILLS[skill]].append(skill)
            matched.add(skill)
    return dict(found)

def extract_education(text: str) -> list:
    edu = []
    for m in re.findall(
        r"(B\.?Tech|B\.?E\.?|Bachelor|B\.?Sc?|B\.?A\.?|M\.?Tech|M\.?E\.?|Master|M\.?Sc?|M\.?A\.?|PhD|Ph\.D|MBA|BBA|Diploma|Associate)[^\n]{0,80}",
        text, re.IGNORECASE
    ):
        if len(m) > 5:
            edu.append(m.strip())
    for m in re.findall(r"(?:University|College|Institute|School|Academy)\s+of\s+[A-Z][A-Za-z\s,]+", text):
        edu.append(m.strip())
    return list(dict.fromkeys(edu))[:5]

def extract_years_experience(text: str) -> str:
    for p in [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+)\+?\s*years?",
        r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1) + "+ yrs"
    dates = re.findall(r"(20\d{2}|19\d{2})\s*[-\u2013\u2014]\s*(20\d{2}|Present|Current|Now)", text, re.IGNORECASE)
    if dates:
        years = set()
        for s, e in dates:
            try:
                start = int(s)
                end = 2025 if e.isalpha() else int(e)
                years.update(range(start, end + 1))
            except Exception:
                pass
        if years:
            t = max(years) - min(years)
            if t > 0:
                return f"~{t} yrs"
    return "N/A"

def extract_job_titles(text: str) -> list:
    keywords = [
        "engineer","developer","designer","manager","analyst","architect",
        "scientist","consultant","lead","director","specialist","intern",
        "researcher","administrator","coordinator","head of","vp of",
        "chief","officer","associate","senior","junior","principal",
    ]
    titles = []
    for line in text.split("\n"):
        line = line.strip()
        if 3 < len(line) < 60:
            lower = line.lower()
            if any(kw in lower for kw in keywords) and not re.search(r"\d{4}", line):
                titles.append(line)
    return list(dict.fromkeys(titles))[:5]

def _is_section_header(line: str) -> bool:
    for pattern in SECTION_PATTERNS.values():
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False

def extract_summary(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if re.search(SECTION_PATTERNS["summary"], line, re.IGNORECASE):
            chunk = []
            for j in range(i + 1, min(i + 8, len(lines))):
                if _is_section_header(lines[j]):
                    break
                chunk.append(lines[j])
            if chunk:
                return " ".join(chunk)[:500]
    for line in lines[:20]:
        if len(line) > 80 and not re.search(r"[@|\d{4}]", line[:10]):
            return line[:400]
    return ""

def parse_resume(text: str) -> dict:
    skills = extract_skills(text)
    return {
        "contact":          extract_contact_info(text),
        "skills":           skills,
        "education":        extract_education(text),
        "years_experience": extract_years_experience(text),
        "job_titles":       extract_job_titles(text),
        "summary":          extract_summary(text),
        "total_skills":     sum(len(v) for v in skills.values()),
        "word_count":       len(text.split()),
        "char_count":       len(text),
        "all_skills_flat":  [s for skills_list in skills.values() for s in skills_list],
    }

# ══════════════════════════════════════════════════════════════════════
# JOB FETCHING ENGINE
# ══════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_jobs_himalayas(query: str, limit: int = 20) -> list:
    """Fetch jobs from Himalayas API (100% free, no auth)."""
    try:
        url = "https://himalayas.app/jobs/api"
        params = {"q": query, "limit": limit}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            jobs = data.get("jobs", [])
            result = []
            for j in jobs:
                result.append({
                    "title":       j.get("title", ""),
                    "company":     j.get("companyName", ""),
                    "location":    j.get("locationRestrictions", ["Remote"])[0] if j.get("locationRestrictions") else "Remote",
                    "description": j.get("description", "")[:2000],
                    "url":         j.get("applyUrl") or j.get("url", ""),
                    "type":        j.get("employmentType", "Full Time"),
                    "posted":      j.get("createdAt", "")[:10],
                    "source":      "Himalayas",
                    "salary":      "",
                    "skills_required": extract_skills_from_jd(j.get("description", "")),
                })
            return result
    except Exception:
        pass
    return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_jobs_jsearch(query: str, location: str, rapidapi_key: str) -> list:
    """Fetch jobs from JSearch API via RapidAPI (free tier: 10 req/month)."""
    if not rapidapi_key:
        return []
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        params = {
            "query": f"{query} in {location}" if location else query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "month",
        }
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }
        r = requests.get(url, headers=headers, params=params, timeout=12)
        if r.status_code == 200:
            data = r.json()
            jobs = data.get("data", [])
            result = []
            for j in jobs:
                desc = j.get("job_description", "")[:2000]
                result.append({
                    "title":           j.get("job_title", ""),
                    "company":         j.get("employer_name", ""),
                    "location":        j.get("job_city", "") or j.get("job_country", ""),
                    "description":     desc,
                    "url":             j.get("job_apply_link", ""),
                    "type":            j.get("job_employment_type", "FULLTIME"),
                    "posted":          j.get("job_posted_at_datetime_utc", "")[:10],
                    "source":          "JSearch / Google Jobs",
                    "salary":          _format_salary(j),
                    "skills_required": extract_skills_from_jd(desc),
                })
            return result
    except Exception:
        pass
    return []

def _format_salary(j: dict) -> str:
    mn = j.get("job_min_salary")
    mx = j.get("job_max_salary")
    cur = j.get("job_salary_currency", "USD")
    period = j.get("job_salary_period", "")
    if mn and mx:
        return f"{cur} {int(mn):,} – {int(mx):,} / {period}"
    if mn:
        return f"{cur} {int(mn):,}+ / {period}"
    return ""

def extract_skills_from_jd(text: str) -> list:
    """Extract skills from a job description."""
    text_lower = text.lower()
    found = []
    matched = set()
    for skill in sorted(FLAT_SKILLS.keys(), key=len, reverse=True):
        if skill in matched:
            continue
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found.append(skill)
            matched.add(skill)
    return found[:25]

# ══════════════════════════════════════════════════════════════════════
# MATCHING ENGINE  (DSA — set intersection + scoring)
# ══════════════════════════════════════════════════════════════════════

def compute_match(resume_skills: list, job: dict) -> dict:
    """
    Score = weighted combination of:
      - skill overlap ratio
      - title keyword match
      - experience level match
    """
    resume_set = set(s.lower() for s in resume_skills)
    job_set    = set(s.lower() for s in job.get("skills_required", []))

    matched_skills  = resume_set & job_set
    missing_skills  = job_set - resume_set
    extra_skills    = resume_set - job_set   # bonus skills candidate has

    # Skill score (0-70 pts)
    if job_set:
        skill_score = round(len(matched_skills) / len(job_set) * 70)
    else:
        skill_score = 35  # no JD skills parsed → neutral

    # Title keyword score (0-20 pts)
    title_score = 0
    job_title_lower = job.get("title", "").lower()
    for skill in resume_skills:
        if skill.lower() in job_title_lower:
            title_score = min(title_score + 5, 20)

    # Description keyword frequency bonus (0-10 pts)
    desc_lower = job.get("description", "").lower()
    freq_bonus = 0
    for skill in matched_skills:
        freq_bonus += desc_lower.count(skill)
    freq_score = min(round(freq_bonus / max(len(matched_skills), 1)), 10)

    total = min(skill_score + title_score + freq_score, 100)

    return {
        "score":          total,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "extra_skills":   sorted(list(extra_skills)[:10]),
        "match_pct":      total,
    }

def rank_jobs(resume_data: dict, jobs: list) -> list:
    """Rank jobs by match score, deduplicate by title+company."""
    resume_skills = resume_data.get("all_skills_flat", [])
    seen = set()
    ranked = []
    for job in jobs:
        key = (job["title"].lower().strip(), job["company"].lower().strip())
        if key in seen:
            continue
        seen.add(key)
        match = compute_match(resume_skills, job)
        ranked.append({**job, **match})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked

# ══════════════════════════════════════════════════════════════════════
# GROQ AI ENGINE
# ══════════════════════════════════════════════════════════════════════

def get_groq_client(api_key: str):
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception:
        return None

def groq_call(client, system: str, user: str, max_tokens: int = 1024) -> str:
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Groq API error: {e}"

def ai_resume_tips(client, resume_data: dict) -> str:
    skills_str = ", ".join(resume_data.get("all_skills_flat", [])[:20])
    titles_str = ", ".join(resume_data.get("job_titles", []))
    exp        = resume_data.get("years_experience", "N/A")
    system = (
        "You are an expert career coach and resume reviewer. "
        "Give practical, specific, actionable advice. Be concise and direct."
    )
    user = f"""Analyze this resume profile and give 5 specific improvement tips:

Experience: {exp}
Current/Past Roles: {titles_str}
Skills: {skills_str}
Education: {", ".join(resume_data.get("education", [])[:2])}

Focus on: resume formatting, skills to add, ATS optimisation, and career positioning.
Format as a numbered list."""
    return groq_call(client, system, user, max_tokens=600)

def ai_cover_letter(client, resume_data: dict, job: dict) -> str:
    name       = resume_data.get("contact", {}).get("name", "the applicant")
    skills_str = ", ".join(resume_data.get("all_skills_flat", [])[:15])
    matched    = ", ".join(job.get("matched_skills", [])[:10])
    system     = "You are an expert cover letter writer. Write professional, engaging, specific cover letters."
    user = f"""Write a concise, compelling cover letter for:

Candidate: {name}
Candidate Skills: {skills_str}
Experience: {resume_data.get("years_experience","N/A")}

Job Title: {job["title"]} at {job["company"]}
Matched Skills: {matched}
Job Snippet: {job.get("description","")[:500]}

Write 3 paragraphs. Be specific and enthusiastic. Do not use generic filler phrases."""
    return groq_call(client, system, user, max_tokens=500)

def ai_skill_roadmap(client, resume_data: dict, missing_skills: list, job_title: str) -> str:
    system = "You are a technical career advisor. Give precise, actionable learning paths."
    user = f"""Create a 30-60-90 day learning roadmap for:

Target Role: {job_title}
Missing Skills: {", ".join(missing_skills[:10])}
Current Level: {resume_data.get("years_experience","N/A")}

For each skill include: best free resource, estimated time, and a project idea to practice it.
Be specific — name actual courses, repos, or tools."""
    return groq_call(client, system, user, max_tokens=700)

def ai_interview_prep(client, job: dict, resume_data: dict) -> str:
    system = "You are an interview coach. Give targeted, role-specific interview questions and tips."
    user = f"""Generate 8 interview questions for:

Role: {job["title"]} at {job["company"]}
Candidate Skills: {", ".join(resume_data.get("all_skills_flat",[])[:10])}
Missing Skills: {", ".join(job.get("missing_skills",[])[:5])}

Mix of: behavioural (STAR), technical, and situational questions.
After each question add a 1-line tip on how to answer well."""
    return groq_call(client, system, user, max_tokens=700)

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR — API KEY CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

def get_api_keys():
    """Get API keys from st.secrets (Streamlit Cloud) or sidebar input."""
    groq_key     = ""
    rapidapi_key = ""

    # Try st.secrets first (production)
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    try:
        rapidapi_key = st.secrets.get("RAPIDAPI_KEY", "")
    except Exception:
        pass

    with st.sidebar:
        st.header("⚙️ Configuration")

        # Groq key
        if not groq_key:
            st.markdown("**Groq API Key** (free at [console.groq.com](https://console.groq.com))")
            groq_key = st.text_input("Groq API Key", type="password",
                                     placeholder="gsk_...", key="groq_key_input",
                                     label_visibility="collapsed")
            if groq_key:
                st.success("✅ Groq key set")
        else:
            st.success("✅ Groq API key loaded")

        st.divider()

        # RapidAPI key
        if not rapidapi_key:
            st.markdown("**RapidAPI Key** (optional — for JSearch live jobs)")
            st.caption("Free tier: 10 req/month at [rapidapi.com](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)")
            rapidapi_key = st.text_input("RapidAPI Key", type="password",
                                          placeholder="your_key...", key="rapidapi_key_input",
                                          label_visibility="collapsed")
            if rapidapi_key:
                st.success("✅ RapidAPI key set")
        else:
            st.success("✅ RapidAPI key loaded")

        st.divider()

        # Job search settings
        st.header("🔍 Job Search Settings")
        job_location = st.text_input("Preferred Location", placeholder="e.g. Remote, New York, London", value="Remote")
        job_role     = st.text_input("Target Role", placeholder="e.g. Data Scientist, Backend Engineer")
        top_k        = st.slider("Top K Jobs to show", 5, 30, 10)

        st.divider()
        st.caption("Built with ⚡ Streamlit · Groq · Himalayas API")

    return groq_key, rapidapi_key, job_location, job_role, top_k

# ══════════════════════════════════════════════════════════════════════
# SKILL GAP VISUALISATION
# ══════════════════════════════════════════════════════════════════════

def render_skill_gap(resume_data: dict, ranked_jobs: list):
    """Aggregate missing skills across top N jobs."""
    if not ranked_jobs:
        st.info("No jobs loaded yet. Go to Job Matches first.")
        return

    top_jobs = ranked_jobs[:10]
    all_missing = defaultdict(int)
    all_matched = defaultdict(int)

    for job in top_jobs:
        for s in job.get("missing_skills", []):
            all_missing[s] += 1
        for s in job.get("matched_skills", []):
            all_matched[s] += 1

    # Top missing skills
    top_missing = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:15]
    top_matched = sorted(all_matched.items(), key=lambda x: x[1], reverse=True)[:10]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚨 Top Missing Skills")
        st.caption("Skills appearing most in job descriptions you don't have")
        if top_missing:
            for skill, count in top_missing:
                pct = count / len(top_jobs)
                cat = FLAT_SKILLS.get(skill, "🔧 Tools")
                st.markdown(f"**`{skill}`** — needed in {count}/{len(top_jobs)} jobs")
                st.progress(pct)
        else:
            st.success("Great! No major skill gaps found in top jobs.")

    with col2:
        st.subheader("✅ Your Strongest Matches")
        st.caption("Skills you have that appear most across job descriptions")
        if top_matched:
            for skill, count in top_matched:
                pct = count / len(top_jobs)
                st.markdown(f"**`{skill}`** — matched in {count}/{len(top_jobs)} jobs")
                st.progress(pct)

    # Category coverage
    st.subheader("📊 Skill Category Coverage")
    st.caption("How well your skills cover each category across the top jobs")
    resume_skills = set(resume_data.get("all_skills_flat", []))

    category_stats = defaultdict(lambda: {"have": 0, "missing": 0})
    for job in top_jobs:
        for s in job.get("matched_skills", []):
            cat = FLAT_SKILLS.get(s, "Other")
            category_stats[cat]["have"] += 1
        for s in job.get("missing_skills", []):
            cat = FLAT_SKILLS.get(s, "Other")
            category_stats[cat]["missing"] += 1

    if category_stats:
        cols = st.columns(2)
        for i, (cat, stats) in enumerate(category_stats.items()):
            total = stats["have"] + stats["missing"]
            if total == 0:
                continue
            pct = stats["have"] / total
            (cols[0] if i % 2 == 0 else cols[1]).markdown(
                f"**{cat}** — {stats['have']}/{total} skills covered"
            )
            (cols[0] if i % 2 == 0 else cols[1]).progress(pct)


# ══════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════

groq_key, rapidapi_key, job_location, job_role, top_k = get_api_keys()
groq_client = get_groq_client(groq_key) if groq_key else None

# ── HEADER ──────────────────────────────────────────────────────────
st.title("⚡ HireMind")
st.caption("AI-powered resume parser · job matcher · skill gap analyser · career coach")
st.divider()

# ── RESUME INPUT ─────────────────────────────────────────────────────
col_upload, col_paste = st.columns([1, 1], gap="large")

with col_upload:
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

with col_paste:
    with st.expander("✏️ Or paste resume text instead"):
        manual_text = st.text_area("Paste your resume here", height=180,
                                   label_visibility="collapsed")

analyze_btn = st.button("⚡ Analyze Resume", type="primary", use_container_width=True, key="analyze")

# ── ANALYSIS ──────────────────────────────────────────────────────────
if analyze_btn:
    if not uploaded_file and not (manual_text and manual_text.strip()):
        st.warning("Please upload a PDF or paste resume text first.")
        st.stop()

    with st.spinner("Parsing your resume..."):
        raw_text = extract_text_from_pdf(uploaded_file) if uploaded_file else manual_text
        if not raw_text.strip():
            st.error("Could not extract text. Try pasting the content manually.")
            st.stop()
        resume_data = parse_resume(raw_text)
        st.session_state["resume_data"] = resume_data
        st.session_state["raw_text"]    = raw_text
        st.session_state["jobs_loaded"] = False

    st.success(
        f"✅ Resume parsed — **{resume_data['total_skills']} skills** found "
        f"across **{len(resume_data['skills'])} categories**"
    )

# ── REQUIRE RESUME TO CONTINUE ────────────────────────────────────────
if "resume_data" not in st.session_state:
    st.info("👆 Upload your resume above to get started.")
    st.stop()

resume_data = st.session_state["resume_data"]
raw_text    = st.session_state["raw_text"]

st.divider()

# ── METRICS ROW ────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Skills Found",    resume_data["total_skills"])
c2.metric("Experience",      resume_data["years_experience"])
c3.metric("Categories",      len(resume_data["skills"]))
c4.metric("Words",           resume_data["word_count"])
c5.metric("Roles Detected",  len(resume_data["job_titles"]))

st.divider()

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Resume Profile",
    "🔍 Job Matches",
    "📊 Skill Gap",
    "🤖 AI Coach",
    "📦 Export",
])

# ─────────────────────────────────────────────────────────────────────
# TAB 1 — RESUME PROFILE
# ─────────────────────────────────────────────────────────────────────
with tab1:
    contact = resume_data["contact"]
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Contact Info")
        for label, key in [("Name","name"),("Email","email"),("Phone","phone"),
                            ("LinkedIn","linkedin"),("GitHub","github"),("Website","website")]:
            val = contact.get(key)
            if val:
                st.text_input(label, value=val, disabled=True)

    with col_b:
        if resume_data["summary"]:
            st.subheader("Professional Summary")
            st.info(resume_data["summary"])
        if resume_data["job_titles"]:
            st.subheader("Detected Roles")
            for t in resume_data["job_titles"]:
                st.markdown(f"- {t}")

    if resume_data["education"]:
        st.subheader("Education")
        for edu in resume_data["education"]:
            st.markdown(f"🎓 {edu}")

    st.subheader("Skills by Category")
    for category, skills in resume_data["skills"].items():
        with st.expander(f"{category}  ·  {len(skills)} skills", expanded=True):
            st.markdown("  ".join([f"`{s}`" for s in skills]))

# ─────────────────────────────────────────────────────────────────────
# TAB 2 — JOB MATCHES
# ─────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("🔍 Find Matching Jobs")

    # Build search query
    if job_role:
        query = job_role
    elif resume_data["job_titles"]:
        query = resume_data["job_titles"][0]
    else:
        # Fall back to top skills
        query = " ".join(resume_data.get("all_skills_flat", ["developer"])[:3])

    col_q, col_btn = st.columns([3, 1])
    with col_q:
        query = st.text_input("Search query", value=query, label_visibility="collapsed")
    with col_btn:
        fetch_btn = st.button("🔍 Fetch Jobs", type="primary", use_container_width=True)

    if fetch_btn or (not st.session_state.get("jobs_loaded") and st.session_state.get("resume_data")):
        with st.spinner("Fetching live jobs..."):
            jobs_himalayas = fetch_jobs_himalayas(query, limit=20)
            jobs_jsearch   = fetch_jobs_jsearch(query, job_location, rapidapi_key) if rapidapi_key else []
            all_jobs       = jobs_himalayas + jobs_jsearch

            if not all_jobs:
                st.warning("No jobs found. Try a different query or check your API keys.")
            else:
                ranked = rank_jobs(resume_data, all_jobs)
                st.session_state["ranked_jobs"] = ranked
                st.session_state["jobs_loaded"]  = True

    ranked_jobs = st.session_state.get("ranked_jobs", [])

    if ranked_jobs:
        st.caption(f"Found **{len(ranked_jobs)}** jobs · sorted by match score · query: `{query}`")
        st.divider()

        # Score distribution
        scores = [j["score"] for j in ranked_jobs]
        high   = sum(1 for s in scores if s >= 60)
        mid    = sum(1 for s in scores if 30 <= s < 60)
        low    = sum(1 for s in scores if s < 30)
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("🟢 Strong Match (≥60%)", high)
        sc2.metric("🟡 Partial Match (30–59%)", mid)
        sc3.metric("🔴 Low Match (<30%)", low)
        st.divider()

        for i, job in enumerate(ranked_jobs[:top_k]):
            score = job["score"]
            color = "🟢" if score >= 60 else ("🟡" if score >= 30 else "🔴")

            with st.expander(
                f"{color} **{job['title']}** @ {job['company']}  ·  {score}% match  ·  {job['location']}",
                expanded=(i < 3)
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    if job.get("salary"):
                        st.markdown(f"💰 **Salary:** {job['salary']}")
                    st.markdown(f"📋 **Type:** {job['type']}  |  📅 **Posted:** {job['posted'] or 'N/A'}  |  🌐 **Source:** {job['source']}")
                    st.markdown("**Description:**")
                    st.markdown(job["description"][:600] + "..." if len(job["description"]) > 600 else job["description"])

                with col2:
                    # Match score gauge
                    st.metric("Match Score", f"{score}%")
                    st.progress(score / 100)

                    if job.get("matched_skills"):
                        st.markdown("**✅ Your matching skills:**")
                        st.markdown("  ".join([f"`{s}`" for s in job["matched_skills"][:8]]))

                    if job.get("missing_skills"):
                        st.markdown("**❌ Skills to learn:**")
                        st.markdown("  ".join([f"`{s}`" for s in job["missing_skills"][:6]]))

                col_apply, col_letter, col_prep = st.columns(3)

                with col_apply:
                    if job.get("url"):
                        st.link_button("🚀 Apply Now", job["url"], use_container_width=True)

                with col_letter:
                    if groq_client:
                        if st.button("✍️ Generate Cover Letter", key=f"cl_{i}", use_container_width=True):
                            with st.spinner("Writing cover letter..."):
                                letter = ai_cover_letter(groq_client, resume_data, job)
                                st.session_state[f"cover_letter_{i}"] = letter

                with col_prep:
                    if groq_client:
                        if st.button("🎯 Interview Prep", key=f"ip_{i}", use_container_width=True):
                            with st.spinner("Preparing questions..."):
                                prep = ai_interview_prep(groq_client, job, resume_data)
                                st.session_state[f"interview_prep_{i}"] = prep

                # Show generated content
                if st.session_state.get(f"cover_letter_{i}"):
                    st.divider()
                    st.markdown("**✍️ Cover Letter:**")
                    st.markdown(st.session_state[f"cover_letter_{i}"])
                    st.download_button(
                        "⬇️ Download Cover Letter",
                        data=st.session_state[f"cover_letter_{i}"],
                        file_name=f"cover_letter_{job['company'].replace(' ','_')}.txt",
                        mime="text/plain",
                        key=f"dl_cl_{i}",
                    )

                if st.session_state.get(f"interview_prep_{i}"):
                    st.divider()
                    st.markdown("**🎯 Interview Questions:**")
                    st.markdown(st.session_state[f"interview_prep_{i}"])

    elif not st.session_state.get("jobs_loaded"):
        st.info("👆 Click **Fetch Jobs** to find live job matches.")

# ─────────────────────────────────────────────────────────────────────
# TAB 3 — SKILL GAP
# ─────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Skill Gap Analysis")
    ranked_jobs = st.session_state.get("ranked_jobs", [])
    render_skill_gap(resume_data, ranked_jobs)

    if groq_client and ranked_jobs:
        st.divider()
        st.subheader("🗺️ AI Learning Roadmap")
        st.caption("Get a personalised 30-60-90 day plan to close your skill gaps")

        # Aggregate top missing skills
        all_missing = defaultdict(int)
        for job in ranked_jobs[:10]:
            for s in job.get("missing_skills", []):
                all_missing[s] += 1
        top_missing_skills = [s for s, _ in sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:8]]

        target_role = st.text_input("Target role for roadmap",
                                    value=resume_data["job_titles"][0] if resume_data["job_titles"] else "Software Engineer")

        if st.button("📅 Generate Learning Roadmap", type="primary"):
            with st.spinner("Building your personalised learning roadmap..."):
                roadmap = ai_skill_roadmap(groq_client, resume_data, top_missing_skills, target_role)
                st.session_state["roadmap"] = roadmap

        if st.session_state.get("roadmap"):
            st.markdown(st.session_state["roadmap"])
            st.download_button(
                "⬇️ Download Roadmap",
                data=st.session_state["roadmap"],
                file_name="learning_roadmap.txt",
                mime="text/plain",
            )

# ─────────────────────────────────────────────────────────────────────
# TAB 4 — AI COACH
# ─────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("🤖 AI Career Coach")

    if not groq_client:
        st.warning("⚠️ Add your **Groq API key** in the sidebar to unlock AI coaching features.")
        st.markdown("""
**How to get a free Groq API key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free (no credit card needed)
3. Create an API key
4. Paste it in the sidebar
        """)
    else:
        # Resume tips
        st.markdown("### 📝 Resume Review & Tips")
        if st.button("🔍 Analyse My Resume", type="primary", key="resume_tips_btn"):
            with st.spinner("Analysing your resume..."):
                tips = ai_resume_tips(groq_client, resume_data)
                st.session_state["resume_tips"] = tips

        if st.session_state.get("resume_tips"):
            st.markdown(st.session_state["resume_tips"])

        st.divider()

        # Free chat
        st.markdown("### 💬 Ask the Career Coach")
        st.caption("Ask anything about your job search, career transitions, salary negotiation, interviews...")

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Display history
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_msg = st.chat_input("Ask your career coach...")
        if user_msg:
            st.session_state["chat_history"].append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)

            # Build context
            skills_ctx = ", ".join(resume_data.get("all_skills_flat", [])[:15])
            exp_ctx    = resume_data.get("years_experience", "N/A")
            system_ctx = (
                f"You are an expert career coach. The user's resume shows: "
                f"Experience: {exp_ctx}, Skills: {skills_ctx}. "
                "Give practical, specific, personalized advice. Be encouraging but honest."
            )

            try:
                messages = [{"role": "system", "content": system_ctx}]
                messages += [{"role": m["role"], "content": m["content"]}
                             for m in st.session_state["chat_history"]]
                resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=600,
                    temperature=0.7,
                )
                reply = resp.choices[0].message.content.strip()
            except Exception as e:
                reply = f"⚠️ Error: {e}"

            st.session_state["chat_history"].append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

        if st.session_state.get("chat_history"):
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state["chat_history"] = []
                st.rerun()

# ─────────────────────────────────────────────────────────────────────
# TAB 5 — EXPORT
# ─────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("📦 Export Your Data")

    ranked_jobs = st.session_state.get("ranked_jobs", [])

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("#### Resume Data (JSON)")
        export_resume = {
            "contact":          resume_data["contact"],
            "skills":           resume_data["skills"],
            "education":        resume_data["education"],
            "job_titles":       resume_data["job_titles"],
            "summary":          resume_data["summary"],
            "years_experience": resume_data["years_experience"],
            "stats": {
                "total_skills":     resume_data["total_skills"],
                "word_count":       resume_data["word_count"],
                "skill_categories": len(resume_data["skills"]),
            },
        }
        st.download_button(
            "⬇️ Download Resume JSON",
            data=json.dumps(export_resume, indent=2),
            file_name="resume_data.json",
            mime="application/json",
            use_container_width=True,
        )
        with st.expander("Preview"):
            st.json(export_resume)

    with col_e2:
        st.markdown("#### Job Matches (JSON)")
        if ranked_jobs:
            export_jobs = [
                {
                    "rank":           i + 1,
                    "title":          j["title"],
                    "company":        j["company"],
                    "location":       j["location"],
                    "match_score":    j["score"],
                    "matched_skills": j["matched_skills"],
                    "missing_skills": j["missing_skills"],
                    "url":            j["url"],
                    "salary":         j.get("salary", ""),
                    "source":         j["source"],
                }
                for i, j in enumerate(ranked_jobs[:top_k])
            ]
            st.download_button(
                "⬇️ Download Job Matches JSON",
                data=json.dumps(export_jobs, indent=2),
                file_name="job_matches.json",
                mime="application/json",
                use_container_width=True,
            )
            with st.expander("Preview top 3"):
                st.json(export_jobs[:3])
        else:
            st.info("Fetch jobs first in the Job Matches tab.")

    # Full report as markdown
    st.divider()
    st.markdown("#### 📄 Full Report (Markdown)")
    if st.button("Generate Full Report", use_container_width=True):
        name  = resume_data["contact"].get("name", "Candidate")
        lines = [
            f"# HireMind Report — {name}",
            "",
            "## Resume Summary",
            f"- **Experience:** {resume_data['years_experience']}",
            f"- **Total Skills:** {resume_data['total_skills']}",
            f"- **Roles:** {', '.join(resume_data['job_titles'][:3])}",
            "",
            "## Skills",
        ]
        for cat, skills in resume_data["skills"].items():
            lines.append(f"### {cat}")
            lines.append(", ".join(skills))
            lines.append("")

        if ranked_jobs:
            lines += ["## Top Job Matches", ""]
            for i, j in enumerate(ranked_jobs[:5]):
                lines += [
                    f"### {i+1}. {j['title']} @ {j['company']} ({j['score']}% match)",
                    f"- Location: {j['location']}",
                    f"- Matched Skills: {', '.join(j['matched_skills'][:5])}",
                    f"- Missing Skills: {', '.join(j['missing_skills'][:5])}",
                    f"- Apply: {j['url']}",
                    "",
                ]

        report = "\n".join(lines)
        st.session_state["full_report"] = report

    if st.session_state.get("full_report"):
        st.download_button(
            "⬇️ Download Full Report (Markdown)",
            data=st.session_state["full_report"],
            file_name="hiremind_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
        with st.expander("Preview"):
            st.markdown(st.session_state["full_report"])

    # Raw text
    st.divider()
    st.markdown("#### 📄 Raw Extracted Text")
    st.text_area(
        "raw",
        value=raw_text[:5000] + ("…" if len(raw_text) > 5000 else ""),
        height=300,
        label_visibility="collapsed",
        disabled=True,
    )
