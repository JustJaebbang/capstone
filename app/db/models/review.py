from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    movie_id: Mapped[str] = mapped_column(ForeignKey("movies.movie_id"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_review_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1), nullable=True)
    written_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    text_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    __table_args__ = (
        UniqueConstraint("source", "external_review_id", name="uq_reviews_source_external"),
        Index("ix_reviews_source_movie_hash", "source", "movie_id", "text_hash"),
    )

    movie = relationship("Movie", back_populates="reviews")
    phrases = relationship("LLMPhrase", back_populates="review")
