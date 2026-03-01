import streamlit as st
import pdfplumber
import re
import json
from collections import defaultdict

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ · Smart Job Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark editorial aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0A0A0F !important;
    color: #E8E4DC !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #0A0A0F !important;
}

[data-testid="stHeader"] { background: transparent !important; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0F0F18 !important;
    border-right: 1px solid #1E1E2E !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0A0F; }
::-webkit-scrollbar-thumb { background: #2A2A3E; border-radius: 3px; }

/* ── HERO HEADER ── */
.hero-wrap {
    position: relative;
    padding: 60px 0 40px;
    overflow: hidden;
}
.hero-bg {
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(88,101,242,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    color: #5865F2;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(36px, 5vw, 64px);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: #F0EDE8;
}
.hero-title span {
    color: transparent;
    -webkit-text-stroke: 1.5px #5865F2;
}
.hero-sub {
    font-size: 15px;
    color: #6B6880;
    margin-top: 14px;
    max-width: 500px;
    line-height: 1.6;
}
.hero-line {
    width: 60px; height: 2px;
    background: linear-gradient(90deg, #5865F2, transparent);
    margin: 28px 0;
}

/* ── UPLOAD ZONE ── */
.upload-container {
    border: 1.5px dashed #2A2A40;
    border-radius: 16px;
    padding: 48px 32px;
    text-align: center;
    background: linear-gradient(145deg, #0F0F1A 0%, #12121F 100%);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.upload-container::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(circle at 50% 0%, rgba(88,101,242,0.07) 0%, transparent 60%);
    pointer-events: none;
}
.upload-icon {
    font-size: 40px;
    margin-bottom: 12px;
    display: block;
}
.upload-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #D0CCE0;
    margin-bottom: 6px;
}
.upload-sub { font-size: 13px; color: #4A4760; }

/* ── STREAMLIT FILE UPLOADER OVERRIDE ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    border: 1.5px dashed #2A2A40 !important;
    border-radius: 16px !important;
    background: linear-gradient(145deg, #0F0F1A 0%, #12121F 100%) !important;
    padding: 20px !important;
}
[data-testid="stFileUploader"] label {
    color: #6B6880 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
[data-testid="stFileDropzoneInstructions"] div span {
    color: #5865F2 !important;
    font-weight: 600 !important;
}

/* ── CARDS ── */
.card {
    background: #0F0F1A;
    border: 1px solid #1A1A2E;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(88,101,242,0.4), transparent);
}
.card-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    color: #5865F2;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #F0EDE8;
    margin-bottom: 4px;
}
.card-value {
    font-family: 'DM Mono', monospace;
    font-size: 32px;
    font-weight: 500;
    color: #5865F2;
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3A3750;
    margin: 32px 0 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1A1A2E;
}

/* ── SKILL TAGS ── */
.tag-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.tag {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 12px;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 400;
    border: 1px solid;
    transition: all 0.2s;
}
.tag-tech  { background: rgba(88,101,242,0.1); border-color: rgba(88,101,242,0.3); color: #8B96FF; }
.tag-soft  { background: rgba(34,197,94,0.08);  border-color: rgba(34,197,94,0.25);  color: #6EE7A0; }
.tag-tool  { background: rgba(245,158,11,0.08); border-color: rgba(245,158,11,0.25); color: #FCD34D; }
.tag-lang  { background: rgba(239,68,68,0.08);  border-color: rgba(239,68,68,0.25);  color: #FCA5A5; }
.tag-edu   { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.25); color: #C4B5FD; }

/* ── INFO GRID ── */
.info-row {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid #141420;
}
.info-row:last-child { border-bottom: none; }
.info-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    background: #14142A;
    border: 1px solid #1E1E3A;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}
.info-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3A3750;
    margin-bottom: 2px;
}
.info-value {
    font-size: 14px;
    color: #C0BCCC;
    line-height: 1.4;
}

/* ── EXPERIENCE TIMELINE ── */
.exp-item {
    position: relative;
    padding-left: 24px;
    padding-bottom: 24px;
}
.exp-item::before {
    content: '';
    position: absolute;
    left: 6px; top: 8px; bottom: 0;
    width: 1px;
    background: linear-gradient(180deg, #5865F2 0%, transparent 100%);
}
.exp-dot {
    position: absolute;
    left: 0; top: 6px;
    width: 13px; height: 13px;
    border-radius: 50%;
    background: #0A0A0F;
    border: 2px solid #5865F2;
    box-shadow: 0 0 8px rgba(88,101,242,0.5);
}
.exp-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #E8E4DC;
    margin-bottom: 2px;
}
.exp-company {
    font-size: 13px;
    color: #5865F2;
    margin-bottom: 2px;
}
.exp-date {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #3A3750;
    margin-bottom: 6px;
}
.exp-desc {
    font-size: 13px;
    color: #6B6880;
    line-height: 1.6;
}

/* ── PROGRESS BAR ── */
.skill-bar-wrap { margin: 8px 0; }
.skill-bar-label {
    display: flex; justify-content: space-between;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #6B6880;
    margin-bottom: 4px;
}
.skill-bar-bg {
    height: 4px;
    background: #1A1A2E;
    border-radius: 2px;
    overflow: hidden;
}
.skill-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #5865F2, #8B96FF);
    transition: width 1s ease;
}

/* ── RAW TEXT BLOCK ── */
.raw-text {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #3A3750;
    background: #08080E;
    border: 1px solid #141420;
    border-radius: 10px;
    padding: 16px;
    max-height: 200px;
    overflow-y: auto;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.03em !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(88,101,242,0.4) !important;
}

/* ── STREAMLIT OVERRIDES ── */
.stSpinner > div { border-top-color: #5865F2 !important; }
[data-testid="stMetric"] {
    background: #0F0F1A !important;
    border: 1px solid #1A1A2E !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    color: #3A3750 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    color: #5865F2 !important;
    font-size: 28px !important;
}
[data-testid="stExpander"] {
    background: #0F0F1A !important;
    border: 1px solid #1A1A2E !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: #D0CCE0 !important;
}

/* ── TABS ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    color: #4A4760 !important;
    border-radius: 6px 6px 0 0 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #5865F2 !important;
    border-bottom: 2px solid #5865F2 !important;
}
[data-testid="stTabsContent"] {
    background: transparent !important;
    border: none !important;
}

/* ── DIVIDER ── */
hr { border-color: #141420 !important; }

/* ── SUCCESS / INFO MESSAGES ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid !important;
}

.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    color: #6EE7A0;
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22C55E;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}
.stat-box {
    background: #0F0F1A;
    border: 1px solid #1A1A2E;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #5865F2;
    line-height: 1;
}
.stat-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #3A3750;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SKILL DATABASE
# ─────────────────────────────────────────────
SKILL_DB = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
        "rust", "swift", "kotlin", "ruby", "php", "scala", "r", "matlab", "perl",
        "bash", "shell", "powershell", "dart", "haskell", "lua", "julia", "elixir",
        "clojure", "groovy", "vba", "cobol", "fortran", "assembly",
    ],
    "web_frameworks": [
        "react", "angular", "vue", "next.js", "nuxt.js", "svelte", "django",
        "flask", "fastapi", "spring", "spring boot", "express", "node.js",
        "rails", "laravel", "asp.net", ".net", "blazor", "gatsby", "remix",
        "nestjs", "hapi", "koa", "tornado", "pyramid", "bottle",
    ],
    "data_ml": [
        "machine learning", "deep learning", "neural networks", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "xgboost",
        "lightgbm", "catboost", "pandas", "numpy", "scipy", "matplotlib",
        "seaborn", "plotly", "hugging face", "transformers", "langchain",
        "openai", "llm", "generative ai", "reinforcement learning", "cnn", "rnn", "lstm",
        "bert", "gpt", "stable diffusion", "mlops", "feature engineering",
    ],
    "databases": [
        "sql", "mysql", "postgresql", "postgres", "sqlite", "oracle", "mssql",
        "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "neo4j",
        "firebase", "supabase", "cockroachdb", "snowflake", "bigquery", "redshift",
        "pinecone", "chroma", "weaviate", "nosql",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "github actions", "gitlab ci", "circleci",
        "helm", "prometheus", "grafana", "nginx", "apache", "linux", "ubuntu",
        "devops", "ci/cd", "microservices", "serverless", "lambda", "ec2", "s3",
        "cloudformation", "pulumi", "vagrant", "packer",
    ],
    "tools_platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
        "figma", "adobe", "postman", "swagger", "graphql", "rest api", "grpc",
        "kafka", "rabbitmq", "celery", "airflow", "spark", "hadoop", "dbt",
        "tableau", "power bi", "looker", "excel", "jupyter", "vscode", "intellij",
        "streamlit", "gradio", "vercel", "netlify", "heroku",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving", "critical thinking",
        "project management", "agile", "scrum", "kanban", "collaboration", "mentoring",
        "time management", "analytical", "research", "presentation", "negotiation",
        "stakeholder management", "strategic thinking", "decision making",
    ],
}

# Flat lookup for quick matching
FLAT_SKILLS = {}
for category, skills in SKILL_DB.items():
    for skill in skills:
        FLAT_SKILLS[skill.lower()] = category


SECTION_PATTERNS = {
    "experience": r"(work\s+experience|professional\s+experience|employment|experience|career\s+history|work\s+history)",
    "education": r"(education|academic|qualification|degree|university|college|school)",
    "skills": r"(skills|technical\s+skills|core\s+competencies|technologies|expertise|proficiencies)",
    "projects": r"(projects|personal\s+projects|key\s+projects|notable\s+projects|portfolio)",
    "certifications": r"(certification|certificates|licenses|credentials|awards)",
    "summary": r"(summary|profile|objective|about\s+me|overview|executive\s+summary|professional\s+summary)",
}

CONTACT_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
    "phone": r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}",
    "linkedin": r"(?:linkedin\.com/in/|linkedin:\s*)([A-Za-z0-9\-_/]+)",
    "github": r"(?:github\.com/|github:\s*)([A-Za-z0-9\-_]+)",
    "website": r"https?://(?!linkedin|github)[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+",
}


# ─────────────────────────────────────────────
# PARSING ENGINE
# ─────────────────────────────────────────────

def extract_text_from_pdf(pdf_file) -> str:
    text_parts = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if page_text:
                    text_parts.append(page_text)
                # Also try table extraction
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            row_text = " | ".join([str(c) for c in row if c])
                            text_parts.append(row_text)
    except Exception as e:
        return ""
    return "\n".join(text_parts)


def extract_contact_info(text: str) -> dict:
    contact = {}
    for key, pattern in CONTACT_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            contact[key] = matches[0] if isinstance(matches[0], str) else matches[0]
    
    # Extract name (usually first non-empty line)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first = lines[0]
        # Name heuristic: 2-4 words, no special chars, title case
        words = first.split()
        if 2 <= len(words) <= 4 and all(w.replace('.', '').isalpha() for w in words):
            contact['name'] = first
        elif len(lines) > 1:
            second = lines[1]
            words2 = second.split()
            if 2 <= len(words2) <= 4 and all(w.replace('.', '').isalpha() for w in words2):
                contact['name'] = second
    
    return contact


def extract_skills(text: str) -> dict:
    text_lower = text.lower()
    found = defaultdict(list)
    
    # Sort by length descending to match longer phrases first
    sorted_skills = sorted(FLAT_SKILLS.keys(), key=len, reverse=True)
    matched = set()
    
    for skill in sorted_skills:
        if skill in matched:
            continue
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            category = FLAT_SKILLS[skill]
            found[category].append(skill)
            matched.add(skill)
    
    return dict(found)


def extract_education(text: str) -> list:
    education = []
    degree_patterns = [
        r"(B\.?Tech|B\.?E\.?|Bachelor|B\.?Sc?|B\.?A\.?|M\.?Tech|M\.?E\.?|Master|M\.?Sc?|M\.?A\.?|PhD|Ph\.D|MBA|BBA|Diploma|Associate)[^\n]{0,80}",
    ]
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) > 5:
                education.append(match.strip())
    
    # Also extract university/college names
    uni_pattern = r"(?:University|College|Institute|School|Academy)\s+of\s+[A-Z][A-Za-z\s,]+"
    uni_matches = re.findall(uni_pattern, text)
    education.extend(uni_matches[:3])
    
    return list(dict.fromkeys(education))[:6]


def extract_years_experience(text: str) -> str:
    patterns = [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+)\+?\s*years?",
        r"(\d+)\+?\s*yrs?\s+(?:of\s+)?experience",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1) + "+ years"
    
    # Count date ranges
    date_pattern = r"(20\d{2}|19\d{2})\s*[-–—]\s*(20\d{2}|Present|Current|Now)"
    dates = re.findall(date_pattern, text, re.IGNORECASE)
    if dates:
        years = set()
        for start, end in dates:
            try:
                s = int(start)
                e = 2024 if end.isalpha() else int(end)
                for y in range(s, e + 1):
                    years.add(y)
            except:
                pass
        if years:
            total = max(years) - min(years)
            if total > 0:
                return f"~{total} years"
    return "N/A"


def extract_job_titles(text: str) -> list:
    title_keywords = [
        "engineer", "developer", "designer", "manager", "analyst", "architect",
        "scientist", "consultant", "lead", "director", "specialist", "intern",
        "researcher", "administrator", "coordinator", "head of", "vp of",
        "chief", "officer", "associate", "senior", "junior", "principal",
    ]
    lines = text.split('\n')
    titles = []
    for line in lines:
        line = line.strip()
        if 3 < len(line) < 60:
            lower = line.lower()
            if any(kw in lower for kw in title_keywords):
                if not re.search(r'\d{4}', line):  # skip lines with years
                    titles.append(line)
    return list(dict.fromkeys(titles))[:5]


def _is_section_header(line: str) -> bool:
    """Check if a line matches any known section header pattern."""
    for pattern in SECTION_PATTERNS.values():
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def extract_summary(text: str) -> str:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    # Look for summary section
    for i, line in enumerate(lines):
        if re.search(SECTION_PATTERNS["summary"], line, re.IGNORECASE):
            chunk = []
            for j in range(i+1, min(i+8, len(lines))):
                if _is_section_header(lines[j]):
                    break
                chunk.append(lines[j])
            if chunk:
                return ' '.join(chunk)[:500]

    # Fallback: find longest paragraph-like section near top
    for line in lines[:20]:
        if len(line) > 80 and not re.search(r'[@|\d{4}]', line[:10]):
            return line[:400]
    return ""


def parse_resume(text: str) -> dict:
    return {
        "contact": extract_contact_info(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "years_experience": extract_years_experience(text),
        "job_titles": extract_job_titles(text),
        "summary": extract_summary(text),
        "total_skills": sum(len(v) for v in extract_skills(text).values()),
        "word_count": len(text.split()),
        "char_count": len(text),
    }


# ─────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────

CATEGORY_META = {
    "programming_languages": ("💻", "Languages",     "tag-lang"),
    "web_frameworks":        ("🌐", "Frameworks",    "tag-tech"),
    "data_ml":               ("🧠", "AI / ML",       "tag-tool"),
    "databases":             ("🗄️", "Databases",     "tag-edu"),
    "cloud_devops":          ("☁️", "Cloud & DevOps","tag-tech"),
    "tools_platforms":       ("🔧", "Tools",         "tag-tool"),
    "soft_skills":           ("🤝", "Soft Skills",   "tag-soft"),
}

def render_tags(skills: list, cls: str) -> str:
    return "".join(f'<span class="tag {cls}">{s}</span>' for s in skills)

def render_skill_section(skills_dict: dict) -> str:
    html = ""
    for cat, skills in skills_dict.items():
        if not skills:
            continue
        icon, label, cls = CATEGORY_META.get(cat, ("•", cat, "tag-tech"))
        html += f'<div class="section-header">{icon} {label}</div>'
        html += f'<div class="tag-wrap">{render_tags(skills, cls)}</div>'
    return html


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

# HERO
st.markdown("""
<div class="hero-wrap">
  <div class="hero-bg"></div>
  <div class="hero-eyebrow">⚡ v1.0 · Smart Job Recommendation Engine</div>
  <div class="hero-title">Resume<span>IQ</span></div>
  <div class="hero-sub">Upload any resume or CV. Extract skills, experience, and insights instantly — no templates, no limits.</div>
  <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)


# MAIN LAYOUT
col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown('<div class="section-header">📁 Upload Resume</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drag & drop or click to browse",
        type=["pdf"],
        help="Supports any PDF resume format — single column, multi-column, tables, graphics",
        label_visibility="collapsed",
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin:12px 0;">
          <div class="status-badge">
            <div class="status-dot"></div>
            File loaded
          </div>
          <span style="font-family:'DM Mono',monospace; font-size:11px; color:#3A3750;">{uploaded_file.name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📝 Or paste text</div>', unsafe_allow_html=True)
    manual_text = st.text_area(
        "Paste resume content",
        height=180,
        placeholder="Paste your resume text here if you don't have a PDF...",
        label_visibility="collapsed",
    )
    
    analyze_btn = st.button("⚡  Analyze Resume", use_container_width=True)


with col_right:
    if not uploaded_file and not manual_text:
        st.markdown("""
        <div class="card" style="text-align:center; padding:48px 24px;">
          <div style="font-size:48px; margin-bottom:16px;">🔍</div>
          <div class="card-title" style="font-size:18px;">Waiting for input</div>
          <div style="color:#3A3750; font-size:13px; margin-top:8px;">Upload a PDF or paste resume text to see the magic happen.</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────
if analyze_btn and (uploaded_file or manual_text):
    with st.spinner("Parsing resume…"):
        if uploaded_file:
            raw_text = extract_text_from_pdf(uploaded_file)
        else:
            raw_text = manual_text
        
        if not raw_text.strip():
            st.error("⚠️ Could not extract text from the file. Try pasting the content manually.")
            st.stop()
        
        data = parse_resume(raw_text)
    
    # ── STAT ROW ──
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Skills Found", data["total_skills"])
    with m2:
        st.metric("Experience", data["years_experience"])
    with m3:
        st.metric("Skill Categories", len(data["skills"]))
    with m4:
        st.metric("Resume Words", data["word_count"])
    
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    
    # ── TABS ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤  Profile", "🔧  Skills", "📊  Analysis", "📄  Raw Text"
    ])
    
    # ── TAB 1: PROFILE ──
    with tab1:
        c1, c2 = st.columns([1, 1], gap="medium")
        
        with c1:
            contact = data["contact"]
            st.markdown('<div class="card-label">Contact & Identity</div>', unsafe_allow_html=True)
            
            info_html = '<div class="card">'
            fields = [
                ("👤", "Name",     contact.get("name", "—")),
                ("✉️", "Email",    contact.get("email", "—")),
                ("📞", "Phone",    contact.get("phone", "—")),
                ("🔗", "LinkedIn", contact.get("linkedin", "—")),
                ("🐙", "GitHub",   contact.get("github", "—")),
                ("🌐", "Website",  contact.get("website", "—")),
            ]
            for icon, label, val in fields:
                info_html += f"""
                <div class="info-row">
                  <div class="info-icon">{icon}</div>
                  <div>
                    <div class="info-label">{label}</div>
                    <div class="info-value">{val}</div>
                  </div>
                </div>"""
            info_html += '</div>'
            st.markdown(info_html, unsafe_allow_html=True)
        
        with c2:
            if data["summary"]:
                st.markdown('<div class="card-label">Professional Summary</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="card">
                  <div style="font-size:14px; color:#9A96A6; line-height:1.7; font-style:italic;">
                    "{data['summary']}"
                  </div>
                </div>
                """, unsafe_allow_html=True)
            
            if data["job_titles"]:
                st.markdown('<div class="card-label" style="margin-top:16px;">Detected Roles</div>', unsafe_allow_html=True)
                titles_html = '<div class="tag-wrap">'
                for t in data["job_titles"]:
                    titles_html += f'<span class="tag tag-tech">💼 {t}</span>'
                titles_html += '</div>'
                st.markdown(titles_html, unsafe_allow_html=True)
            
            if data["education"]:
                st.markdown('<div class="card-label" style="margin-top:20px;">Education</div>', unsafe_allow_html=True)
                edu_html = '<div class="card">'
                for edu in data["education"][:4]:
                    edu_html += f'<div class="info-row"><div class="info-icon">🎓</div><div class="info-value">{edu}</div></div>'
                edu_html += '</div>'
                st.markdown(edu_html, unsafe_allow_html=True)
    
    # ── TAB 2: SKILLS ──
    with tab2:
        if data["skills"]:
            skills_html = render_skill_section(data["skills"])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("No skills matched in the database. Try adding more content to your resume.")
    
    # ── TAB 3: ANALYSIS ──
    with tab3:
        st.markdown('<div class="card-label">Skill Category Breakdown</div>', unsafe_allow_html=True)
        
        if data["skills"]:
            bar_html = '<div class="card">'
            total = max(sum(len(v) for v in data["skills"].values()), 1)
            for cat, skills in sorted(data["skills"].items(), key=lambda x: len(x[1]), reverse=True):
                icon, label, _ = CATEGORY_META.get(cat, ("•", cat, ""))
                pct = round(len(skills) / total * 100)
                bar_html += f"""
                <div class="skill-bar-wrap">
                  <div class="skill-bar-label">
                    <span>{icon} {label}</span>
                    <span>{len(skills)} skills · {pct}%</span>
                  </div>
                  <div class="skill-bar-bg">
                    <div class="skill-bar-fill" style="width:{pct}%"></div>
                  </div>
                </div>"""
            bar_html += '</div>'
            st.markdown(bar_html, unsafe_allow_html=True)
        
        # Top skills by frequency in text
        st.markdown('<div class="card-label" style="margin-top:20px;">Top Mentioned Skills</div>', unsafe_allow_html=True)
        all_skills = [s for skills in data["skills"].values() for s in skills]
        freq = {}
        text_lower = raw_text.lower()
        for s in all_skills:
            freq[s] = len(re.findall(r'\b' + re.escape(s) + r'\b', text_lower))
        
        top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:12]
        if top:
            freq_html = '<div class="card"><div class="tag-wrap">'
            for skill, count in top:
                cat = FLAT_SKILLS.get(skill, "tools_platforms")
                _, _, cls = CATEGORY_META.get(cat, ("•", cat, "tag-tech"))
                freq_html += f'<span class="tag {cls}">{skill} <span style="opacity:0.5">×{count}</span></span>'
            freq_html += '</div></div>'
            st.markdown(freq_html, unsafe_allow_html=True)
        
        # JSON export
        with st.expander("📦  Export parsed data as JSON"):
            export = {
                "contact": data["contact"],
                "skills": data["skills"],
                "education": data["education"],
                "job_titles": data["job_titles"],
                "summary": data["summary"],
                "years_experience": data["years_experience"],
                "stats": {
                    "total_skills": data["total_skills"],
                    "word_count": data["word_count"],
                    "skill_categories": len(data["skills"]),
                },
            }
            st.code(json.dumps(export, indent=2), language="json")
    
    # ── TAB 4: RAW TEXT ──
    with tab4:
        st.markdown('<div class="card-label">Extracted Raw Text</div>', unsafe_allow_html=True)
        preview = raw_text[:3000] + ("…" if len(raw_text) > 3000 else "")
        st.markdown(f'<div class="raw-text">{preview}</div>', unsafe_allow_html=True)
        st.caption(f"Total characters: {data['char_count']:,} · Words: {data['word_count']:,}")

elif analyze_btn:
    st.warning("Please upload a PDF or paste resume text before analyzing.")
