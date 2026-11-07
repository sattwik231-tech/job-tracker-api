from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key = True, index = True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
                                         nullable=False, index=True)

    company: Mapped[str] = mapped_column(String(150), nullable=False)

    job_title: Mapped[str] = mapped_column(String(150), nullable=False)

    location: Mapped[str | None] = mapped_column(String(150), nullable=True)

    job_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="Applied",
                                        server_default="Applied", nullable=False)

    salary: Mapped[Decimal | None] = mapped_column(Numeric(12,2), nullable=True)

    applied_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(),
                                                 onupdate=func.now(),
                                                 nullable=False)


    owner: Mapped["User"] = relationship(back_populates="jobs")

    __table_args__ = (
        Index("ix_job_user_status", "user_id", "status"),
    )

