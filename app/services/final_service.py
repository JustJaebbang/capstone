from collections import defaultdict

from app.schemas import (
    FinalResultSchema,
    FinalSummarySchema,
    FinalDetailsSchema,
    TopOpinionItem,
    OpinionGroupItem,
    OpinionReviewItem,
    SentimentRatioSchema,
)


LABEL_MAP = {
    ("연기", "positive"): "연기가 좋아요",
    ("연기", "negative"): "연기가 아쉬워요",
    ("캐릭터", "positive"): "캐릭터가 매력적이에요",
    ("캐릭터", "negative"): "캐릭터가 아쉬워요",
    ("스토리", "positive"): "스토리가 좋아요",
    ("스토리", "negative"): "스토리가 아쉬워요",
    ("연출", "positive"): "연출이 좋아요",
    ("연출", "negative"): "연출이 아쉬워요",
    ("영상미", "positive"): "영상미가 좋아요",
    ("영상미", "negative"): "영상미가 아쉬워요",
    ("음향", "positive"): "음향이 좋아요",
    ("음향", "negative"): "음향이 아쉬워요",
    ("속도감", "positive"): "전개 속도감이 좋아요",
    ("속도감", "negative"): "전개가 늘어져요",
    ("재미", "positive"): "재미있어요",
    ("재미", "negative"): "재미가 아쉬워요",
    ("몰입감", "positive"): "몰입감이 높아요",
    ("몰입감", "negative"): "몰입감이 떨어져요",
    ("감정", "positive"): "감정적으로 와닿아요",
    ("감정", "negative"): "감정선이 아쉬워요",
    ("메시지", "positive"): "메시지가 인상적이에요",
    ("메시지", "negative"): "메시지가 아쉬워요",
    ("기타", "positive"): "긍정적인 반응이 있어요",
    ("기타", "negative"): "아쉬운 반응이 있어요",
}


def make_label(topic: str, sentiment: str) -> str:
    return LABEL_MAP.get((topic, sentiment), f"{topic} ({sentiment})")


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
    opinion_groups = []

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

    for cluster in clusters:
        cluster_reviews = collect_reviews_for_cluster(
            cluster=cluster,
            llm_result=llm_result,
            source_reviews=source_reviews,
        )

        opinion_groups.append(
            OpinionGroupItem(
                cluster_id=cluster["cluster_id"],
                topic=cluster["topic"],
                sentiment=cluster["sentiment"],
                label=make_label(cluster["topic"], cluster["sentiment"]),
                count=cluster["count"],
                examples=cluster["phrases"],
                reviews=cluster_reviews,
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
        details=FinalDetailsSchema(
            opinion_groups=opinion_groups,
        ),
    )