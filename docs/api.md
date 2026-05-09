# API Reference

Base URL: `http://localhost:8000`
FastAPI auto-docs: `http://localhost:8000/docs`

## Endpoints

### GET /

Health check.

**Response:**
```json
{"status": "ok"}
```

---

### POST /resume/parse

Parse a PDF resume and return structured data.

**Request:** `multipart/form-data`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | PDF file | Yes | Must have `.pdf` extension |

**curl example:**
```bash
curl -X POST "http://localhost:8000/resume/parse" \
  -F "file=@/path/to/resume.pdf"
```

**Success Response (200):** `ParsedResume` JSON object — see `docs/data-models.md`

**Error Responses:**

| Status | Condition |
|--------|-----------|
| 400 | File is not a PDF |
| 400 | PDF is invalid or unreadable |
| 400 | Extracted text is empty or too short (<20 chars) |
| 400 | Fireworks/instructor validation failed after retries |

Error body:
```json
{"detail": "<error message>"}
```

---

## How the Route Works (`app/api/routes.py`)

1. Validates `.pdf` extension
2. Writes upload to `/tmp/<uuid>.pdf`
3. Calls `FireworksResumeParser.parse_resume(path)`
4. Deletes temp file (`unlink(missing_ok=True)`)
5. Returns parsed result or raises 400 with error detail

## FastAPI App Config (`app/main.py`)

- Title: `Resume Parser API`, Version: `1.0.0`
- `root_path="/proxy/8000"` — supports running behind a proxy/tunnel
- CORS: all origins allowed (tighten for production)
- Router prefix: `/resume`
