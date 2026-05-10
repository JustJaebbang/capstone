from collections import defaultdict

from app.schemas import (
    FinalResultSchema,
    FinalSummarySchema,
    TopOpinionItem,
    OpinionReviewItem,
    SentimentRatioSchema,
)
from app.services.labels import make_label

REVIEWS_PREVIEW_LIMIT = 10


def collect_reviews_for_cluster(
    cluster: dict,
    llm_result: dict,
    source_reviews: list[dict],
) -> list[OpinionReviewItem]:
    target_phrase_set = set(cluster["phrases"])
    matched_review_ids = set()

    for item in llm_result["results"]:
        review_id = item["review_id"]

        for phrase in item["phrases"]:
            if phrase["text"] in target_phrase_set:
                matched_review_ids.add(review_id)

    reviews = []
    for review in source_reviews:
        if review["review_id"] in matched_review_ids:
            reviews.append(
                OpinionReviewItem(
                    review_id=review["review_id"],
                    text=review["text"],
                )
            )

    return reviews


def calculate_sentiment_ratio(llm_result: dict) -> SentimentRatioSchema:
    review_scores = []

    for item in llm_result["results"]:
        positive_count = 0
        negative_count = 0

        for phrase in item["phrases"]:
            if phrase["sentiment"] == "positive":
                positive_count += 1
            elif phrase["sentiment"] == "negative":
                negative_count += 1

        score = positive_count - negative_count

        if score > 0:
            sentiment_for_ratio = "positive"
        elif score < 0:
            sentiment_for_ratio = "negative"
        else:
            sentiment_for_ratio = "tie"

        review_scores.append(
            {
                "review_id": item["review_id"],
                "positive_count": positive_count,
                "negative_count": negative_count,
                "score": score,
                "sentiment_for_ratio": sentiment_for_ratio,
            }
        )

    positive_review_count = sum(1 for r in review_scores if r["sentiment_for_ratio"] == "positive")
    negative_review_count = sum(1 for r in review_scores if r["sentiment_for_ratio"] == "negative")
    tie_review_count = sum(1 for r in review_scores if r["sentiment_for_ratio"] == "tie")
    total_review_count = len(review_scores)

    positive_effective = positive_review_count + tie_review_count * 0.5
    negative_effective = negative_review_count + tie_review_count * 0.5

    if total_review_count == 0:
        positive_percent = 0.0
        negative_percent = 0.0
    else:
        positive_percent = round((positive_effective / total_review_count) * 100, 1)
        negative_percent = round((negative_effective / total_review_count) * 100, 1)

    return SentimentRatioSchema(
        positive_percent=positive_percent,
        negative_percent=negative_percent,
        positive_review_count=positive_review_count,
        negative_review_count=negative_review_count,
        tie_review_count=tie_review_count,
        total_review_count=total_review_count,
        rule="tie reviews are split 50:50",
    )


def build_final_result(
    job,
    llm_result: dict,
    cluster_result: dict,
    source_reviews: list[dict],
) -> FinalResultSchema:
    top_opinions = []
    clusters = cluster_result["clusters"]

    for idx, cluster in enumerate(clusters[:3], start=1):
        top_opinions.append(
            TopOpinionItem(
                rank=idx,
                topic=cluster["topic"],
                sentiment=cluster["sentiment"],
                label=make_label(cluster["topic"], cluster["sentiment"]),
                count=cluster["count"],
            )
        )

    sentiment_ratio = calculate_sentiment_ratio(llm_result)

    return FinalResultSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        summary=FinalSummarySchema(
            top_opinions=top_opinions,
            sentiment_ratio=sentiment_ratio,
        ),
    )


