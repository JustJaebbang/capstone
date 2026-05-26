"""
DB 파이프라인 상태를 한 눈에 보여주는 직접 확인용 도구.

`uv run python scripts/show_db_state.py` 로 언제든 실행.
파이프라인 단계마다 row 수 변화를 눈으로 비교할 때 사용.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import desc, func, select  # noqa: E402

from app.db.models.batch_job import BatchJob  # noqa: E402
from app.db.models.llm_phrase import LLMPhrase  # noqa: E402
from app.db.models.movie_summary import MovieSummary  # noqa: E402
from app.db.models.opinion_group import OpinionGroup  # noqa: E402
from app.db.models.review_cluster_map import ReviewClusterMap  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

JSON_FILES = [
    BASE_DIR / "data" / "jobs.json",
    BASE_DIR / "data" / "llm_results.json",
    BASE_DIR / "data" / "cluster_results.json",
    BASE_DIR / "data" / "final_results.json",
]


def main():
    print("=== JSON archive (frozen - should not change after Stage 4) ===")
    for p in JSON_FILES:
        if p.exists():
            from datetime import datetime
            mtime = datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")
            size_kb = p.stat().st_size / 1024
            print(f"  {p.name:25s}  mtime={mtime}  size={size_kb:.1f}KB")
        else:
            print(f"  {p.name:25s}  (not present)")

    db = SessionLocal()
    try:
        print()
        print("=== DB row counts (live source of truth) ===")
        print(f"  batch_jobs         : {db.scalar(select(func.count()).select_from(BatchJob))}")
        print(f"  llm_phrases        : {db.scalar(select(func.count()).select_from(LLMPhrase))}")
        print(f"  opinion_groups     : {db.scalar(select(func.count()).select_from(OpinionGroup))}")
        print(f"  review_cluster_map : {db.scalar(select(func.count()).select_from(ReviewClusterMap))}")
        print(f"  movie_summary      : {db.scalar(select(func.count()).select_from(MovieSummary))}")

        print()
        print("=== Latest 5 batch_jobs ===")
        rows = db.query(BatchJob).order_by(desc(BatchJob.created_at)).limit(5).all()
        if not rows:
            print("  (none)")
        for r in rows:
            print(
                f"  {r.job_id}  movie={r.movie_id}  status={r.status:<18s}"
                f"  target_date={r.target_date}  created={r.created_at.isoformat(timespec='seconds')}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
