# Setup Guide

## Prerequisites

- Python 3.10+
- `uv` package manager (`pip install uv`)
- Fireworks AI account and API key (get one at fireworks.ai)
- No cloud subscription needed beyond Fireworks — pay-per-token, ~$0.20/M tokens

## Local Setup

```bash
# 1. Install dependencies
uv sync

# 2. Create .env file (git-ignored — never committed)
cat > .env <<EOF
FIREWORKS_API_KEY=your_fireworks_api_key_here
FIREWORKS_MODEL_ID=accounts/fireworks/models/llama-v3p3-70b-instruct
EOF

# 3. Start backend (terminal 1)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Start frontend (terminal 2)
uv run streamlit run streamlit_ui/ui.py --server.port 8501
```

Open `http://localhost:8501` to use the UI.
FastAPI interactive docs available at `http://localhost:8000/docs`.

## Restarting the Backend

```bash
# If running — press Ctrl+C, then:
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# If port 8000 is stuck from a previous run:
lsof -ti:8000 | xargs kill -9
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Setup

```bash
# Build
docker build -t resume-parser .

# Run — pass Fireworks API key as env var
docker run -p 8000:8000 -p 8501:8501 \
  -e FIREWORKS_API_KEY=your_fireworks_api_key_here \
  resume-parser
```

The container runs both services via `start.sh`:
- FastAPI starts first, waits 3 seconds
- Streamlit starts after

## Environment Variables

| Variable | Default (in code) | Required |
|----------|--------------------|----------|
| `FIREWORKS_API_KEY` | `""` | Yes |
| `FIREWORKS_MODEL_ID` | `accounts/fireworks/models/llama-v3p3-70b-instruct` | No — override to swap model |
| `FIREWORKS_BASE_URL` | `https://api.fireworks.ai/inference/v1` | No — override for proxy |

> `.env` is git-ignored. Never commit it — it contains the API key.

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `Connection refused on port 8000` | Backend not running | Start uvicorn in a separate terminal |
| `Extra inputs are not permitted` on startup | Stale env var (e.g. `BEDROCK_MODEL_ID`) in shell | Already fixed via `extra="ignore"` in config — restart shell if it persists |
| `401 Unauthorized` | Invalid or missing Fireworks API key | Check `FIREWORKS_API_KEY` in `.env` |
| `404 model not found` | Wrong model ID | Verify model ID at fireworks.ai/models |
| `PDF extraction failed` | Encrypted or corrupted PDF | Try a different PDF; ensure poppler-utils is installed |
| `Address already in use` | Port 8000 or 8501 taken | `lsof -ti:8000 \| xargs kill -9` |
| `Resume text is empty or too short` | Image-based (scanned) PDF | pdfplumber can't extract text from scanned PDFs |
| `Schema validation failed` | Model returned malformed JSON | instructor retries up to 3 times automatically; if it still fails, retry the upload |
