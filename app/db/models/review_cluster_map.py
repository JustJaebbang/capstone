from uuid import uuid4

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewClusterMap(Base):
    __tablename__ = "review_cluster_map"
    __table_args__ = (
        ForeignKeyConstraint(
            ["job_id", "cluster_id"],
            ["opinion_groups.job_id", "opinion_groups.cluster_id"],
        ),
    )

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        default=lambda: f"rcm_{uuid4().hex}",
    )
    job_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    cluster_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    review_id: Mapped[str] = mapped_column(
        ForeignKey("reviews.review_id"),
        index=True,
    )

    opinion_group = relationship("OpinionGroup", back_populates="review_maps")
