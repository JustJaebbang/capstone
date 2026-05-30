import logging
from datetime import date, datetime
from typing import List, Optional

from app.db.models.batch_job import BatchJob
from app.db.models.movie import Movie
from app.db.session import SessionLocal
from app.schemas import (
    BatchJobSchema,
    CreateBatchJobRequest,
    LLMRequestSchema,
    OpinionReviewItem,
    ReviewItem,
    OpinionGroupListItem,
    OpinionGroupListResponse,
    OpinionGroupReviewsResponse,
)

logger = logging.getLogger(__name__)
from app.services.llm_service import extract_phrases_with_sentiment
from app.services.cluster_service import build_cluster_request_for_job, run_cluster_module
from app.services.topic_service import reclassify_etc_clusters
from app.services.review_service import fetch_reviews
from app.services.result_service import (
    save_llm_phrases_to_db,
    save_opinion_groups_to_db,
    save_review_cluster_map_to_db,
    save_movie_summary_to_db,
    update_opinion_group_labels_to_db,
    get_llm_result_by_job_id,
    get_cluster_result_by_job_id,
    get_opinion_group_list_from_db,
    get_opinion_group_meta_from_db,
    get_paginated_reviews_for_cluster_from_db,
)

from app.services.final_service import (
    build_final_result,
    collect_reviews_for_cluster,
)


def _batchjob_to_schema(row: BatchJob) -> BatchJobSchema:
    return BatchJobSchema(
        job_id=row.job_id,
        movie_id=row.movie_id,
        movie_title=row.movie_title,
        target_date=row.target_date,
        status=row.status,
        created_at=row.created_at,
        started_at=row.started_at,
        finished_at=row.finished_at,
    )


def list_jobs() -> List[BatchJobSchema]:
    db = SessionLocal()
    try:
        rows = db.query(BatchJob).order_by(BatchJob.job_id).all()
        return [_batchjob_to_schema(r) for r in rows]
    finally:
        db.close()


def get_job(job_id: str) -> Optional[BatchJobSchema]:
    db = SessionLocal()
    try:
        row = db.query(BatchJob).filter(BatchJob.job_id == job_id).one_or_none()
        if row is None:
            return None
        return _batchjob_to_schema(row)
    finally:
        db.close()


def _next_job_id(db) -> str:
    existing = [row[0] for row in db.query(BatchJob.job_id).all()]
    max_n = 0
    for jid in existing:
        try:
            n = int(jid.split("_", 1)[1])
        except (IndexError, ValueError):
            continue
        if n > max_n:
            max_n = n
    return f"job_{max_n+1:03d}"


