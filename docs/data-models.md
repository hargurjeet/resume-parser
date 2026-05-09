# Data Models

All models live in `app/models/resume.py`. They are Pydantic v2 models used both for API response validation and as the schema passed to `instructor` for structured LLM output.

## Top-Level: ParsedResume

```python
class ParsedResume(BaseModel):
    # Contact
    full_name: str                          # required, min_length=1
    email: Optional[EmailStr]
    phone: Optional[str]
    location: Optional[str]

    # Links
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_url: Optional[str]

    # Overview
    summary: Optional[str]
    current_job_title: Optional[str]
    years_of_experience: Optional[int]      # ge=0, le=50

    # Nested
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[Skill]
    certifications: List[Certification]
    projects: List[Project]
    languages: List[str]
```

## WorkExperience

```python
class WorkExperience(BaseModel):
    job_title: str          # required
    company: str            # required
    location: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    duration: Optional[str]
    responsibilities: List[str]   # prompt instructs: limit to 3–5 bullets
```

## Education

```python
class Education(BaseModel):
    degree: str             # required
    institution: str        # required
    field_of_study: Optional[str]
    graduation_year: Optional[int]   # ge=1950, le=2030
    gpa: Optional[float]             # ge=0.0, le=4.0
    location: Optional[str]
```

## Skill

```python
class Skill(BaseModel):
    name: str               # required
    category: Optional[Literal["technical", "soft", "language", "tool", "framework", "other"]]
    proficiency: Optional[Literal["beginner", "intermediate", "advanced", "expert"]]
```

## Certification

```python
class Certification(BaseModel):
    name: str               # required
    issuing_organization: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]
    credential_id: Optional[str]
```

## Project

```python
class Project(BaseModel):
    title: str              # required
    description: str        # required
    technologies: List[str]
    url: Optional[str]
    date: Optional[str]
```

## Validation Notes

- `email` uses Pydantic's `EmailStr` — will reject malformed emails
- `graduation_year` is bounded: 1950–2030
- `gpa` is bounded: 0.0–4.0
- `years_of_experience` is bounded: 0–50
- All list fields default to `[]` via `Field(default_factory=list)` — never `None`
- Claude is instructed not to infer missing information, so missing fields will correctly come back as `null`/omitted
