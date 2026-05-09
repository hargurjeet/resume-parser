# Architecture

## System Overview

```
User (browser)
    │
    ├── http://localhost:8501  ──► Streamlit UI (streamlit_ui/ui.py)
    │                                   │
    │                                   │ POST /resume/parse (multipart/form-data)
    │                                   ▼
    └── http://localhost:8000  ──► FastAPI Backend (app/main.py)
                                        │
                                        ▼
                                  routes.py
                                  - validates file is PDF
                                  - saves to /tmp/<uuid>.pdf
                                        │
                                        ▼
                                  FireworksResumeParser (app/services/parser.py)
                                  - pdfplumber extracts raw text
                                  - builds prompt
                                  - calls Fireworks AI via instructor
                                        │
                                        ▼
                                  Fireworks AI (Llama 3.3 70B Instruct)
                                  - JSON-mode structured output
                                        │
                                        ▼
                                  instructor validates response
                                  against ParsedResume (Pydantic)
                                        │
                                        ▼
                                  JSON response returned to UI
```

## Component Breakdown

### FastAPI Backend (`app/`)

```
app/
├── main.py          # App factory — mounts router, adds CORS middleware
├── api/
│   └── routes.py    # POST /resume/parse — file upload handler
├── services/
│   └── parser.py    # FireworksResumeParser — all AI logic lives here
├── models/
│   └── resume.py    # Pydantic models (ParsedResume and nested types)
├── core/
│   └── config.py    # Settings loaded from .env via pydantic-settings (Fireworks API key, model, base URL)
└── utils/
    └── pdf.py       # Standalone PDF extraction helper (not currently used by parser)
```

### Streamlit Frontend (`streamlit_ui/`)

Single file (`ui.py`). Responsibilities:
- File uploader widget (PDF only)
- POSTs to `http://localhost:8000/resume/parse`
- Renders: name, experience, role, location, email, summary, work history, skills, education, certifications
- Download button for raw JSON

### Docker / Deployment

Both services run in a single container:
- `start.sh` launches `uvicorn` (FastAPI) on port 8000, then `streamlit` on port 8501
- `Dockerfile` uses `python:3.10-slim` with `poppler-utils` for PDF support

## How `instructor` Works Here

`instructor` wraps the OpenAI-compatible Fireworks client. When `client.create()` is called with `response_model=ParsedResume`, instructor:
1. Converts the Pydantic model to a JSON Schema
2. Sends it to Fireworks with `Mode.JSON` — the model is instructed to return valid JSON matching the schema
3. instructor parses the response and validates it against the Pydantic model

`Mode.JSON` is used (rather than `Mode.TOOLS`) for broader compatibility across open-source models.

## Fireworks AI Integration

- Client: `openai.OpenAI(base_url="https://api.fireworks.ai/inference/v1", api_key=...)`
- Model: `accounts/fireworks/models/llama-v3p3-70b-instruct` (Llama 3.3 70B — open-source, ~$0.20/M tokens)
- API key set via `FIREWORKS_API_KEY` in `.env`
- Previously used AWS Bedrock (Claude 3.7 Sonnet) — switched due to cost/access constraints
