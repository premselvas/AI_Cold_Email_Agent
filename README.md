# AI Cold Email Agent 📧

A production-ready AI-powered cold email agent that automates the process of generating and sending personalized cold emails for job applications. Upload your resume, add a job description, and let the agent analyze fit, research the company, and draft a tailored outreach email — ready to send straight from Gmail.

## Features

- 📄 **Resume parsing** — extracts text and structured info (skills, contact details) from PDF resumes
- 🔍 **Job description parsing** — paste raw text or fetch and clean a job posting directly from a URL
- 📊 **ATS score analysis** — scores resume-to-JD match using AI
- 🏢 **Company research** — gathers context on the target company to personalize outreach
- 🤖 **AI-powered email generation** — drafts cold emails using Groq's Llama 3.3 70B model
- 📧 **Gmail integration** — sends emails directly via the Gmail API (OAuth2), with attachment support
- 📥 **Bulk outreach** — parse an Excel/CSV list of companies, roles, and HR emails for batch campaigns
- 💾 **SQLite database** — tracks sent email history
- 🎨 **Streamlit dashboard** — a guided, step-by-step UI for the whole workflow

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12+ |
| Frontend | Streamlit |
| AI | Groq API (Llama-3.3-70B-Versatile) |
| Database | SQLite |
| Email | Gmail API (OAuth2) |
| Parsing | pdfplumber, BeautifulSoup4, trafilatura, pandas |

## Project Structure

```
AI_Cold_Email_Agent/
├── app.py                     # Streamlit application entry point
├── config.py                  # Central configuration (env vars, paths, settings)
├── agents/
│   ├── ats_matcher.py         # ATS match scoring between resume & job description
│   ├── company_research.py    # AI-driven company research for personalization
│   ├── email_writer.py        # AI cold email generation
│   ├── job_parser.py          # Wrapper agent for job description extraction
│   ├── resume_analyzer.py     # Wrapper agent for resume analysis
│   └── sender.py              # Generic email-dispatch agent
├── parser/
│   ├── resume_parser.py       # PDF resume text extraction
│   ├── resume_info.py         # Structured info/skills extraction from resume text
│   ├── jd_parser.py           # Job description parsing from URL or text
│   └── excel_parser.py        # Bulk outreach list parsing (Excel/CSV)
├── gmail/
│   ├── gmail_auth.py          # Google OAuth2 credential handling
│   ├── gmail_send.py          # Low-level Gmail API send logic
│   └── gmail_sender.py        # Sender class wrapper
├── database/
│   └── database.py            # SQLite email history manager
├── utils/
│   ├── logger.py              # Logging setup
│   ├── validators.py          # Email/URL validation helpers
│   └── helpers.py             # File download / format conversion helpers
└── data/
    └── sample_hr_list.xlsx    # Sample bulk-outreach template
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/premselvas/AI_Cold_Email_Agent.git
cd AI_Cold_Email_Agent
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

The repo doesn't currently ship a `requirements.txt`, so install the packages the app imports directly:

```bash
pip install streamlit pandas python-dotenv groq pdfplumber trafilatura beautifulsoup4 requests \
            google-auth google-auth-oauthlib google-api-python-client python-docx openpyxl
```

> Tip: once installed, freeze them for next time with `pip freeze > requirements.txt`.

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Groq API
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Gmail API (OAuth2)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
GMAIL_ACCESS_TOKEN=your_gmail_access_token

# Database (optional override)
DATABASE_PATH=data/email_agent.db
```

- Get a Groq API key from [console.groq.com](https://console.groq.com).
- Get Gmail OAuth2 credentials from the [Google Cloud Console](https://console.cloud.google.com/) (enable the Gmail API, create OAuth client credentials with the `gmail.send` scope).

### 5. Run the app

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

## Usage

1. **Upload your resume** (PDF) — the app extracts your skills and profile automatically.
2. **Add a job description** — paste text directly or provide a job posting URL.
3. **Review your ATS match score** — see how well your resume aligns with the JD.
4. **Let the agent research the company** and generate a personalized cold email.
5. **Send it via Gmail**, or download it as text/DOCX.
6. For outreach at scale, upload an Excel/CSV list (`company_name`, `role`, `hr_email`, `job_description` columns) to generate and send emails in bulk.
7. Check **email history** in the sidebar, backed by the SQLite database.

## Notes

- `.env`, OAuth tokens (`token.json`, `credentials.json`), and local databases are already excluded via `.gitignore` — never commit real credentials.
- `Config.validate_config()` in `config.py` flags a missing/placeholder `GROQ_API_KEY` at startup.

## License

No license file is currently included in this repository. Add one (e.g. MIT) if you intend for others to reuse this code.