def create_job(payload: CreateBatchJobRequest, movie_title: str) -> BatchJobSchema:
    db = SessionLocal()
    try:
        new_job = BatchJobSchema(
            job_id=_next_job_id(db),
            movie_id=payload.movie_id,
            movie_title=movie_title,
            target_date=payload.target_date,
            status="queued",
            created_at=datetime.now(),
            started_at=None,
            finished_at=None,
        )
        db.add(
            BatchJob(
                job_id=new_job.job_id,
                movie_id=new_job.movie_id,
                movie_title=new_job.movie_title,
                target_date=new_job.target_date,
                status=new_job.status,
                created_at=new_job.created_at,
                started_at=new_job.started_at,
                finished_at=new_job.finished_at,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return new_job


def update_job_status(job_id: str, new_status: str) -> None:
    db = SessionLocal()
    try:
        db_job = db.query(BatchJob).filter(BatchJob.job_id == job_id).one_or_none()
        if db_job is None:
            raise ValueError(f"Job not found: {job_id}")

        db_job.status = new_status

        if new_status != "queued" and db_job.started_at is None:
            db_job.started_at = datetime.now()

        if new_status in ("completed", "failed"):
            db_job.finished_at = datetime.now()

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def build_llm_request(
    job,
    review_limit: int = 50,
    ) -> LLMRequestSchema:
    """
    DB의 reviews 테이블에서 리뷰를 읽어 B -> C 요청 스키마로 변환한다.
    """
    source_reviews = fetch_reviews(
        movie_id=job.movie_id,
        review_limit=review_limit,
    )

    reviews = [
        ReviewItem(
            review_id=review.review_id,
            text=review.text,
        )
        for review in source_reviews
    ]

    return LLMRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        reviews=reviews,
    )


def run_llm_for_job(
    job,
    review_limit: int = 50,
    llm_mode: str = "openai",
    ) -> dict:
    """
    DB의 reviews -> B -> C -> B 전체 실행
    """
    # 1. DB에서 리뷰를 읽고 B → C 스키마 생성
    llm_request = build_llm_request(
        job=job,
        review_limit=review_limit,
        )
    payload = llm_request.model_dump(mode="json")

    print(f"[Pipeline] llm_mode = {llm_mode}")
    
    total_reviews = len(payload["reviews"])
    print(f"[Pipeline] selected reviews = {total_reviews}")

    # 2. C 호출
    llm_response = extract_phrases_with_sentiment(llm_request, mode=llm_mode)
    llm_result = llm_response.model_dump(mode="json")
    
    # 3. 입력 리뷰 수 == 출력 결과 수 검증
    input_count = len(payload["reviews"])
    output_count = len(llm_result["results"])

    if input_count != output_count:
        raise ValueError(
            f"LLM result count mismatch: input={input_count}, output={output_count}"
        )
    
    save_llm_phrases_to_db(
        job_id=job.job_id,
        movie_id=job.movie_id,
        result_data=llm_result,
    )
    print(f"[Pipeline] llm results received: {output_count}")
    print("[Pipeline] llm_phrases saved (db)")
    
    return llm_result


def run_cluster_for_job(
    job,
    cluster_mode: str = "phrase_llm",
    reclassify_etc: bool = False,
) -> dict:
    cluster_request = build_cluster_request_for_job(job)

    cluster_response = run_cluster_module(cluster_request, mode=cluster_mode)
    # phrase_llm은 phrase별로 이미 17-set 분류를 끝내므로 기본적으로 2차
    # "기타" 재분류를 돌리지 않는다(중복 토픽 생성·억지 분류 방지). 자유토픽
    # 모드(hdbscan/kmeans)에서 의미가 있으니 reclassify_etc=True로 켤 수 있다.
    if reclassify_etc:
        cluster_response = reclassify_etc_clusters(cluster_response)
    cluster_result = cluster_response.model_dump(mode="json")

    save_opinion_groups_to_db(
        job_id=job.job_id,
        movie_id=job.movie_id,
        cluster_result=cluster_result,
    )

    return cluster_result


def run_final_for_job(job) -> dict:
    llm_result = get_llm_result_by_job_id(job.job_id)
    if llm_result is None:
        raise ValueError(f"LLM result not found for job_id={job.job_id}")

    cluster_result = get_cluster_result_by_job_id(job.job_id)
    if cluster_result is None:
        raise ValueError(f"Cluster result not found for job_id={job.job_id}")

    source_reviews = fetch_reviews(
        movie_id=job.movie_id,
        review_limit=1000,
    )

    source_reviews_data = [
        {
            "review_id": review.review_id,
            "text": review.text,
        }
        for review in source_reviews
    ]

    final_response = build_final_result(
        job=job,
        llm_result=llm_result,
        cluster_result=cluster_result,
        source_reviews=source_reviews_data,
    )

    final_result = final_response.model_dump(mode="json")

    mapping_rows = []
    for cluster in cluster_result["clusters"]:
        matched = collect_reviews_for_cluster(
            cluster=cluster,
            llm_result=llm_result,
            source_reviews=source_reviews_data,
        )
        for review in matched:
            mapping_rows.append(
                {
                    "job_id": job.job_id,
                    "cluster_id": cluster["cluster_id"],
                    "review_id": review.review_id,
                }
            )

    save_review_cluster_map_to_db(job_id=job.job_id, mapping=mapping_rows)
    save_movie_summary_to_db(
        movie_id=job.movie_id,
        sentiment_ratio=final_result["summary"]["sentiment_ratio"],
    )

    # build_final_result가 만든 top_opinions LLM 라벨을 opinion_groups.label에 반영.
    # top_opinions는 cluster_result["clusters"][:3]와 동일 순서이므로 인덱스로 매핑.
    top_clusters = cluster_result["clusters"][:len(final_result["summary"]["top_opinions"])]
    label_by_cluster_id = {
        cluster["cluster_id"]: opinion["label"]
        for cluster, opinion in zip(top_clusters, final_result["summary"]["top_opinions"])
    }
    update_opinion_group_labels_to_db(job.job_id, label_by_cluster_id)

    return final_result


def get_opinion_group_reviews(
    job,
    cluster_id: str,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    if page < 1:
        raise ValueError("page must be >= 1")

    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    meta = get_opinion_group_meta_from_db(job.job_id, cluster_id)
    if meta is None:
        raise ValueError(f"Cluster not found: {cluster_id}")

    paged_rows, total_count = get_paginated_reviews_for_cluster_from_db(
        job_id=job.job_id,
        cluster_id=cluster_id,
        page=page,
        page_size=page_size,
    )

    total_pages = (
        (total_count + page_size - 1) // page_size if total_count > 0 else 1
    )

    return OpinionGroupReviewsResponse(
        job_id=job.job_id,
        cluster_id=cluster_id,
        label=meta["label"],
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        reviews=[OpinionReviewItem(**row) for row in (paged_rows or [])],
    ).model_dump(mode="json")


def get_opinion_groups(job) -> dict:
    db_items = get_opinion_group_list_from_db(job.job_id)
    if db_items is None:
        raise ValueError(f"Opinion groups not found for job_id={job.job_id}")

    return OpinionGroupListResponse(
        job_id=job.job_id,
        items=[OpinionGroupListItem(**item) for item in db_items],
        total_count=len(db_items),
    ).model_dump(mode="json")


def run_full_pipeline(
    movie_id: str,
    target_date: Optional[date] = None,
    llm_mode: str = "openai",
    cluster_mode: str = "phrase_llm",
    reclassify_etc: bool = False,
    review_limit: int = 1000,
) -> BatchJobSchema:
    """One-shot pipeline: create batch_job -> LLM -> cluster -> final.

    Used by:
    - scheduler nightly batch (after fresh review collection)
    - API run-now-with-analysis path
    - any other internal trigger that needs the full pipeline

    Reads reviews from the DB only (toclaude2 §"기존 분석 파이프라인 연결 원칙").
    The pipeline is unaware of which collector populated the reviews — that
    separation is preserved.

    Raises ValueError if the movie isn't in the movies table.
    """
    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).one_or_none()
        if movie is None:
            raise ValueError(f"movie_id '{movie_id}' not found in movies table")
        movie_title = movie.movie_title
    finally:
        db.close()

    if target_date is None:
        target_date = date.today()

    payload = CreateBatchJobRequest(movie_id=movie_id, target_date=target_date)
    job = create_job(payload, movie_title=movie_title)
    logger.info("pipeline created batch_job %s for movie %s", job.job_id, movie_id)

    try:
        update_job_status(job.job_id, "llm_processing")
        run_llm_for_job(job, review_limit=review_limit, llm_mode=llm_mode)

        update_job_status(job.job_id, "clustering")
        run_cluster_for_job(job, cluster_mode=cluster_mode, reclassify_etc=reclassify_etc)

        update_job_status(job.job_id, "saving_results")
        run_final_for_job(job)

        update_job_status(job.job_id, "completed")
        logger.info("pipeline completed for batch_job %s", job.job_id)
    except Exception:
        logger.exception("pipeline failed for batch_job %s", job.job_id)
        try:
            update_job_status(job.job_id, "failed")
        except Exception:
            logger.exception("failed to mark job %s as failed", job.job_id)
        raise

    return get_job(job.job_id)