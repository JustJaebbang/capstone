from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"

    movie_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    movie_title: Mapped[str] = mapped_column(String(255), nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    reviews = relationship("Review", back_populates="movie")
    jobs = relationship("BatchJob", back_populates="movie")
