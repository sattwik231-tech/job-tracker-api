from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import Query

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse


router = APIRouter(prefix="/jobs", tags=["Jobs"])


def get_user_job(db: Session, job_id: int, user_id: int) -> Job:
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.user_id == user_id,
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


# CREATE A JOB
@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job_data_dict = job_data.model_dump()

    if job_data_dict.get("job_url") is not None:
        job_data_dict["job_url"] = str(job_data_dict["job_url"])

    new_job = Job(
        **job_data_dict,
        user_id=current_user.id,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# GET ALL JOBS OF THE LOGGED-IN USER WITH FILTERING, SEARCHING, SORTING AND PAGINATION
@router.get("/")
def get_all_jobs(
    # PAGINATION
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=30, ge=1, le=100),

    # FILTERING
    job_id: int | None = Query(default=None, alias="id", ge=1),
    company: str | None = Query(default=None, min_length=1),
    location: str | None = Query(default=None, min_length=1),

    status_filter: Literal[
        "Applied",
        "Screening",
        "Assessment",
        "Interview",
        "Offer",
        "Selected",
        "Rejected",
        "Withdrawn",
        "On Hold",
    ] | None = Query(default=None, alias="status"),

    min_salary: Decimal | None = Query(default=None, ge=0),
    max_salary: Decimal | None = Query(default=None, ge=0),

    applied_from: date | None = None,
    applied_to: date | None = None,

    #GENERAL SEARCH
    search: str | None = Query(default=None, min_length=1),

    # SORTING
    sort_by: Literal[
        "id",
        "company",
        "job_title",
        "location",
        "status",
        "salary",
        "applied_date",
        "created_at",
    ] =  "created_at",

    order: Literal["asc", "desc"] = "desc",

    # AUTHENTICATION 

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # START WITH JOBS BELONGING TO THE LOGGED-IN USER
    query = db.query(Job).filter(
        Job.user_id == current_user.id
    )

    # 1. FILTER BY JOB ID
    if job_id is not None:
        query = query.filter(Job.id == job_id)

    # 2. FILTER BY COMPANY NAME
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))

    # 3. FILTER BY LOCATION
    if location:
        query = query.filter(
            Job.location.ilike(f"%{location}%")
        )

    # 4. FILTER BY APPLICATION STATUS
    if status_filter:
        query = query.filter(
            Job.status == status_filter
        )

    # 5. FILTER BY SALARY RANGE
    if min_salary is not None:
        query = query.filter(
            Job.salary >= min_salary
        )

    if max_salary is not None:
        query = query.filter(
            Job.salary <= max_salary
        )

    # 6. FILTER BY APPLICATION DATE RANGE
    if applied_from:
        query = query.filter(
            Job.applied_date >= applied_from
        )

    if applied_to:
        query = query.filter(
            Job.applied_date <= applied_to
        )

    # 7. GENERAL KEYWORD SEARCH
    if search:
        search_term = f"%{search}%"

        query = query.filter(
            Job.company.ilike(search_term)
            | Job.job_title.ilike(search_term)
            | Job.location.ilike(search_term)
        )

    # 8. VALIDATE FILTER RANGERS
    if (
        min_salary is not None
        and max_salary is not None
        and min_salary > max_salary
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="min_salary cannot be greater than max_salary",
        )

    if(
        applied_from is not None
        and applied_to is not None
        and applied_from > applied_to
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="applied_from cannot be later than applied_to",
        )

    # 9. COUNT MATCHING JOBS BEFORE PAGINATION
    total = query.count()

    # 10. SORTING 
    sort_column = {
        "id": Job.id,
        "company": Job.company,
        "job_title": Job.job_title,
        "location": Job.location,
        "status": Job.status,
        "salary": Job.salary,
        "applied_date": Job.applied_date,
        "created_at": Job.created_at,
    }

    sort_column = sort_column[sort_by]

    if order == "asc":
        query = query.order_by(
            sort_column.asc(),
            Job.id.asc(),
        )
    else:
        query = query.order_by(
            sort_column.desc(),
            Job.id.desc(),
        )

    # 11. PAGINATION
    jobs = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    total_pages = (total + limit - 1) // limit

    # 12. RETURN PAGINATION RESPONSE
    return {
        "items": jobs,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }

# GET A SPECIFIC JOB
@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_job(db, job_id, current_user.id)


# UPDATE A JOB
@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_user_job(db, job_id, current_user.id)

    updates = job_data.model_dump(exclude_unset=True)

    if updates.get("job_url") is not None:
        updates["job_url"] = str(updates["job_url"])

    for field, value in updates.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


# DELETE A JOB
@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_user_job(db, job_id, current_user.id)

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}
