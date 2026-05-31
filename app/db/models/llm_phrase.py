from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LLMPhrase(Base):
    __tablename__ = "llm_phrases"

    phrase_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        default=lambda: f"ph_{uuid4().hex}",
    )
    job_id: Mapped[str] = mapped_column(
        ForeignKey("batch_jobs.job_id"),
        index=True,
        nullable=False,
    )
    review_id: Mapped[str] = mapped_column(ForeignKey("reviews.review_id"), index=True)
    movie_id: Mapped[str] = mapped_column(String(50), index=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    review = relationship("Review", back_populates="phrases")
