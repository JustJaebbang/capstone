from collections import defaultdict
from typing import List, Optional

from sqlalchemy import func

from app.db.models.batch_job import BatchJob
from app.db.models.llm_phrase import LLMPhrase
from app.db.models.movie_summary import MovieSummary
from app.db.models.opinion_group import OpinionGroup
from app.db.models.review import Review
from app.db.models.review_cluster_map import ReviewClusterMap
from app.db.session import SessionLocal
from app.services.labels import make_label

TOP_OPINIONS_LIMIT = 3


def _get_llm_result_dict_from_db(job_id: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        job = db.query(BatchJob).filter(BatchJob.job_id == job_id).one_or_none()
        if job is None:
            return None

        phrases = (
            db.query(LLMPhrase)
            .filter(LLMPhrase.job_id == job_id)
            .order_by(LLMPhrase.review_id, LLMPhrase.phrase_id)
            .all()
        )
        if not phrases:
            return None

        grouped = defaultdict(list)
        for p in phrases:
            grouped[p.review_id].append({"text": p.text, "sentiment": p.sentiment})

        results = [
            {"review_id": review_id, "phrases": ph_list}
            for review_id, ph_list in grouped.items()
        ]

        return {
            "job_id": job.job_id,
            "movie_id": job.movie_id,
            "movie_title": job.movie_title,
            "results": results,
        }
    finally:
        db.close()


def get_llm_result_by_job_id(job_id: str) -> Optional[dict]:
    return _get_llm_result_dict_from_db(job_id)


def save_llm_phrases_to_db(job_id: str, movie_id: str, result_data: dict) -> None:
    rows = []
    for item in result_data["results"]:
        review_id = item["review_id"]
        for phrase in item["phrases"]:
            rows.append(
                {
                    "job_id": job_id,
                    "review_id": review_id,
                    "movie_id": movie_id,
                    "text": phrase["text"],
                    "sentiment": phrase["sentiment"],
                }
            )

    db = SessionLocal()
    try:
        db.query(LLMPhrase).filter(LLMPhrase.job_id == job_id).delete(
            synchronize_session=False
        )
        if rows:
            db.bulk_insert_mappings(LLMPhrase, rows)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_llm_phrases_by_job_id(job_id: str) -> List[LLMPhrase]:
    db = SessionLocal()
    try:
        return (
            db.query(LLMPhrase)
            .filter(LLMPhrase.job_id == job_id)
            .order_by(LLMPhrase.review_id, LLMPhrase.phrase_id)
            .all()
        )
    finally:
        db.close()


def _get_cluster_result_dict_from_db(job_id: str) -> Optional[dict]:
    db = SessionLocal()
    try:
        job = db.query(BatchJob).filter(BatchJob.job_id == job_id).one_or_none()
        if job is None:
            return None

        groups = (
            db.query(OpinionGroup)
            .filter(OpinionGroup.job_id == job_id)
            .order_by(OpinionGroup.count.desc(), OpinionGroup.cluster_id)
            .all()
        )
        if not groups:
            return None

        clusters = [
            {
                "cluster_id": g.cluster_id,
                "topic": g.topic,
                "sentiment": g.sentiment,
                "count": g.count,
                "review_count": g.review_count,
                "phrases": g.phrases,
            }
            for g in groups
        ]

        return {
            "job_id": job.job_id,
            "movie_id": job.movie_id,
            "movie_title": job.movie_title,
            "clusters": clusters,
        }
    finally:
        db.close()


def get_cluster_result_by_job_id(job_id: str):
    return _get_cluster_result_dict_from_db(job_id)


def save_opinion_groups_to_db(job_id: str, movie_id: str, cluster_result: dict) -> None:
    rows = []
    for cluster in cluster_result["clusters"]:
        topic = cluster["topic"]
        sentiment = cluster["sentiment"]
        rows.append(
            {
                "job_id": job_id,
                "cluster_id": cluster["cluster_id"],
                "movie_id": movie_id,
                "topic": topic,
                "sentiment": sentiment,
                "label": make_label(topic, sentiment),
                "count": cluster["count"],
                "review_count": cluster["review_count"],
                "phrases": cluster["phrases"],
            }
        )

    db = SessionLocal()
    try:
        db.query(ReviewClusterMap).filter(ReviewClusterMap.job_id == job_id).delete(
            synchronize_session=False
        )
        db.query(OpinionGroup).filter(OpinionGroup.job_id == job_id).delete(
            synchronize_session=False
        )
        if rows:
            db.bulk_insert_mappings(OpinionGroup, rows)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def save_review_cluster_map_to_db(job_id: str, mapping: list[dict]) -> None:
    db = SessionLocal()
    try:
        db.query(ReviewClusterMap).filter(ReviewClusterMap.job_id == job_id).delete(
            synchronize_session=False
        )
        if mapping:
            db.bulk_insert_mappings(ReviewClusterMap, mapping)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_opinion_group_list_from_db(job_id: str) -> Optional[List[dict]]:
    db = SessionLocal()
    try:
        groups = (
            db.query(OpinionGroup)
            .filter(OpinionGroup.job_id == job_id)
            .order_by(OpinionGroup.count.desc(), OpinionGroup.cluster_id)
            .all()
        )
        if not groups:
            return None

        return [
            {
                "cluster_id": g.cluster_id,
                "topic": g.topic,
                "sentiment": g.sentiment,
                "label": g.label,
                "count": g.count,
            }
            for g in groups
        ]
    finally:
        db.close()


def get_opinion_group_meta_from_db(
    job_id: str, cluster_id: str
) -> Optional[dict]:
    db = SessionLocal()
    try:
        g = (
            db.query(OpinionGroup)
            .filter(OpinionGroup.job_id == job_id)
            .filter(OpinionGroup.cluster_id == cluster_id)
            .one_or_none()
        )
        if g is None:
            return None
        return {
            "cluster_id": g.cluster_id,
            "topic": g.topic,
            "sentiment": g.sentiment,
            "label": g.label,
            "count": g.count,
            "review_count": g.review_count,
        }
    finally:
        db.close()


def get_paginated_reviews_for_cluster_from_db(
    job_id: str,
    cluster_id: str,
    page: int,
    page_size: int,
) -> tuple[Optional[List[dict]], int]:
    db = SessionLocal()
    try:
        total_count = (
            db.query(func.count())
            .select_from(ReviewClusterMap)
            .filter(ReviewClusterMap.job_id == job_id)
            .filter(ReviewClusterMap.cluster_id == cluster_id)
            .scalar()
        )

        if total_count == 0:
            return None, 0

        offset = (page - 1) * page_size
        rows = (
            db.query(Review.review_id, Review.text)
            .join(ReviewClusterMap, ReviewClusterMap.review_id == Review.review_id)
            .filter(ReviewClusterMap.job_id == job_id)
            .filter(ReviewClusterMap.cluster_id == cluster_id)
            .order_by(Review.review_id)
            .offset(offset)
            .limit(page_size)
            .all()
        )

        reviews = [{"review_id": r.review_id, "text": r.text} for r in rows]
        return reviews, total_count
    finally:
        db.close()


def save_movie_summary_to_db(movie_id: str, sentiment_ratio: dict) -> None:
    db = SessionLocal()
    try:
        existing = (
            db.query(MovieSummary).filter(MovieSummary.movie_id == movie_id).one_or_none()
        )
        if existing is None:
            db.add(
                MovieSummary(
                    movie_id=movie_id,
                    positive_percent=sentiment_ratio["positive_percent"],
                    negative_percent=sentiment_ratio["negative_percent"],
                    positive_review_count=sentiment_ratio["positive_review_count"],
                    negative_review_count=sentiment_ratio["negative_review_count"],
                    tie_review_count=sentiment_ratio["tie_review_count"],
                    total_review_count=sentiment_ratio["total_review_count"],
                )
            )
        else:
            existing.positive_percent = sentiment_ratio["positive_percent"]
            existing.negative_percent = sentiment_ratio["negative_percent"]
            existing.positive_review_count = sentiment_ratio["positive_review_count"]
            existing.negative_review_count = sentiment_ratio["negative_review_count"]
            existing.tie_review_count = sentiment_ratio["tie_review_count"]
            existing.total_review_count = sentiment_ratio["total_review_count"]
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_final_result_dict_from_db(job_id: str) -> Optional[dict]:
    cluster_dict = _get_cluster_result_dict_from_db(job_id)
    if cluster_dict is None:
        return None

    llm_dict = _get_llm_result_dict_from_db(job_id)
    if llm_dict is None:
        return None

    from app.services.final_service import calculate_sentiment_ratio

    top_opinions = []
    for idx, cluster in enumerate(cluster_dict["clusters"][:TOP_OPINIONS_LIMIT], start=1):
        top_opinions.append(
            {
                "rank": idx,
                "topic": cluster["topic"],
                "sentiment": cluster["sentiment"],
                "label": make_label(cluster["topic"], cluster["sentiment"]),
                "count": cluster["count"],
            }
        )

    sentiment_ratio = calculate_sentiment_ratio(llm_dict).model_dump(mode="json")

    return {
        "job_id": cluster_dict["job_id"],
        "movie_id": cluster_dict["movie_id"],
        "movie_title": cluster_dict["movie_title"],
        "summary": {
            "top_opinions": top_opinions,
            "sentiment_ratio": sentiment_ratio,
        },
    }


def get_final_result_by_job_id(job_id: str):
    return _get_final_result_dict_from_db(job_id)