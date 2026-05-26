from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OpinionGroup(Base):
    __tablename__ = "opinion_groups"

    job_id: Mapped[str] = mapped_column(
        ForeignKey("batch_jobs.job_id"),
        primary_key=True,
    )
    cluster_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    movie_id: Mapped[str] = mapped_column(String(50), index=True)
    topic: Mapped[str] = mapped_column(String(50), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    phrases: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    review_maps = relationship("ReviewClusterMap", back_populates="opinion_group")
