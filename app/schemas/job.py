from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


JobStatus = Literal[
    "Applied",
    "Screening",
    "Assessment",
    "Interview",
    "Offer",
    "Selected",
    "Rejected",
    "Withdrawn",
    "On Hold"
]

class JobCreate(BaseModel):
    """Validate data for a new job application."""

    company: str = Field(min_length=1, max_length=150)
    job_title: str = Field(min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=150)
    job_url: HttpUrl | None = None
    source: str | None = Field(default=None, max_length= 150)
    status: JobStatus = "Applied"
    salary: Decimal | None = Field(default=None, ge=0)
    applied_date: date | None = None
    notes: str | None = None

class JobUpdate(BaseModel):
    """Validate fields provided when updating a job application."""

    company: str | None = Field(default=None, min_length=1, max_length=150)
    job_title: str | None = Field(default=None, min_length=1, max_length=150)
    location: str | None = Field(default=None, max_length=150)
    job_url: HttpUrl | None = None
    source: str | None = Field(default=None, max_length=100)
    status: JobStatus | None = None
    salary: Decimal | None = Field(default=None, ge=0)
    applied_date: date | None = None
    notes: str | None = None

class JobResponse(BaseModel):
    """Define the job application information returned by the API."""

    id: int
    user_id: int
    company: str
    job_title: str
    location: str | None
    job_url: HttpUrl | None
    source: str | None
    status: str
    salary: Decimal | None
    applied_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

