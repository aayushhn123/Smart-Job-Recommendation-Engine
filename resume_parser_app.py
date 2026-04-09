import streamlit as st
import pdfplumber
import re
import json
import requests
from collections import defaultdict

st.set_page_config(
    page_title="HireMind",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        "mlops","feature engineering","time series","random forest","statistics",
        "probability","data analysis","data science",
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
        "opencv","yfinance",
    ],
    "🤝 Soft Skills": [
        "leadership","communication","teamwork","problem solving","critical thinking",
        "project management","agile","scrum","kanban","collaboration","mentoring",
        "time management","analytical","research","presentation","negotiation",
        "stakeholder management","strategic thinking","decision making","adaptability",
    ],
}

FLAT_SKILLS = {skill.lower(): cat for cat, skills in SKILL_DB.items() for skill in skills}

ATS_POWER_WORDS = {
    "achieved","improved","increased","reduced","led","built","designed","developed",
    "optimised","optimized","deployed","automated","managed","delivered","launched",
    "scaled","researched","analysed","analyzed","implemented","created","collaborated",
    "mentored","drove","spearheaded","streamlined","accelerated",
}

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
    "linkedin": r"(?:linkedin\.com/in/|linkedin:\s*|linked\s*in\s*[:\|]?\s*)([A-Za-z0-9\-_/]+)",
    "github":   r"(?:github\.com/|github:\s*)([A-Za-z0-9\-_]+)",
    "website":  r"https?://(?!linkedin|github)[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+",
}

EDU_KW = re.compile(
    r"\b(university|college|school|institute|b\.?tech|m\.?tech|bachelor|master|"
    r"phd|diploma|mba|bba|cgpa|gpa|grade|degree|pursuing|ssc|hsc|coursera|"
    r"certification|certificate|nmims|iit|nit|bits)\b",
    re.IGNORECASE,
)
WORK_KW = re.compile(
    r"\b(experience|work|job|role|position|company|organisation|organization|"
    r"employed|internship|intern|client|startup|project)\b",
    re.IGNORECASE,
)

# ── Parsing functions ──────────────────────────────────────────────────────────

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
        r"(B\.?Tech|B\.?E\.?|Bachelor|B\.?Sc?|B\.?A\.?|M\.?Tech|M\.?E\.?|Master|"
        r"M\.?Sc?|M\.?A\.?|PhD|Ph\.D|MBA|BBA|Diploma|Associate)[^\n]{0,80}",
        text, re.IGNORECASE
    ):
        if len(m) > 5:
            edu.append(m.strip())
    for m in re.findall(r"(?:University|College|Institute|School|Academy)\s+of\s+[A-Z][A-Za-z\s,]+", text):
        edu.append(m.strip())
    for m in re.findall(r"(?:NMIMS|IIT|NIT|BITS|VIT|MIT|Stanford|Harvard|Carnegie|Oxford|Cambridge)[^\n]{0,60}", text):
        edu.append(m.strip())
    return list(dict.fromkeys(edu))[:6]


def extract_years_experience(text: str) -> str:
    for p in [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+)\+?\s*years?",
        r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience",
    ]:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1) + "+ yrs"

    lines = text.split("\n")
    work_years = set()
    for i, line in enumerate(lines):
        if EDU_KW.search(line):
            continue
        context = "\n".join(lines[max(0, i - 2): i + 2])
        if EDU_KW.search(context) and not WORK_KW.search(context):
            continue
        pairs = re.findall(
            r"(20\d{2}|19\d{2})\s*[-\u2013\u2014]\s*(20\d{2}|Present|Current|Now)",
            line, re.IGNORECASE,
        )
        for s, e in pairs:
            try:
                start = int(s)
                end = 2025 if e.isalpha() else int(e)
                work_years.update(range(start, end + 1))
            except Exception:
                pass

    if work_years:
        t = max(work_years) - min(work_years)
        if t > 0:
            return f"~{t} yrs"

    all_dates = re.findall(
        r"(20\d{2}|19\d{2})\s*[-\u2013\u2014]\s*(20\d{2}|Present|Current|Now)",
        text, re.IGNORECASE,
    )
    return "Fresher" if all_dates else "N/A"


