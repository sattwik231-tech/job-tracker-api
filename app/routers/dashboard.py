
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.job import Job
from app.models.user import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# DASHBOARD SUMMARY
@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_applications = (
        db.query(func.count(Job.id))
        .filter(Job.user_id == current_user.id)
        .scalar()
    )

    status_results = (
        db.query(
            Job.status,
            func.count(Job.id),
        )
        .filter(Job.user_id == current_user.id)
        .group_by(Job.status)
        .all()
    )

    status_breakdown = {
        "Applied": 0,
        "Screening": 0,
        "Assessment": 0,
        "Interview": 0,
        "Offer": 0,
        "Selected": 0,
        "Rejected": 0,
        "Withdrawn": 0,
        "On Hold": 0,
    }

    for job_status, count in status_results:
        status_breakdown[job_status] = count

    return {
        "total_applications": total_applications,
        "status_breakdown": status_breakdown,
    }


# APPLICATION ANALYTICS
@router.get("/analytics")
def get_application_analytics(
    months: int = Query(default=12, ge=1, le=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. DETERMINE THE DATE RANGE
    today = date.today()

    month_starts = []

    for offset in range(months - 1, -1, -1):
        month_index = today.year * 12 + today.month - 1 - offset

        year = month_index // 12
        month = month_index % 12 + 1

        month_starts.append(date(year, month, 1))

    start_date = month_starts[0]

    # FIRST DAY OF THE MONTH AFTER THE CURRENT MONTH
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1)
    else:
        end_date = date(today.year, today.month + 1, 1)

    # 2. GET MONTHLY APPLICATION COUNTS
    month_expression = func.date_trunc(
        "month",
        Job.applied_date,
    )

    monthly_results = (
        db.query(
            month_expression.label("month"),
            func.count(Job.id).label("total"),
        )
        .filter(
            Job.user_id == current_user.id,
            Job.applied_date >= start_date,
            Job.applied_date < end_date,
        )
        .group_by(month_expression)
        .order_by(month_expression)
        .all()
    )

    # CONVERT DATABASE RESULTS INTO DICTIONARY
    monthly_counts = {
        result.month.strftime("%Y-%m"): result.total
        for result in monthly_results
    }

    # INCLUDE MONTHS WITH ZERO APPLICATIONS
    monthly_applications = []

    for month_start in month_starts:
        month_key = month_start.strftime("%Y-%m")

        monthly_applications.append({
            "month": month_key,
            "applications": monthly_counts.get(month_key, 0),
        })

    # 3. GET APPLICATION COUNTS BY STATUS
    status_results = (
        db.query(
            Job.status,
            func.count(Job.id).label("total"),
        )
        .filter(Job.user_id == current_user.id)
        .group_by(Job.status)
        .all()
    )

    status_counts = {
        result.status: result.total
        for result in status_results
    }

    total_applications = sum(status_counts.values())

    # 4. CALCULATE APPLICATION FUNNEL COUNTS
    interview_reached = (
        status_counts.get("Interview", 0)
        + status_counts.get("Offer", 0)
        + status_counts.get("Selected", 0)
    )

    offer_reached = (
        status_counts.get("Offer", 0)
        + status_counts.get("Selected", 0)
    )

    selected = status_counts.get("Selected", 0)

    # 5. CALCULATE PERCENTAGES
    def calculate_percentage(count: int) -> float:
        if total_applications == 0:
            return 0.0

        return round(
            (count / total_applications) * 100,
            2,
        )

    # 6. RETURN ANALYTICS
    return {
        "total_applications": total_applications,

        "monthly_applications": monthly_applications,

        "application_funnel": {
            "interview_reached": {
                "count": interview_reached,
                "percentage": calculate_percentage(interview_reached),
            },

            "offer_reached": {
                "count": offer_reached,
                "percentage": calculate_percentage(offer_reached),
            },

            "selected": {
                "count": selected,
                "percentage": calculate_percentage(selected),
            },
        },
    }


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recent_jobs = (
        db.query(Job)
        .filter(Job.user_id == current_user.id)
        .order_by(
            Job.updated_at.desc(),
            Job.created_at.desc(),
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "job_id": job.id,
            "company": job.company,
            "job_title": job.job_title,
            "status": job.status,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }

        for job in recent_jobs
    ]