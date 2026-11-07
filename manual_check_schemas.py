
from app.schemas.user import UserCreate
from app.schemas.job import JobCreate

user = UserCreate(
    name="Test User",
    email="test@example.com",
    password="StrongPass123",
)
print("User schema:", user)

job = JobCreate(
    company="Google",
    job_title="Software Engineer",
    location="Bengaluru",
    job_url="https://careers.google.com/",
    status="Applied",
    salary=1200000,
)
print("Job schema:", job)
