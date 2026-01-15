from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal


class Education(BaseModel):
    degree: str = Field(min_length=1)
    institution: str = Field(min_length=1)
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    location: Optional[str] = None


class WorkExperience(BaseModel):
    job_title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    name: str = Field(min_length=1)
    category: Optional[
        Literal["technical", "soft", "language", "tool", "framework", "other"]
    ] = None
    proficiency: Optional[
        Literal["beginner", "intermediate", "advanced", "expert"]
    ] = None


class Certification(BaseModel):
    name: str = Field(min_length=1)
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None


class Project(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    date: Optional[str] = None


class ParsedResume(BaseModel):
    full_name: str = Field(min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None

    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    summary: Optional[str] = None

    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)

    skills: List[Skill] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)

    projects: List[Project] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    current_job_title: Optional[str] = None
