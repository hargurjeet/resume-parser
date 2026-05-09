# Resume Parser — Claude Context

## What This Project Does

A PDF resume parsing application. Users upload a PDF resume → text is extracted → Llama 3.3 70B on Fireworks AI parses it into structured JSON → results are displayed in a Streamlit UI. The output is validated against a strict Pydantic schema.

## Stack

- **Backend**: FastAPI (port 8000) + `uvicorn`
- **Frontend**: Streamlit (port 8501)
- **AI**: Fireworks AI, model `accounts/fireworks/models/llama-v3p3-70b-instruct` (Llama 3.3 70B — open-source, ~$0.20/M tokens)
- **Structured output**: `instructor` library with `Mode.JSON` via OpenAI-compatible Fireworks client
- **PDF extraction**: `pdfplumber`
- **Package manager**: `uv` (see `pyproject.toml` + `uv.lock`)
- **Deployment**: Single Docker container (HF Spaces) + GitHub Action for auto-sync

> **Migration note**: Originally used AWS Bedrock (Claude 3.7 Sonnet). Switched to Fireworks AI for cost — Bedrock subscription was unavailable.

## Key Files

| File | Role |
|------|------|
| `app/main.py` | FastAPI app entrypoint, CORS config |
| `app/api/routes.py` | Single POST endpoint `/resume/parse` |
| `app/services/parser.py` | Core logic — `FireworksResumeParser` class |
| `app/models/resume.py` | Pydantic schema for structured output |
| `app/core/config.py` | Settings (Fireworks API key, model ID, base URL) via pydantic-settings |
| `app/utils/pdf.py` | Standalone PDF extraction helper (not wired in — parser has its own method) |
| `streamlit_ui/ui.py` | Streamlit frontend — upload PDF, call API, display results |
| `.streamlit/config.toml` | Disables XSRF + CORS protection — required for file upload on HF Spaces |
| `Dockerfile` | Python 3.10-slim, copies `.streamlit/`, exposes 8000 + 8501 |
| `start.sh` | Starts uvicorn + streamlit with XSRF/CORS flags disabled |
| `README.md` | Contains HF Spaces YAML frontmatter (sdk: docker, app_port: 8501) |
| `.github/workflows/sync-to-hf.yml` | GitHub Action — syncs repo to HF Spaces on every push to main |
| `.env` | Git-ignored — must be created locally with `FIREWORKS_API_KEY` |
| `.gitignore` | Excludes `.env`, `__pycache__`, `.venv`, `.ipynb_checkpoints`, `*.pdf` |
| `uv.lock` | Locked dependency tree for reproducible installs |

## Data Flow

```
POST /resume/parse (PDF upload)
  → save to /tmp/<uuid>.pdf
  → pdfplumber extracts raw text
  → prompt built in FireworksResumeParser._create_prompt()
  → instructor.client.create() sends to Fireworks AI (Llama 3.3 70B)
  → model responds as JSON → instructor validates against ParsedResume
  → parsed result returned as JSON / delete temp file
```

## ParsedResume Schema (app/models/resume.py)

Top-level fields: `full_name`, `email`, `phone`, `location`, `linkedin_url`, `github_url`, `portfolio_url`, `summary`, `current_job_title`, `years_of_experience`

Nested lists: `work_experience` (WorkExperience), `education` (Education), `skills` (Skill), `certifications` (Certification), `projects` (Project), `languages`

Key schema decisions:
- `Project.description` is `Optional[str]` — resumes often list projects by title only
- `instructor.Mode.JSON` used (not TOOLS) for open-source model compatibility
- `Settings` uses `extra="ignore"` so stale shell env vars don't crash startup

## Fireworks AI / Credentials

- API key set via `FIREWORKS_API_KEY` in `.env` (git-ignored — never committed)
- On HF Spaces: set `FIREWORKS_API_KEY` as a Space secret in Settings → Variables and secrets
- Base URL: `https://api.fireworks.ai/inference/v1` (OpenAI-compatible)
- Model: `accounts/fireworks/models/llama-v3p3-70b-instruct` (override via `FIREWORKS_MODEL_ID`)

## Deployment — Hugging Face Spaces

- **Space**: https://huggingface.co/spaces/Hargurjeet/Resume_parser
- **SDK**: Docker (`sdk: docker` in README frontmatter)
- **Exposed port**: 8501 (Streamlit) — only this port is accessible from outside
- **Auto-sync**: `.github/workflows/sync-to-hf.yml` uploads files to HF on every push to `main` using `huggingface_hub.upload_folder()` (REST API, not git — avoids binary file restrictions)
- **Required GitHub secret**: `HF_TOKEN` (Hugging Face write token)
- **Required HF Space secret**: `FIREWORKS_API_KEY`

### HF Spaces known issue — file upload 403
HF Spaces proxies Streamlit traffic. Without config, Streamlit's XSRF protection causes a 403 on PDF upload. Fixed in two places:
1. `.streamlit/config.toml` — `enableXsrfProtection = false`, `enableCORS = false`
2. `start.sh` — passes `--server.enableXsrfProtection false --server.enableCORS false`
The Dockerfile must copy `.streamlit/` (`COPY .streamlit ./.streamlit`) — forgetting this was the original root cause.

## Known Gaps / Notes

- `app/utils/pdf.py` duplicates PDF extraction logic already inside `FireworksResumeParser` — not wired in
- `archieve/` contains prototype Jupyter notebooks and legacy stubs (not production code)
- No tests exist yet
- CORS is wide open (`allow_origins=["*"]`) — tighten for production
- UI is functional but basic — Next.js migration planned for a more polished look (plan exists in `.claude/plans/`)

## Running Locally

```bash
# Install dependencies (first time only)
uv sync

# Create .env file
echo "FIREWORKS_API_KEY=your_key_here" > .env

# Backend (terminal 1)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (terminal 2)
uv run streamlit run streamlit_ui/ui.py --server.port 8501
```

## Docs Folder

See `docs/` for deeper references:
- `docs/architecture.md` — full system design and data flow
- `docs/data-models.md` — all Pydantic models documented
- `docs/api.md` — API endpoint reference
- `docs/setup.md` — local, Docker, and HF Spaces setup guide
