export type Movie = {
  movie_id: string;
  movie_title: string;
  source: string;
  is_active: boolean;
  release_year: number;
  notes?: string;
};

export type BatchJobResponse = {
  job_id: string;
  movie_id: string;
  movie_title?: string;
  target_date: string;
  status: string;
  created_at?: string;
  started_at?: string | null;
  finished_at?: string | null;
};

export type SentimentRatio = {
  positive_percent: number;
  negative_percent: number;
};

export type TopOpinion = {
  label: string;
  count: number;
};

export type ElementScore = {
  element: string;
  score: number; // 0–100
};

export type FinalResult = {
  summary: {
    sentiment_ratio: SentimentRatio;
    top_opinions: TopOpinion[];
    element_scores?: ElementScore[];
  };
};

export type OpinionGroup = {
  cluster_id: string | number;
  label: string;
  count: number;
};

export type ReviewItem = {
  text: string;
  sentiment: "positive" | "negative" | "neutral" | string;
};

export type OpinionGroupReviewsResponse = {
  reviews: ReviewItem[];
  total_count: number;
  total_pages: number;
};

// ============================================
// 대시보드 (/movies) 화면용 타입
// ============================================

export type JobStatus = "completed" | "running" | "failed";

export type KeywordSentiment = "positive" | "negative" | "neutral";

export type TopKeyword = {
  rank: number;
  label: string;
  sentiment: KeywordSentiment;
  count: number;
};

export type RecentActivity = {
  movie_id: string;
  movie_title: string;
  status: JobStatus;
  completed_at: string; // ISO datetime
};

export type DashboardSummary = {
  total_movies: number;
  completed_movies: number;
  total_reviews: number;
  avg_processing_seconds: number;
  overall_sentiment: SentimentRatio;
  top_keywords_overall: TopKeyword[];
  recent_activities: RecentActivity[];
  updated_at: string;
};

// 기존 Movie 타입을 확장 — 추가 필드만 더함
export type DashboardMovie = Movie & {
  poster_url: string | null;
  release_date: string | null;
  genres: string[];

  latest_job_id: string | null;
  job_status: JobStatus | null;
  job_completed_at: string | null;

  review_count: number;
  sentiment: SentimentRatio;
  top_keywords: TopKeyword[];
};

export type DashboardMoviesResponse = {
  items: DashboardMovie[];
  total: number;
};