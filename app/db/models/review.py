from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    movie_id: Mapped[str] = mapped_column(ForeignKey("movies.movie_id"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    movie = relationship("Movie", back_populates="reviews")
    phrases = relationship("LLMPhrase", back_populates="review")