def extract_job_titles(text: str) -> list:
    TITLE_KW = [
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
            if any(kw in lower for kw in TITLE_KW) and not re.search(r"\d{4}", line):
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


def compute_resume_completeness(resume_data: dict, raw_text: str) -> dict:
    scores = {}
    tips = []
    text_low = raw_text.lower()
    contact = resume_data.get("contact", {})

    c_score = sum([
        5 if contact.get("name") else 0,
        5 if contact.get("email") else 0,
        4 if contact.get("phone") else 0,
        4 if contact.get("linkedin") else 0,
        2 if contact.get("github") else 0,
    ])
    scores["Contact Info"] = c_score
    if not contact.get("linkedin"):
        tips.append("Add your LinkedIn URL — most recruiters check this first.")
    if not contact.get("github"):
        tips.append("Add your GitHub profile — essential for tech roles to showcase projects.")

    summary = resume_data.get("summary", "")
    if len(summary) > 100:
        scores["Summary"] = 15
    elif len(summary) > 40:
        scores["Summary"] = 8
        tips.append("Expand your professional summary to 3-4 sentences highlighting your specialisation.")
    else:
        scores["Summary"] = 0
        tips.append("Add a 3-4 sentence professional summary at the top — the first thing recruiters read.")

    total_skills = resume_data.get("total_skills", 0)
    cat_count = len(resume_data.get("skills", {}))
    if total_skills >= 15 and cat_count >= 4:
        scores["Skills"] = 20
    elif total_skills >= 8:
        scores["Skills"] = 12
        tips.append(f"You have {total_skills} skills detected. Aim for 15+ across 4+ categories for ATS.")
    else:
        scores["Skills"] = 5
        tips.append("Add more technical skills — tools, libraries, frameworks you use daily.")

    ats_found = sum(1 for w in ATS_POWER_WORDS if w in text_low)
    if ats_found >= 8:
        scores["ATS Keywords"] = 20
    elif ats_found >= 4:
        scores["ATS Keywords"] = 12
        tips.append("Use more action verbs: built, improved, reduced, achieved, deployed, automated...")
    else:
        scores["ATS Keywords"] = 4
        tips.append("Start every bullet point with a strong verb: Built / Developed / Led / Improved / Reduced.")

    edu = resume_data.get("education", [])
    scores["Education"] = 10 if edu else 0
    if not edu:
        tips.append("Add education details with institution name, degree, and graduation year/CGPA.")

    has_proj = bool(re.search(r"\bproject", raw_text, re.IGNORECASE))
    has_exp  = bool(re.search(SECTION_PATTERNS["experience"], raw_text, re.IGNORECASE))
    if has_proj and has_exp:
        scores["Projects & Experience"] = 15
    elif has_proj or has_exp:
        scores["Projects & Experience"] = 10
        if not has_proj:
            tips.append("Add a Projects section — critical for freshers to demonstrate practical ability.")
    else:
        scores["Projects & Experience"] = 0
        tips.append("Add a Projects or Work Experience section to show practical application of your skills.")

    overall = min(sum(scores.values()), 100)
    return {"scores": scores, "overall": overall, "tips": tips, "ats_words": ats_found}


def parse_resume(text: str) -> dict:
    skills = extract_skills(text)
    all_flat = [s for cat in skills.values() for s in cat]
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
        "all_skills_flat":  all_flat,
    }


# ── Domain detection ─────────────────────────────────────────────────────────

DOMAIN_SIGNALS = [
    ({"langchain","llm","openai","hugging face","transformers","generative ai","bert","gpt"},
     "AI Engineer", "AI LLM engineer"),
    ({"machine learning","deep learning","tensorflow","pytorch","scikit-learn","sklearn",
      "neural networks","nlp","computer vision","xgboost","lightgbm","random forest"},
     "Machine Learning Engineer", "machine learning engineer"),
    ({"pandas","numpy","matplotlib","seaborn","statistics","probability",
      "data analysis","data science","feature engineering","time series"},
     "Data Scientist", "data scientist python"),
    ({"sql","bigquery","snowflake","redshift","dbt","tableau","power bi","looker"},
     "Data Analyst", "data analyst sql"),
    ({"spark","hadoop","kafka","airflow","bigquery","data pipeline"},
     "Data Engineer", "data engineer"),
    ({"docker","kubernetes","terraform","aws","azure","gcp","ci/cd","github actions"},
     "DevOps Engineer", "devops cloud engineer"),
    ({"react","angular","vue","next.js","typescript","javascript"},
     "Frontend Developer", "frontend developer react"),
    ({"django","fastapi","flask","spring boot","node.js","rest api","postgresql","mongodb"},
     "Backend Developer", "backend developer python"),
    ({"opencv","computer vision","yolo","image processing"},
     "Computer Vision Engineer", "computer vision engineer"),
]

PRIORITY_SKILLS = [
    "machine learning","deep learning","data science","nlp","computer vision",
    "tensorflow","pytorch","scikit-learn","pandas","sql","python","spark",
    "docker","kubernetes","react","fastapi","django","langchain","llm",
    "time series","random forest","statistics",
]


def detect_domain(skills_set: set) -> tuple:
    best_title, best_kw, best_overlap = "Software Engineer", "software engineer", 0
    for required, title, kw in DOMAIN_SIGNALS:
        overlap = len(required & skills_set)
        if overlap > best_overlap:
            best_overlap = overlap
            best_title = title
            best_kw = kw
    return best_title, best_kw, best_overlap


def build_smart_query(resume_data: dict, override_role: str = "") -> str:
    if override_role and override_role.strip():
        return override_role.strip()
    skills_set = set(s.lower() for s in resume_data.get("all_skills_flat", []))
    title, kw, _ = detect_domain(skills_set)
    top_skills = [s for s in PRIORITY_SKILLS if s in skills_set][:2]
    return f"{title} {' '.join(top_skills)}" if top_skills else title


