"""전체 재처리: 기존 batch_jobs + 모든 파생 데이터를 비우고,
리뷰가 있는 영화마다 최신 파이프라인(run_full_pipeline)으로 job 1개씩 새로 생성.

- 보존: movies, reviews (원본)
- 삭제: review_cluster_map, opinion_groups, llm_phrases, movie_summary, batch_jobs
- 재생성: 영화별 새 job 1개 (LLM=openai, cluster=phrase_llm)

실행:
  uv run python scripts/reprocess_all.py            # dry-run (계획만 출력)
  uv run python scripts/reprocess_all.py --apply    # 실제 실행
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import func  # noqa: E402

from app.db.models.batch_job import BatchJob  # noqa: E402
from app.db.models.llm_phrase import LLMPhrase  # noqa: E402
from app.db.models.movie_summary import MovieSummary  # noqa: E402
from app.db.models.opinion_group import OpinionGroup  # noqa: E402
from app.db.models.review import Review  # noqa: E402
from app.db.models.review_cluster_map import ReviewClusterMap  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.job_service import run_full_pipeline  # noqa: E402

# 큰 영화도 truncate되지 않도록 충분히 크게.
REVIEW_LIMIT = 100_000
LLM_MODE = "openai"
CLUSTER_MODE = "phrase_llm"


def movies_with_reviews(db):
    rows = (
        db.query(Review.movie_id, func.count(Review.review_id))
        .group_by(Review.movie_id)
        .having(func.count(Review.review_id) > 0)
        .all()
    )
    # 리뷰 많은 순 → 진행 상황 파악 쉽게 작은 것부터 처리
    return sorted(rows, key=lambda r: r[1])


def main(apply: bool):
    db = SessionLocal()
    try:
        targets = movies_with_reviews(db)
        counts = {
            "batch_jobs": db.query(func.count()).select_from(BatchJob).scalar(),
            "llm_phrases": db.query(func.count()).select_from(LLMPhrase).scalar(),
            "opinion_groups": db.query(func.count()).select_from(OpinionGroup).scalar(),
            "review_cluster_map": db.query(func.count()).select_from(ReviewClusterMap).scalar(),
            "movie_summary": db.query(func.count()).select_from(MovieSummary).scalar(),
        }
    finally:
        db.close()

    total_reviews = sum(c for _, c in targets)
    print("=== PLAN ===")
    print("삭제 대상 (현재 row 수):")
    for k, v in counts.items():
        print(f"  {k:20s}: {v}")
    print(f"\n재생성 대상 영화 {len(targets)}개, 총 리뷰 {total_reviews}개 "
          f"(LLM={LLM_MODE}, cluster={CLUSTER_MODE}):")
    for mid, cnt in targets:
        print(f"  {mid:18s} reviews={cnt}")

    if not apply:
        print("\n[dry-run] --apply 를 붙이면 실제 실행됩니다. 아무것도 변경하지 않았습니다.")
        return

    # 1) 파생 데이터 + 기존 job 삭제 (FK 안전 순서)
    print("\n=== DELETE ===")
    db = SessionLocal()
    try:
        for model in (ReviewClusterMap, OpinionGroup, LLMPhrase, MovieSummary, BatchJob):
            n = db.query(model).delete(synchronize_session=False)
            print(f"  deleted {model.__tablename__}: {n}")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    # 2) 영화별 새 job 1개 + 전체 파이프라인
    print("\n=== REPROCESS ===")
    results = []
    for mid, cnt in targets:
        print(f"  -> {mid} (reviews={cnt}) ...", flush=True)
        try:
            job = run_full_pipeline(
                movie_id=mid,
                llm_mode=LLM_MODE,
                cluster_mode=CLUSTER_MODE,
                review_limit=REVIEW_LIMIT,
            )
            print(f"     OK {job.job_id} status={job.status}", flush=True)
            results.append((mid, job.job_id, job.status))
        except Exception as e:
            print(f"     FAILED {mid}: {e}", flush=True)
            results.append((mid, None, f"FAILED: {e}"))

    print("\n=== DONE ===")
    for mid, jid, status in results:
        print(f"  {mid:18s} {jid or '-':10s} {status}")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
