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


class CollectedMovie(BaseModel):
    source: str = Field(..., examples=["kobis"])
    external_movie_id: str = Field(..., examples=["20239012"])
    movie_title: str = Field(..., examples=["파묘"])
    poster_url: Optional[str] = Field(default=None)
    release_date: Optional[date] = Field(default=None, examples=["2024-02-22"])
    genre: Optional[str] = Field(default=None, examples=["공포,스릴러"])


class CollectedReview(BaseModel):
    source: str = Field(..., examples=["cgv"])
    movie_id: str = Field(..., examples=["kobis_20239012"])
    external_review_id: Optional[str] = Field(default=None, examples=["123456789"])
    author: Optional[str] = Field(default=None, examples=["user***"])
    rating: Optional[float] = Field(default=None, examples=[9.0])
    text: str = Field(..., examples=["배우 연기가 좋았다"])
    written_at: Optional[datetime] = Field(default=None)


CollectionJobStatus = Literal["queued", "running", "completed", "failed"]
CollectionMode = Literal["run_now", "scheduled"]
CollectionDepth = Literal["preview", "full"]


class CollectionRunRequest(BaseModel):
    movie_id: str = Field(..., examples=["kobis_20252402"])
    cgv_movie_code: Optional[str] = Field(default=None, examples=["30001046"])
    source: str = Field(default="cgv", examples=["cgv"])
    depth: CollectionDepth = Field(
        default="preview",
        description="'preview' = ~50 reviews, ~30-60s response. 'full' = all reviews, "
                    "5-15 min (use when caller is okay with long wait, e.g., user "
                    "clicked then walked away).",
    )
    run_analysis: bool = Field(
        default=False,
        description="If true, run the full analysis pipeline (LLM → cluster → final) "
                    "after collection. Only triggers if new reviews were inserted.",
    )


class CollectionJobResponse(BaseModel):
    collection_job_id: str
    source: str
    mode: CollectionMode
    target_movie_id: str
    source_external_id: Optional[str]
    status: CollectionJobStatus
    started_at: datetime
    finished_at: Optional[datetime]
    total_fetched: int
    total_inserted: int
    error_message: Optional[str]
    analysis_job_id: Optional[str] = Field(
        default=None,
        description="batch_jobs.job_id of the analysis pipeline triggered after collection. "
                    "Populated only when run_analysis=true and new reviews were inserted.",
    )
    analysis_status: Optional[str] = Field(
        default=None,
        description="completed / failed / skipped_no_new / not_requested",
    )


class SubscribeRequest(BaseModel):
    movie_id: str = Field(..., examples=["kobis_20252402"])
    cgv_movie_code: Optional[str] = Field(default=None, examples=["30001046"])
    source: str = Field(default="cgv", examples=["cgv"])


class SubscribeResponse(BaseModel):
    subscribed: bool
    movie_id: str
    source: str
    cgv_movie_code: str
    already_subscribed: bool
    collection_job_id: str
    next_batch_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp of next scheduled batch run (KST). "
                    "None if scheduler disabled.",
    )

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


class ClusterGroup(BaseModel):
    cluster_id: str
    topic: str
    sentiment: Literal["positive", "negative"]
    count: int
    review_count: int
    phrases: List[str]


class ClusterResponseSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    clusters: List[ClusterGroup]


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
    reviews_preview: List[OpinionReviewItem]


class OpinionGroupReviewsResponse(BaseModel):
    job_id: str
    cluster_id: str
    label: str
    total_count: int
    page: int
    page_size: int
    total_pages: int
    reviews: List[OpinionReviewItem]


class SentimentRatioSchema(BaseModel):
    positive_percent: float
    negative_percent: float
    positive_review_count: int
    negative_review_count: int
    tie_review_count: int
    total_review_count: int
    rule: str


class ElementScoreItem(BaseModel):
    element: str = Field(..., examples=["스토리"])
    score: Optional[float] = Field(
        default=None,
        description="긍정 비율 × 100 (0~100). 언급된 phrase가 없으면 null.",
        examples=[78.0],
    )
    positive_count: int = Field(default=0, examples=[235])
    negative_count: int = Field(default=0, examples=[65])
    mention_count: int = Field(
        default=0,
        description="positive_count + negative_count",
        examples=[300],
    )


class FinalSummarySchema(BaseModel):
    top_opinions: List[TopOpinionItem]
    sentiment_ratio: SentimentRatioSchema
    element_scores: List[ElementScoreItem] = Field(default_factory=list)


class FinalResultSchema(BaseModel):
    job_id: str
    movie_id: str
    movie_title: str
    summary: FinalSummarySchema


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


class OpinionReviewItem(BaseModel):
    review_id: str
    text: str


class OpinionGroupListItem(BaseModel):
    cluster_id: str
    topic: str
    sentiment: Literal["positive", "negative"]
    label: str
    count: int


class OpinionGroupListResponse(BaseModel):
    job_id: str
    items: List[OpinionGroupListItem]
    total_count: int


class DashboardTopKeyword(BaseModel):
    rank: int = Field(..., examples=[1])
    topic: str = Field(..., examples=["연기"])
    sentiment: Literal["positive", "negative"]
    label: str = Field(..., examples=["연기가 좋아요"])
    count: int = Field(..., examples=[328])


class DashboardSentimentRatio(BaseModel):
    positive_percent: float = Field(..., examples=[72.0])
    negative_percent: float = Field(..., examples=[28.0])


class DashboardMovieItem(BaseModel):
    movie_id: str = Field(..., examples=["kobis_20239012"])
    movie_title: str = Field(..., examples=["파묘"])
    poster_url: Optional[str] = Field(default=None)
    genre: Optional[str] = Field(default=None, examples=["공포,스릴러"])
    release_year: Optional[int] = Field(default=None, examples=[2024])
    release_date: Optional[date] = Field(default=None, examples=["2024-02-22"])
    source: Optional[str] = Field(default=None, examples=["kobis"])
    total_review_count: int = Field(default=0, examples=[1243])
    sentiment_ratio: DashboardSentimentRatio
    top_keywords: List[DashboardTopKeyword] = Field(default_factory=list)


class DashboardMoviesResponse(BaseModel):
    items: List[DashboardMovieItem]
    total_count: int


class DashboardRecentJob(BaseModel):
    job_id: str = Field(..., examples=["job_021"])
    movie_id: str = Field(..., examples=["mv_001"])
    movie_title: str = Field(..., examples=["파묘"])
    status: JobStatus
    finished_at: Optional[datetime] = None


class DashboardSummaryResponse(BaseModel):
    total_movies: int = Field(..., examples=[12])
    total_completed_jobs: int = Field(..., examples=[8])
    total_reviews_analyzed: int = Field(..., examples=[24860])
    recent_jobs: List[DashboardRecentJob] = Field(default_factory=list)
    updated_at: datetime


TopOpinionItem.model_rebuild()
OpinionGroupItem.model_rebuild()
SentimentRatioSchema.model_rebuild()
FinalSummarySchema.model_rebuild()
FinalResultSchema.model_rebuild()