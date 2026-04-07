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
    reviews: List[ReviewItem]


class LLMResultItem(BaseModel):
    review_id: str
    phrases: List[PhraseSentimentItem]


class LLMResponseSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    results: List[LLMResultItem]


class PhraseItem(BaseModel):
    review_id: str
    text: str
    sentiment: Literal["positive", "negative"]


class ClusterRequestSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    phrases: List[PhraseItem]


# class ClusterGroup(BaseModel):
#     cluster_id: str
#     topic: str
#     sentiment: Literal["positive", "negative"]
#     count: int
#     review_count: int
#     phrases: List[str]


# class ClusterResponseSchema(BaseModel):
#     job_id: str
#     movie_id: str
#     movie_title: str
#     clusters: List[ClusterGroup]


class TopOpinionItem(BaseModel):
    rank: int
    topic: str
    sentiment: Literal["positive", "negative"]
    label: str
    count: int


class OpinionGroupItem(BaseModel):
    cluster_id: str
    topic: str
    sentiment: Literal["positive", "negative"]
    label: str
    count: int
    examples: List[str]


class SentimentRatioSchema(BaseModel):
    positive_percent: float
    negative_percent: float
    positive_review_count: int
    negative_review_count: int
    tie_review_count: int
    total_review_count: int
    rule: str


class FinalSummarySchema(BaseModel):
    top_opinions: List[TopOpinionItem]
    sentiment_ratio: SentimentRatioSchema


class FinalDetailsSchema(BaseModel):
    opinion_groups: List[OpinionGroupItem]


class FinalResultSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    summary: FinalSummarySchema
    details: FinalDetailsSchema


class CreateBatchJobRequest(BaseModel):
    movie_id: str
    target_date: date


class CreateBatchJobResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus


class PhraseSentimentItem(BaseModel):
    text: str
    sentiment: Literal["positive", "negative"]


TopOpinionItem.model_rebuild()
OpinionGroupItem.model_rebuild()
SentimentRatioSchema.model_rebuild()
FinalSummarySchema.model_rebuild()
FinalDetailsSchema.model_rebuild()
FinalResultSchema.model_rebuild()