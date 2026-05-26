from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MovieSummary(Base):
    __tablename__ = "movie_summary"

    movie_id: Mapped[str] = mapped_column(
        ForeignKey("movies.movie_id"),
        primary_key=True,
    )
    positive_percent: Mapped[float] = mapped_column(Float, default=0.0)
    negative_percent: Mapped[float] = mapped_column(Float, default=0.0)
    positive_review_count: Mapped[int] = mapped_column(Integer, default=0)
    negative_review_count: Mapped[int] = mapped_column(Integer, default=0)
    tie_review_count: Mapped[int] = mapped_column(Integer, default=0)
    total_review_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