# ── Job fetching ──────────────────────────────────────────────────────────────

def extract_skills_from_jd(text: str) -> list:
    text_lower = text.lower()
    found, matched = [], set()
    for skill in sorted(FLAT_SKILLS.keys(), key=len, reverse=True):
        if skill in matched:
            continue
        if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
            found.append(skill)
            matched.add(skill)
    return found[:30]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_jobs_himalayas(query: str, limit: int = 20) -> list:
    try:
        r = requests.get(
            "https://himalayas.app/jobs/api",
            params={"q": query, "limit": limit},
            timeout=10,
        )
        if r.status_code == 200:
            return [
                {
                    "title":           j.get("title", ""),
                    "company":         j.get("companyName", ""),
                    "location":        (j.get("locationRestrictions") or ["Remote"])[0],
                    "description":     j.get("description", "")[:2000],
                    "url":             j.get("applyUrl") or j.get("url", ""),
                    "type":            j.get("employmentType", "Full Time"),
                    "posted":          (j.get("createdAt") or "")[:10],
                    "source":          "Himalayas",
                    "salary":          "",
                    "skills_required": extract_skills_from_jd(j.get("description", "")),
                }
                for j in r.json().get("jobs", [])
            ]
    except Exception:
        pass
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_jobs_jsearch(query: str, location: str, rapidapi_key: str) -> list:
    if not rapidapi_key:
        return []
    try:
        r = requests.get(
            "https://jsearch.p.rapidapi.com/search",
            headers={"X-RapidAPI-Key": rapidapi_key,
                     "X-RapidAPI-Host": "jsearch.p.rapidapi.com"},
            params={"query": f"{query} in {location}" if location else query,
                    "page": "1", "num_pages": "1", "date_posted": "month"},
            timeout=12,
        )
        if r.status_code == 200:
            result = []
            for j in r.json().get("data", []):
                desc = j.get("job_description", "")[:2000]
                mn, mx = j.get("job_min_salary"), j.get("job_max_salary")
                cur, per = j.get("job_salary_currency", "USD"), j.get("job_salary_period", "")
                sal = (f"{cur} {int(mn):,}–{int(mx):,}/{per}" if mn and mx
                       else f"{cur} {int(mn):,}+/{per}" if mn else "")
                result.append({
                    "title":           j.get("job_title", ""),
                    "company":         j.get("employer_name", ""),
                    "location":        j.get("job_city") or j.get("job_country", ""),
                    "description":     desc,
                    "url":             j.get("job_apply_link", ""),
                    "type":            j.get("job_employment_type", "FULLTIME"),
                    "posted":          (j.get("job_posted_at_datetime_utc") or "")[:10],
                    "source":          "JSearch / Google Jobs",
                    "salary":          sal,
                    "skills_required": extract_skills_from_jd(desc),
                })
            return result
    except Exception:
        pass
    return []


# ── Relevance filter ──────────────────────────────────────────────────────────

OFF_DOMAIN = {
    "customer service","customer support","sales representative","sales associate",
    "cashier","retail","warehouse","driver","cleaner","barista","receptionist",
    "nurse","teacher","chef","cook","waiter","security guard","janitor",
    "call centre","call center","telemarketer","delivery driver","housekeeper",
}
TECH_KW = {
    "engineer","developer","scientist","analyst","data","ml","ai","software",
    "backend","frontend","fullstack","full stack","python","research","quant",
    "intern","associate","architect","devops","platform","infrastructure",
    "machine learning","deep learning","nlp","computer vision","finance",
}


def is_relevant_job(job: dict, resume_skills: set) -> bool:
    title_lower = job.get("title", "").lower()
    if any(bad in title_lower for bad in OFF_DOMAIN):
        return False
    job_skills = set(s.lower() for s in job.get("skills_required", []))
    if resume_skills & job_skills:
        return True
    if any(kw in title_lower for kw in TECH_KW):
        return True
    return False


# ── Match scoring ─────────────────────────────────────────────────────────────

def compute_match(resume_skills: list, job: dict) -> dict:
    resume_set = set(s.lower() for s in resume_skills)
    job_set    = set(s.lower() for s in job.get("skills_required", []))
    matched    = resume_set & job_set
    missing    = job_set - resume_set
    extra      = resume_set - job_set
    skill_score = round(len(matched) / len(job_set) * 70) if job_set else 35
    title_lower = job.get("title", "").lower()
    title_score = min(sum(5 for s in resume_skills if s.lower() in title_lower), 20)
    desc_lower  = job.get("description", "").lower()
    freq_score  = min(round(sum(desc_lower.count(s) for s in matched) / max(len(matched), 1)), 10)
    total = min(skill_score + title_score + freq_score, 100)
    return {
        "score": total,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills":   sorted(list(extra)[:10]),
        "score_breakdown": {
            "skill_overlap": skill_score,
            "title_match":   title_score,
            "freq_bonus":    freq_score,
        },
    }


