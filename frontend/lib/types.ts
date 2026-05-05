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

export type FinalResult = {
  summary: {
    sentiment_ratio: SentimentRatio;
    top_opinions: TopOpinion[];
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