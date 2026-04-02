from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


JobStatus = Literal[
    "queued",
    "collecting_reviews",
    "llm_processing",
    "clustering",
    "saving_results",
    "completed",
    "failed",
]

# 데이터셋용 리뷰 스키마
class DatasetReviewSchema(BaseModel):
    movie_id: str
    movie_title: str
    source: str
    review_id: str
    text: str

class MovieSchema(BaseModel):
    movie_id: str = Field(..., examples=["mv_001"])
    movie_title: str = Field(..., examples=["파묘"])
    source: str = Field(..., examples=["naver"])
    is_active: bool = True
    registered_at: datetime
    updated_at: datetime
    release_year: Optional[int] = Field(default=None, examples=[2024])
    notes: Optional[str] = Field(default=None, examples=["시연용"])


class BatchJobSchema(BaseModel):
    job_id: str = Field(..., examples=["job_001"])
    movie_id: str = Field(..., examples=["mv_001"])
    movie_title: str = Field(..., examples=["파묘"])
    target_date: date
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ReviewItem(BaseModel):
    review_id: str = Field(..., examples=["r1"])
    text: str = Field(..., examples=["연기는 좋았는데 스토리는 지루했다."])


class LLMRequestSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    target_date: date
    reviews: List[ReviewItem]


class LLMResultItem(BaseModel):
    review_id: str
    key_phrases: List[str]


class LLMResponseSchema(BaseModel):
    job_id: str
    movie_id: str
    results: List[LLMResultItem]


class PhraseItem(BaseModel):
    review_id: str
    text: str


class ClusterRequestSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    phrases: List[PhraseItem]


class ClusterItem(BaseModel):
    review_id: str
    text: str


class ClusterGroup(BaseModel):
    cluster_id: int
    topic: str
    items: List[ClusterItem]


class ClusterResponseSchema(BaseModel):
    job_id: str
    movie_id: str
    clusters: List[ClusterGroup]


class ReviewSummaryItem(BaseModel):
    label: str
    count: int
    ratio: float
    examples: List[str]


class FinalResultSchema(BaseModel):
    movie_id: str
    movie_title: str
    analysis_date: date
    total_reviews: int
    review_summary: List[ReviewSummaryItem]


class CreateBatchJobRequest(BaseModel):
    movie_id: str
    target_date: date


class CreateBatchJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus