# ⚡ ResumeIQ — Smart Job Recommendation Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

**A DSA-powered resume parser and job recommendation engine built with Streamlit.**  
Upload any PDF resume → extract skills → get matched to jobs.

[🚀 Live Demo](#) · [📖 Docs](#how-it-works) · [🐛 Issues](../../issues)

</div>

---

## ✨ Features

- 📄 **Universal PDF Parser** — handles any resume format: single-column, multi-column, tables, graphics-heavy CVs
- 🔍 **Smart Skill Extraction** — matches 200+ skills across 7 categories using longest-match regex
- 👤 **Contact Info Detection** — name, email, phone, LinkedIn, GitHub, website
- 🎓 **Education Parser** — detects degrees, universities, and qualifications
- 💼 **Role Identification** — infers job titles and seniority from content
- 📊 **Skill Gap Analysis** — visual breakdown of skill categories with frequency scoring
- 📦 **JSON Export** — download parsed resume data as structured JSON
- 🌙 **Beautiful Dark UI** — custom editorial design, zero generic Streamlit defaults

---

## 🗂️ Project Structure

```
resumeiq/
├── resume_parser_app.py   # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🚀 Deploy on Streamlit Cloud (Recommended)

### Step 1 — Push to GitHub

```bash
# Create a new repo on github.com, then:
git init
git add .
git commit -m "🚀 Initial commit — ResumeIQ"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/resumeiq.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Connect your GitHub account
4. Select your repository and set:
   - **Branch:** `main`
   - **Main file path:** `resume_parser_app.py`
5. Click **"Deploy!"**

Streamlit Cloud automatically installs everything from `requirements.txt`. Your app will be live at:
```
https://YOUR_USERNAME-resumeiq-resume-parser-app-XXXX.streamlit.app
```

---

## 💻 Run Locally

### Prerequisites
- Python 3.9 or higher
- pip

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/resumeiq.git
cd resumeiq

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run resume_parser_app.py
```

The app opens automatically at `http://localhost:8501`

---

## 🧠 How It Works

ResumeIQ is intentionally **ML-free** — it uses classical DSA techniques for speed and transparency:

| Component | Technique |
|---|---|
| PDF Extraction | `pdfplumber` with tolerance-tuned text + table parsing |
| Skill Matching | Longest-match regex over a 200+ skill dictionary |
| Contact Extraction | Named regex patterns per field type |
| Education Detection | Degree keyword + institution name patterns |
| Experience Estimation | Date range parsing + explicit mention extraction |
| Skill Ranking | Frequency counting across raw text |

### Skill Categories

| Category | Examples |
|---|---|
| 💻 Languages | Python, JavaScript, Java, Go, Rust, C++ |
| 🌐 Frameworks | React, Django, FastAPI, Spring Boot, Next.js |
| 🧠 AI / ML | TensorFlow, PyTorch, Scikit-learn, LangChain |
| 🗄️ Databases | PostgreSQL, MongoDB, Redis, Snowflake |
| ☁️ Cloud & DevOps | AWS, Docker, Kubernetes, Terraform, CI/CD |
| 🔧 Tools | Git, Kafka, Airflow, Tableau, Figma |
| 🤝 Soft Skills | Leadership, Agile, Scrum, Communication |

---

## 🗺️ Roadmap

- [x] Resume PDF parsing
- [x] Skill extraction (200+ skills)
- [x] Contact & education detection
- [x] Skill gap analysis UI
- [ ] Job dataset integration
- [ ] Job–resume matching with relevance scores
- [ ] Missing skills recommendations
- [ ] Top-K job ranking (DSA-powered)
- [ ] User accounts & resume history

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io)** — UI framework
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — PDF text extraction
- **Python stdlib** — `re`, `json`, `collections` (no heavy ML deps)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.

---

<div align="center">
Built with ⚡ using Streamlit · Part of the Smart Job Recommendation Engine project
</div>
