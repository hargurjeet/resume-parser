from pathlib import Path
from typing import Optional, Union

import pdfplumber
import instructor
from openai import OpenAI
from pydantic import ValidationError

from app.models.resume import ParsedResume
from app.core.config import settings


class FireworksResumeParser:

    def __init__(self):
        openai_client = OpenAI(
            base_url=settings.fireworks_base_url,
            api_key=settings.fireworks_api_key,
        )
        self.client = instructor.from_openai(
            openai_client,
            mode=instructor.Mode.JSON,
        )
        self.model_id = settings.fireworks_model_id

    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    def _create_prompt(self, resume_text: str) -> str:
        return f"""
You are a resume parsing assistant.

Rules:
- Be concise and factual
- Do not infer missing information
- Limit responsibilities to 3–5 bullets per role
- Normalize skills and titles where possible
- Do not add commentary

Resume:
{resume_text}
""".strip()

    def parse_resume(
        self, pdf_path: Union[str, Path]
    ) -> tuple[Optional[ParsedResume], Optional[str]]:
        path = Path(pdf_path)

        if not path.exists() or path.suffix.lower() != ".pdf":
            return None, "Invalid PDF file"

        try:
            resume_text = self.extract_text_from_pdf(path)
        except Exception as e:
            return None, f"PDF extraction failed: {str(e)}"

        if not resume_text or len(resume_text) < 20:
            return None, "Resume text is empty or too short"

        prompt = self._create_prompt(resume_text)

        try:
            parsed_resume: ParsedResume = self.client.create(
                model=self.model_id,
                response_model=ParsedResume,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract structured resume data and return valid JSON.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
            return parsed_resume, None

        except ValidationError as e:
            return None, f"Schema validation failed: {str(e)}"

        except Exception as e:
            return None, f"Parsing failed: {str(e)}"