def rank_jobs(resume_data: dict, jobs: list) -> list:
    resume_skills = resume_data.get("all_skills_flat", [])
    resume_set    = set(s.lower() for s in resume_skills)
    seen, ranked  = set(), []
    for job in jobs:
        key = (job["title"].lower().strip(), job["company"].lower().strip())
        if key in seen:
            continue
        seen.add(key)
        if not is_relevant_job(job, resume_set):
            continue
        ranked.append({**job, **compute_match(resume_skills, job)})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


# ── Groq AI ───────────────────────────────────────────────────────────────────

def get_groq_client(api_key: str):
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception:
        return None


def groq_call(client, system: str, user: str, max_tokens: int = 900) -> str:
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Groq API error: {e}"


def ai_resume_tips(client, resume_data: dict, completeness: dict) -> str:
    weak = [k for k, v in completeness.get("scores", {}).items() if v < 10]
    return groq_call(client,
        "You are a senior recruiter and resume expert. Give brutally honest, specific, actionable feedback.",
        f"""Review this resume (completeness: {completeness.get("overall",0)}/100):
Experience: {resume_data.get("years_experience","N/A")}
Skills: {", ".join(resume_data.get("all_skills_flat",[])[:20])}
Education: {", ".join(resume_data.get("education",[])[:2])}
Weak areas: {", ".join(weak) if weak else "none"}
Summary: {resume_data.get("summary","")[:200]}

Give exactly 5 numbered tips. Each tip: be specific, say WHY it matters for ATS/recruiters, give a concrete example.""",
        max_tokens=700)


def ai_cover_letter(client, resume_data: dict, job: dict) -> str:
    return groq_call(client,
        "You are an expert cover letter writer. Write confident, specific letters that get interviews. Never use clichés.",
        f"""Cover letter for:
Candidate: {resume_data.get("contact",{}).get("name","Applicant")}
Experience: {resume_data.get("years_experience","Fresher")}
Skills: {", ".join(resume_data.get("all_skills_flat",[])[:15])}
Matched skills: {", ".join(job.get("matched_skills",[])[:10])}
Target: {job["title"]} at {job["company"]}
Job snippet: {job.get("description","")[:400]}

Format: opening hook (NOT "I am writing to apply"), 2 sentences connecting skills to their needs, confident close.
Under 200 words. Zero filler phrases.""",
        max_tokens=400)


def ai_skill_roadmap(client, resume_data: dict, missing_skills: list, target_role: str) -> str:
    return groq_call(client,
        "You are a technical career mentor. Give precise, realistic plans with actual named resources.",
        f"""30-60-90 day roadmap for:
Target: {target_role} | Level: {resume_data.get("years_experience","Fresher")}
Current skills: {", ".join(resume_data.get("all_skills_flat",[])[:8])}
Skills to learn: {", ".join(missing_skills[:8])}

For each skill: (1) exact free resource name, (2) hours to basic proficiency, (3) one portfolio project idea.
Organise into Day 1-30 / Day 31-60 / Day 61-90.""",
        max_tokens=800)


def ai_interview_prep(client, job: dict, resume_data: dict) -> str:
    return groq_call(client,
        "You are an interview coach with 1000+ technical interviews. Give targeted, role-specific prep.",
        f"""Interview prep for: {job["title"]} at {job["company"]}
Candidate skills: {", ".join(resume_data.get("all_skills_flat",[])[:10])}
Gaps to address: {", ".join(job.get("missing_skills",[])[:5])}

8 questions: 3 technical, 2 behavioural STAR, 2 situational, 1 about skill gaps.
After each question: TIP: [one-line advice on how to answer well]""",
        max_tokens=750)


# ── Skill gap renderer ────────────────────────────────────────────────────────

def render_skill_gap(resume_data: dict, ranked_jobs: list):
    if not ranked_jobs:
        st.info("👆 Fetch jobs in the Job Matches tab first.")
        return

    top_jobs = ranked_jobs[:10]
    n = len(top_jobs)
    all_missing: dict = defaultdict(int)
    all_matched: dict = defaultdict(int)
    for job in top_jobs:
        for s in job.get("missing_skills", []):
            all_missing[s] += 1
        for s in job.get("matched_skills", []):
            all_matched[s] += 1

    top_missing = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:12]
    top_matched = sorted(all_matched.items(), key=lambda x: x[1], reverse=True)[:10]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚨 Top Missing Skills")
        st.caption(f"Most needed across your top {n} matched jobs — you don't have these yet")
        if top_missing:
            for skill, count in top_missing:
                pct = count / n
                urg = "🔴" if pct >= 0.7 else ("🟡" if pct >= 0.4 else "⚪")
                cat = FLAT_SKILLS.get(skill, "🔧 Tools")
                st.markdown(f"{urg} **`{skill}`** &nbsp;`{cat}`&nbsp; — {count}/{n} jobs")
                st.progress(pct)
        else:
            st.success("🎉 No major skill gaps in your top matches!")

    with col2:
        st.subheader("✅ Your Strongest Assets")
        st.caption("Skills you have that appear most in job descriptions")
        for skill, count in top_matched:
            st.markdown(f"✅ **`{skill}`** — in {count}/{n} jobs")
            st.progress(count / n)

    st.divider()
    st.subheader("📊 Category Coverage")
    cat_stats: dict = defaultdict(lambda: {"have": 0, "need": 0})
    for job in top_jobs:
        for s in job.get("matched_skills", []):
            cat_stats[FLAT_SKILLS.get(s, "Other")]["have"] += 1
        for s in job.get("missing_skills", []):
            cat_stats[FLAT_SKILLS.get(s, "Other")]["need"] += 1

    cols = st.columns(2)
    for idx, (cat, stats) in enumerate(sorted(cat_stats.items(),
                                               key=lambda x: x[1]["have"] + x[1]["need"],
                                               reverse=True)):
        total = stats["have"] + stats["need"]
        if total == 0:
            continue
        pct = stats["have"] / total
        col = cols[idx % 2]
        col.markdown(f"**{cat}**  `{stats['have']}/{total} covered`")
        col.progress(pct)


