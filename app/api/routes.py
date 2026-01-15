from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

from app.services.parser import BedrockResumeParser
from app.models.resume import ParsedResume

router = APIRouter(prefix="/resume", tags=["Resume Parser"])

parser_service = BedrockResumeParser()


@router.post("/parse", response_model=ParsedResume)
def parse_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    temp_path = Path(f"/tmp/{uuid.uuid4()}.pdf")

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed_resume, error = parser_service.parse_resume(temp_path)

    temp_path.unlink(missing_ok=True)

    if error:
        raise HTTPException(status_code=400, detail=error)

    return parsed_resume

