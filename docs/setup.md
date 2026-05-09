# Setup Guide

## Prerequisites

- Python 3.10+
- Fireworks AI account and API key (get one at fireworks.ai)
- No cloud subscription needed beyond Fireworks — pay-per-token, ~$0.20/M tokens

## Local Setup

```bash
# 1. Create and activate virtualenv
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# .env already has FIREWORKS_API_KEY and FIREWORKS_MODEL_ID set.
# Replace the API key value if needed:
# FIREWORKS_API_KEY=your_fireworks_api_key_here

# 4. Start backend (terminal 1)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Start frontend (terminal 2)
streamlit run streamlit_ui/ui.py --server.port 8501
```

Open `http://localhost:8501` to use the UI.
FastAPI docs available at `http://localhost:8000/docs`.

## Docker Setup

```bash
# Build
docker build -t resume-parser .

# Run (pass AWS credentials as env vars, or mount ~/.aws)
docker run -p 8000:8000 -p 8501:8501 \
  -e AWS_REGION=eu-west-2 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  resume-parser
```

The container runs both services via `start.sh`:
- FastAPI starts first, then waits 3 seconds
- Streamlit starts after

## Environment Variables

| Variable | Default (in code) | Set in .env |
|----------|--------------------|-------------|
| `FIREWORKS_API_KEY` | `""` | Yes — required |
| `FIREWORKS_MODEL_ID` | `accounts/fireworks/models/llama-v3p3-70b-instruct` | Optional override |
| `FIREWORKS_BASE_URL` | `https://api.fireworks.ai/inference/v1` | Optional override |

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `401 Unauthorized` | Invalid or missing Fireworks API key | Check `FIREWORKS_API_KEY` in `.env` |
| `404 model not found` | Wrong model ID | Verify model ID at fireworks.ai/models |
| `PDF extraction failed` | Encrypted or corrupted PDF | Try a different PDF; ensure poppler-utils is installed |
| `Address already in use` | Port 8000 or 8501 taken | Kill the other process or change port |
| `Resume text is empty or too short` | Image-based PDF (scanned) | pdfplumber can't extract text from scanned PDFs |
| `Schema validation failed` | Model returned malformed JSON | Try again — Llama occasionally fails structured output; instructor retries automatically |