# ── Sidebar / config ──────────────────────────────────────────────────────────

def get_config():
    groq_key = rapidapi_key = ""
    try:
        groq_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    try:
        rapidapi_key = st.secrets.get("RAPIDAPI_KEY", "")
    except Exception:
        pass

    with st.sidebar:
        st.title("⚙️ HireMind")
        st.caption("AI-powered job recommendation engine")
        st.divider()
        st.subheader("🔑 API Keys")
        if not groq_key:
            st.markdown("**Groq** — free at [console.groq.com](https://console.groq.com)")
            groq_key = st.text_input("Groq API Key", type="password",
                                     placeholder="gsk_...", key="groq_input",
                                     label_visibility="collapsed")
            if groq_key:
                st.success("✅ Groq key set")
        else:
            st.success("✅ Groq key loaded")

        if not rapidapi_key:
            st.markdown("**RapidAPI** — optional, [JSearch free tier](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)")
            rapidapi_key = st.text_input("RapidAPI Key", type="password",
                                          placeholder="optional...", key="rapid_input",
                                          label_visibility="collapsed")
        else:
            st.success("✅ RapidAPI key loaded")

        st.divider()
        st.subheader("🔍 Job Search")
        job_role     = st.text_input("Override Target Role",
                                     placeholder="e.g. Data Scientist (blank = auto-detect)")
        job_location = st.text_input("Location", value="Remote")
        top_k        = st.slider("Max jobs to display", 5, 25, 10)
        st.divider()
        st.caption("Himalayas API · Groq LLaMA 3.3 · JSearch")
    return groq_key, rapidapi_key, job_location, job_role, top_k


# ══════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════

groq_key, rapidapi_key, job_location, job_role, top_k = get_config()
groq_client = get_groq_client(groq_key) if groq_key else None

st.title("⚡ HireMind")
st.caption("Upload your resume · get matched to live jobs · close skill gaps · get AI coaching")
st.divider()

c_up, c_paste = st.columns([1, 1], gap="large")
with c_up:
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
with c_paste:
    with st.expander("✏️ Or paste resume text instead"):
        manual_text = st.text_area("Paste resume here", height=180, label_visibility="collapsed")

analyze_btn = st.button("⚡  Analyze Resume", type="primary", use_container_width=True, key="analyze")

if analyze_btn:
    if not uploaded_file and not (manual_text and manual_text.strip()):
        st.warning("Please upload a PDF or paste resume text first.")
        st.stop()
    with st.spinner("Parsing resume..."):
        raw_text = extract_text_from_pdf(uploaded_file) if uploaded_file else manual_text
        if not raw_text.strip():
            st.error("Could not extract text from the PDF. Try pasting the content manually.")
            st.stop()
        resume_data  = parse_resume(raw_text)
        completeness = compute_resume_completeness(resume_data, raw_text)
        st.session_state.update({
            "resume_data":  resume_data,
            "raw_text":     raw_text,
            "completeness": completeness,
            "jobs_loaded":  False,
            "ranked_jobs":  [],
        })
    st.success(
        f"✅ Parsed — **{resume_data['total_skills']} skills** · "
        f"**{len(resume_data['skills'])} categories** · "
        f"Resume score: **{completeness['overall']}/100**"
    )

if "resume_data" not in st.session_state:
    st.info("👆 Upload your resume above to get started.")
    st.stop()

