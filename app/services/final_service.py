from collections import defaultdict
from typing import List

from app.schemas import (
    ElementScoreItem,
    FinalResultSchema,
    FinalSummarySchema,
    TopOpinionItem,
    OpinionReviewItem,
    SentimentRatioSchema,
)
from app.services.labels import make_label

REVIEWS_PREVIEW_LIMIT = 10

# 6요소 고정 + 매핑 키워드. phrase 텍스트에 키워드가 포함되면 해당 요소로 분류.
# 순서 = 응답 노출 순서.
ELEMENT_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("스토리", ("스토리", "서사", "결말", "개연")),
    ("연기", ("연기", "배우", "캐스팅")),
    ("몰입감", ("몰입", "긴장")),
    ("전개", ("전개", "지루", "루즈", "늘어", "템포")),
    ("재미", ("재미", "재밌", "재미없", "노잼", "흥미")),
    ("연출", ("연출", "장면", "분위기", "영상미", "비주얼", "화면", "촬영", "색감")),
]


def _classify_phrase_to_element(text: str) -> str | None:
    for element, keywords in ELEMENT_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return element
    return None


def calculate_element_scores(llm_result: dict) -> List[ElementScoreItem]:
    """
    리뷰 단위로 요소별 긍정/부정 언급을 집계.
    한 리뷰에서 같은 요소에 대해 phrase sentiment가 섞이면 tie로 처리하고
    sentiment_ratio와 동일하게 50:50 분배.
    score = 긍정 effective / (긍정 effective + 부정 effective) × 100.
    언급 0인 요소는 score=None.
    """
    per_review: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"positive": 0, "negative": 0})
    )

    for item in llm_result["results"]:
        review_id = item["review_id"]
        for phrase in item["phrases"]:
            element = _classify_phrase_to_element(phrase["text"])
            if element is None:
                continue
            sentiment = phrase["sentiment"]
            if sentiment in ("positive", "negative"):
                per_review[review_id][element][sentiment] += 1

    tally = {
        element: {"positive": 0, "negative": 0, "tie": 0}
        for element, _ in ELEMENT_KEYWORDS
    }

    for elements_for_review in per_review.values():
        for element, counts in elements_for_review.items():
            pos = counts["positive"]
            neg = counts["negative"]
            if pos > 0 and neg == 0:
                tally[element]["positive"] += 1
            elif neg > 0 and pos == 0:
                tally[element]["negative"] += 1
            else:
                tally[element]["tie"] += 1

    scores: List[ElementScoreItem] = []
    for element, _ in ELEMENT_KEYWORDS:
        pos = tally[element]["positive"]
        neg = tally[element]["negative"]
        tie = tally[element]["tie"]
        mention = pos + neg + tie

        if mention == 0:
            scores.append(
                ElementScoreItem(
                    element=element,
                    score=None,
                    positive_count=0,
                    negative_count=0,
                    mention_count=0,
                )
            )
            continue

        positive_effective = pos + tie * 0.5
        score = round((positive_effective / mention) * 100, 1)

        scores.append(
            ElementScoreItem(
                element=element,
                score=score,
                positive_count=pos,
                negative_count=neg,
                mention_count=mention,
            )
        )

    return scores


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
    element_scores = calculate_element_scores(llm_result)

    return FinalResultSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        summary=FinalSummarySchema(
            top_opinions=top_opinions,
            sentiment_ratio=sentiment_ratio,
            element_scores=element_scores,
        ),
    )


