import streamlit as st
import pdfplumber
import re
import json
from collections import defaultdict

st.set_page_config(page_title="ResumeIQ", page_icon="⚡", layout="centered")

# ─────────────────────────────────────────────
# SKILL DATABASE
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# PARSING ENGINE
# ─────────────────────────────────────────────

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
                end = 2024 if e.isalpha() else int(e)
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
    }

# ─────────────────────────────────────────────
# APP UI
# ─────────────────────────────────────────────

st.title("⚡ ResumeIQ")
st.caption("Upload any PDF resume to extract skills, experience, and insights instantly.")
st.divider()

# INPUT
uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

with st.expander("✏️ Or paste resume text instead"):
    manual_text = st.text_area("Paste your resume here", height=200, label_visibility="collapsed")

st.button("Analyze Resume", type="primary", use_container_width=True, key="analyze")

# ANALYSIS
if st.session_state.get("analyze"):
    if not uploaded_file and not (manual_text and manual_text.strip()):
        st.warning("Please upload a PDF or paste resume text first.")
        st.stop()

    with st.spinner("Parsing your resume..."):
        raw_text = extract_text_from_pdf(uploaded_file) if uploaded_file else manual_text
        if not raw_text.strip():
            st.error("Could not extract text. Try pasting the content manually.")
            st.stop()
        data = parse_resume(raw_text)

    st.success(f"✅ Resume parsed successfully — {data['total_skills']} skills found across {len(data['skills'])} categories.")
    st.divider()

    # METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Skills Found",     data["total_skills"])
    c2.metric("Experience",       data["years_experience"])
    c3.metric("Categories",       len(data["skills"]))
    c4.metric("Words",            data["word_count"])

    st.divider()

    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔧 Skills", "📊 Analysis", "📄 Raw Text"])

    # TAB 1 — PROFILE
    with tab1:
        contact = data["contact"]
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Contact Info")
            for label, key in [("Name","name"),("Email","email"),("Phone","phone"),
                                ("LinkedIn","linkedin"),("GitHub","github"),("Website","website")]:
                val = contact.get(key)
                if val:
                    st.text_input(label, value=val, disabled=True)

        with col_b:
            if data["summary"]:
                st.subheader("Summary")
                st.info(data["summary"])
            if data["job_titles"]:
                st.subheader("Detected Roles")
                for t in data["job_titles"]:
                    st.markdown(f"- {t}")

        if data["education"]:
            st.subheader("Education")
            for edu in data["education"]:
                st.markdown(f"🎓 {edu}")

    # TAB 2 — SKILLS
    with tab2:
        if data["skills"]:
            for category, skills in data["skills"].items():
                with st.expander(f"{category}  ·  {len(skills)} skills", expanded=True):
                    st.markdown("  ".join([f"`{s}`" for s in skills]))
        else:
            st.info("No skills matched. Try adding more detail to your resume.")

    # TAB 3 — ANALYSIS
    with tab3:
        if data["skills"]:
            st.subheader("Skill Breakdown")
            total = max(sum(len(v) for v in data["skills"].values()), 1)
            for cat, skills in sorted(data["skills"].items(), key=lambda x: len(x[1]), reverse=True):
                pct = round(len(skills) / total * 100)
                st.markdown(f"**{cat}** &nbsp; `{len(skills)} skills`")
                st.progress(pct / 100)
                st.write("")

            st.subheader("Top Mentioned Skills")
            text_lower = raw_text.lower()
            freq = {
                s: len(re.findall(r"\b" + re.escape(s) + r"\b", text_lower))
                for skills in data["skills"].values()
                for s in skills
            }
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            if top:
                col1, col2 = st.columns(2)
                for i, (skill, count) in enumerate(top):
                    (col1 if i % 2 == 0 else col2).markdown(f"**{skill}** — {count}×")

        st.divider()
        st.subheader("Export Data")
        export = {
            "contact":          data["contact"],
            "skills":           data["skills"],
            "education":        data["education"],
            "job_titles":       data["job_titles"],
            "summary":          data["summary"],
            "years_experience": data["years_experience"],
            "stats": {
                "total_skills":     data["total_skills"],
                "word_count":       data["word_count"],
                "skill_categories": len(data["skills"]),
            },
        }
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(export, indent=2),
            file_name="resume_data.json",
            mime="application/json",
            use_container_width=True,
        )
        with st.expander("Preview JSON"):
            st.json(export)

    # TAB 4 — RAW TEXT
    with tab4:
        st.subheader("Extracted Text")
        st.caption(f"{data['word_count']:,} words · {data['char_count']:,} characters")
        st.text_area(
            "raw",
            value=raw_text[:5000] + ("…" if len(raw_text) > 5000 else ""),
            height=400,
            label_visibility="collapsed",
            disabled=True,
        )