resume_data  = st.session_state["resume_data"]
raw_text     = st.session_state["raw_text"]
completeness = st.session_state.get("completeness", {})

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Skills",       resume_data["total_skills"])
m2.metric("Experience",   resume_data["years_experience"])
m3.metric("Categories",   len(resume_data["skills"]))
m4.metric("Words",        resume_data["word_count"])
m5.metric("Resume Score", f"{completeness.get('overall',0)}/100")
m6.metric("ATS Keywords", completeness.get("ats_words", 0))
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 Resume Profile", "🔍 Job Matches", "📊 Skill Gap", "🤖 AI Coach", "📦 Export"
])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        st.subheader("📇 Contact Info")
        contact = resume_data["contact"]
        for label, key in [("Name","name"),("Email","email"),("Phone","phone"),
                            ("LinkedIn","linkedin"),("GitHub","github"),("Website","website")]:
            val = contact.get(key)
            if val:
                st.text_input(label, value=val, disabled=True)
        if resume_data["education"]:
            st.subheader("🎓 Education")
            for edu in resume_data["education"]:
                st.markdown(f"- {edu}")
        if resume_data["job_titles"]:
            st.subheader("💼 Detected Roles")
            for t in resume_data["job_titles"]:
                st.markdown(f"- {t}")

    with col_b:
        if resume_data["summary"]:
            st.subheader("📝 Professional Summary")
            st.info(resume_data["summary"])
        st.subheader("📊 Resume Completeness")
        overall = completeness.get("overall", 0)
        badge = "🟢" if overall >= 75 else ("🟡" if overall >= 50 else "🔴")
        st.markdown(f"### {badge} {overall} / 100")
        st.progress(overall / 100)
        max_map = {"Contact Info":20,"Summary":15,"Skills":20,
                   "ATS Keywords":20,"Education":10,"Projects & Experience":15}
        for section, score in completeness.get("scores", {}).items():
            max_s = max_map.get(section, 10)
            pct   = score / max_s if max_s else 0
            ic    = "✅" if pct >= 0.8 else ("⚠️" if pct >= 0.4 else "❌")
            st.markdown(f"{ic} **{section}** — {score}/{max_s}")
            st.progress(pct)
        if completeness.get("tips"):
            st.subheader("💡 Quick Wins")
            for tip in completeness["tips"][:4]:
                st.markdown(f"- {tip}")

    st.divider()
    st.subheader("🔧 Skills by Category")
    for cat, skills in resume_data["skills"].items():
        with st.expander(f"{cat}  ·  {len(skills)} skills", expanded=True):
            st.markdown("  ".join(f"`{s}`" for s in skills))

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("🔍 Live Job Matches")
    skills_set = set(s.lower() for s in resume_data.get("all_skills_flat", []))
    det_title, _, det_overlap = detect_domain(skills_set)
    smart_query = build_smart_query(resume_data, override_role=job_role)
    st.info(f"🧠 **Auto-detected domain:** {det_title} ({det_overlap} domain signals) — query: `{smart_query}`")

    col_q, col_btn = st.columns([3, 1])
    with col_q:
        query = st.text_input("Refine search query", value=smart_query, label_visibility="collapsed")
    with col_btn:
        fetch_btn = st.button("🔍 Fetch Jobs", type="primary", use_container_width=True)

    if fetch_btn or not st.session_state.get("jobs_loaded"):
        with st.spinner(f"Searching for '{query}' jobs..."):
            h_jobs = fetch_jobs_himalayas(query, limit=20)
            j_jobs = fetch_jobs_jsearch(query, job_location, rapidapi_key)
            all_j  = h_jobs + j_jobs
        if not all_j:
            st.warning("No jobs returned. Check your internet or try a different query.")
        else:
            ranked = rank_jobs(resume_data, all_j)
            if not ranked:
                st.warning(f"Found {len(all_j)} jobs but all were filtered as off-domain. Try a more specific query.")
                st.session_state["ranked_jobs"] = []
            else:
                st.session_state["ranked_jobs"] = ranked
                st.session_state["jobs_loaded"]  = True

    ranked_jobs = st.session_state.get("ranked_jobs", [])
    if ranked_jobs:
        scores = [j["score"] for j in ranked_jobs]
        high = sum(1 for s in scores if s >= 60)
        mid  = sum(1 for s in scores if 30 <= s < 60)
        low  = sum(1 for s in scores if s < 30)
        st.caption(f"**{len(ranked_jobs)}** relevant jobs · 🟢 {high} strong · 🟡 {mid} partial · 🔴 {low} low")
        st.divider()

        for i, job in enumerate(ranked_jobs[:top_k]):
            score = job["score"]
            badge = "🟢" if score >= 60 else ("🟡" if score >= 30 else "🔴")
            bkdn  = job.get("score_breakdown", {})
            with st.expander(
                f"{badge} **{job['title']}** @ {job['company']}  ·  {score}% match  ·  📍 {job['location']}",
                expanded=(i < 2),
            ):
                c_left, c_right = st.columns([2, 1])
                with c_left:
                    meta = []
                    if job.get("salary"):  meta.append(f"💰 {job['salary']}")
                    if job.get("type"):    meta.append(f"📋 {job['type']}")
                    if job.get("posted"):  meta.append(f"📅 {job['posted']}")
                    meta.append(f"🌐 {job['source']}")
                    st.markdown("  |  ".join(meta))
                    st.markdown("---")
                    desc = job["description"]
                    st.markdown(desc[:600] + ("..." if len(desc) > 600 else ""))
                with c_right:
                    st.metric("Match Score", f"{score}%")
                    st.progress(score / 100)
                    if bkdn:
                        st.caption(
                            f"Skill: {bkdn.get('skill_overlap',0)}pt  "
                            f"Title: {bkdn.get('title_match',0)}pt  "
                            f"Freq: {bkdn.get('freq_bonus',0)}pt"
                        )
                    if job.get("matched_skills"):
                        st.markdown("**✅ Matched:**")
                        st.markdown("  ".join(f"`{s}`" for s in job["matched_skills"][:8]))
                    if job.get("missing_skills"):
                        st.markdown("**❌ Missing:**")
                        st.markdown("  ".join(f"`{s}`" for s in job["missing_skills"][:6]))

                b1, b2, b3 = st.columns(3)
                with b1:
                    if job.get("url"):
                        st.link_button("🚀 Apply Now", job["url"], use_container_width=True)
                with b2:
                    if groq_client:
                        if st.button("✍️ Cover Letter", key=f"cl_{i}", use_container_width=True):
                            with st.spinner("Writing..."):
                                st.session_state[f"cl_{i}"] = ai_cover_letter(groq_client, resume_data, job)
                    else:
                        st.caption("Add Groq key for AI")
                with b3:
                    if groq_client:
                        if st.button("🎯 Interview Prep", key=f"ip_{i}", use_container_width=True):
                            with st.spinner("Preparing..."):
                                st.session_state[f"ip_{i}"] = ai_interview_prep(groq_client, job, resume_data)

                if st.session_state.get(f"cl_{i}"):
                    st.divider()
                    st.markdown("**✍️ Cover Letter**")
                    st.markdown(st.session_state[f"cl_{i}"])
                    st.download_button("⬇️ Save", data=st.session_state[f"cl_{i}"],
                                       file_name=f"cover_{job['company'].replace(' ','_')}.txt",
                                       mime="text/plain", key=f"dl_cl_{i}")
                if st.session_state.get(f"ip_{i}"):
                    st.divider()
                    st.markdown("**🎯 Interview Questions**")
                    st.markdown(st.session_state[f"ip_{i}"])
    elif not st.session_state.get("jobs_loaded"):
        st.info("👆 Click **Fetch Jobs** to find live matches for your profile.")

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Skill Gap Analysis")
    render_skill_gap(resume_data, st.session_state.get("ranked_jobs", []))
    ranked_for_gap = st.session_state.get("ranked_jobs", [])
    if ranked_for_gap and groq_client:
        st.divider()
        st.subheader("🗺️ 30-60-90 Day Learning Roadmap")
        miss_freq: dict = defaultdict(int)
        for j in ranked_for_gap[:10]:
            for s in j.get("missing_skills", []):
                miss_freq[s] += 1
        top_missing = [s for s, _ in sorted(miss_freq.items(), key=lambda x: x[1], reverse=True)[:8]]
        if top_missing:
            st.info("Top skills to learn: " + "  ".join(f"`{s}`" for s in top_missing[:5]))
        sq = build_smart_query(resume_data)
        target = st.text_input("Target role for roadmap", value=sq, key="roadmap_role")
        if st.button("📅 Generate Roadmap", type="primary", key="roadmap_btn"):
            with st.spinner("Building your personalised roadmap..."):
                st.session_state["roadmap"] = ai_skill_roadmap(groq_client, resume_data, top_missing, target)
        if st.session_state.get("roadmap"):
            st.markdown(st.session_state["roadmap"])
            st.download_button("⬇️ Download Roadmap", data=st.session_state["roadmap"],
                               file_name="learning_roadmap.txt", mime="text/plain", key="dl_roadmap")
    elif not groq_client:
        st.info("Add your free Groq API key in the sidebar to generate a personalised learning roadmap.")

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("🤖 AI Career Coach")
    if not groq_client:
        st.warning("⚠️ Add your **Groq API key** in the sidebar to unlock AI features.")
        st.markdown("""
**Get a free Groq key in 60 seconds:**
1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign up (no credit card)
3. API Keys → Create API Key
4. Paste in the sidebar

Model: `llama-3.3-70b-versatile` — free, fast, powerful.
        """)
    else:
        st.markdown("### 📝 Resume Review")
        r1, r2 = st.columns([1, 1])
        with r1:
            if st.button("🔍 Get AI Feedback", type="primary", key="tips_btn"):
                with st.spinner("Analysing..."):
                    st.session_state["resume_tips"] = ai_resume_tips(groq_client, resume_data, completeness)
        with r2:
            if st.session_state.get("resume_tips"):
                st.download_button("⬇️ Save Feedback", data=st.session_state["resume_tips"],
                                   file_name="resume_feedback.txt", mime="text/plain", key="dl_tips")
        if st.session_state.get("resume_tips"):
            st.markdown(st.session_state["resume_tips"])

        st.divider()
        st.markdown("### 💬 Career Coach Chat")
        st.caption("Ask about interviews, salary negotiation, career transitions, skill advice...")

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask your career coach..."):
            st.session_state["chat_history"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            skills_ctx = ", ".join(resume_data.get("all_skills_flat", [])[:15])
            domain_ctx, _, _ = detect_domain(set(s.lower() for s in resume_data.get("all_skills_flat", [])))
            try:
                msgs = [{"role": "system", "content":
                         f"You are an expert career coach. User profile: Domain: {domain_ctx}, "
                         f"Experience: {resume_data.get('years_experience','Fresher')}, "
                         f"Skills: {skills_ctx}. Be honest, specific, practical."}]
                msgs += [{"role": m["role"], "content": m["content"]}
                         for m in st.session_state["chat_history"]]
                resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile", messages=msgs,
                    max_tokens=600, temperature=0.7)
                reply = resp.choices[0].message.content.strip()
            except Exception as e:
                reply = f"⚠️ {e}"
            st.session_state["chat_history"].append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)

        if st.session_state.get("chat_history"):
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state["chat_history"] = []
                st.rerun()

# ── TAB 5 ─────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("📦 Export Everything")
    ranked_jobs = st.session_state.get("ranked_jobs", [])
    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("#### Resume Data (JSON)")
        export_resume = {
            "contact": resume_data["contact"], "skills": resume_data["skills"],
            "education": resume_data["education"], "job_titles": resume_data["job_titles"],
            "summary": resume_data["summary"], "years_experience": resume_data["years_experience"],
            "resume_score": completeness.get("overall", 0),
            "completeness": completeness.get("scores", {}),
            "stats": {"total_skills": resume_data["total_skills"],
                      "word_count": resume_data["word_count"],
                      "ats_keywords": completeness.get("ats_words", 0),
                      "skill_categories": len(resume_data["skills"])},
        }
        st.download_button("⬇️ Download Resume JSON", data=json.dumps(export_resume, indent=2),
                           file_name="resume_data.json", mime="application/json",
                           use_container_width=True)
        with st.expander("Preview"):
            st.json(export_resume)

    with col_e2:
        st.markdown("#### Job Matches (JSON)")
        if ranked_jobs:
            export_jobs = [
                {"rank": i+1, "title": j["title"], "company": j["company"],
                 "location": j["location"], "match_score": j["score"],
                 "score_breakdown": j.get("score_breakdown", {}),
                 "matched_skills": j["matched_skills"], "missing_skills": j["missing_skills"],
                 "salary": j.get("salary",""), "url": j["url"], "source": j["source"]}
                for i, j in enumerate(ranked_jobs[:top_k])
            ]
            st.download_button("⬇️ Download Job Matches JSON", data=json.dumps(export_jobs, indent=2),
                               file_name="job_matches.json", mime="application/json",
                               use_container_width=True)
            with st.expander("Preview top 3"):
                st.json(export_jobs[:3])
        else:
            st.info("Fetch jobs first in the Job Matches tab.")

    st.divider()
    st.markdown("#### 📄 Full Report (Markdown)")
    if st.button("Generate Full Report", use_container_width=True, key="gen_report"):
        name = resume_data["contact"].get("name", "Candidate")
        lines = [f"# HireMind Report — {name}",
                 f"Resume Score: {completeness.get('overall',0)}/100", "",
                 "## Profile",
                 f"- Experience: {resume_data['years_experience']}",
                 f"- Total Skills: {resume_data['total_skills']}",
                 f"- ATS Keywords: {completeness.get('ats_words',0)}", "", "## Skills"]
        for cat, skills in resume_data["skills"].items():
            lines += [f"### {cat}", ", ".join(skills), ""]
        if completeness.get("tips"):
            lines += ["## Improvement Tips", ""] + [f"- {t}" for t in completeness["tips"]] + [""]
        if ranked_jobs:
            lines += ["## Top Job Matches", ""]
            for i, j in enumerate(ranked_jobs[:5]):
                lines += [f"### {i+1}. {j['title']} @ {j['company']} — {j['score']}% match",
                           f"- Location: {j['location']}",
                           f"- Matched: {', '.join(j['matched_skills'][:5])}",
                           f"- Missing: {', '.join(j['missing_skills'][:5])}",
                           f"- Apply: {j['url']}", ""]
        st.session_state["full_report"] = "\n".join(lines)

    if st.session_state.get("full_report"):
        st.download_button("⬇️ Download Full Report (.md)", data=st.session_state["full_report"],
                           file_name="hiremind_report.md", mime="text/markdown",
                           use_container_width=True, key="dl_report")
        with st.expander("Preview"):
            st.markdown(st.session_state["full_report"])

    st.divider()
    st.markdown("#### 📄 Raw Extracted Text")
    st.caption(f"{resume_data['word_count']:,} words · {resume_data['char_count']:,} characters")
    st.text_area("raw", value=raw_text[:5000] + ("…" if len(raw_text) > 5000 else ""),
                 height=260, label_visibility="collapsed", disabled=True)
