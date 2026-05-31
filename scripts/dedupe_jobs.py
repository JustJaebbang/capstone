"""영화별 최신 completed job 1개만 남기고, 나머지 job과 그 파생 데이터를 삭제.

중복 분석(배치 중복 실행 등)으로 한 영화에 여러 job이 쌓였을 때 정리용.
- 보존: 영화별 가장 최근 completed job (finished_at 기준, tie면 job_id)
- 삭제: 그 외 모든 batch_job + 해당 job의 llm_phrases / opinion_groups /
        review_cluster_map. (reviews, movies, movie_summary 원본은 보존)

대시보드는 항상 최신 completed job만 읽으므로 화면 결과는 불변.

실행:
  uv run python scripts/dedupe_jobs.py            # dry-run
  uv run python scripts/dedupe_jobs.py --apply    # 실제 삭제
"""

import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.db.models.batch_job import BatchJob  # noqa: E402
from app.db.models.llm_phrase import LLMPhrase  # noqa: E402
from app.db.models.opinion_group import OpinionGroup  # noqa: E402
from app.db.models.review_cluster_map import ReviewClusterMap  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


def _sort_key(job):
    # 최신 우선: finished_at 큰 것. None은 가장 뒤로.
    fa = job.finished_at
    return (fa is not None, fa, job.job_id)


def main(apply: bool):
    db = SessionLocal()
    try:
        all_jobs = db.query(BatchJob).all()
        by_movie = defaultdict(list)
        for j in all_jobs:
            by_movie[j.movie_id].append(j)

        keep_ids = set()
        delete_ids = []
        for mid, jobs in by_movie.items():
            completed = [j for j in jobs if j.status == "completed"]
            pool = completed or jobs  # completed 없으면 전체에서 최신 1개
            keeper = max(pool, key=_sort_key)
            keep_ids.add(keeper.job_id)
            for j in jobs:
                if j.job_id != keeper.job_id:
                    delete_ids.append(j.job_id)

        print(f"=== 영화 {len(by_movie)}개, 전체 job {len(all_jobs)}개 ===")
        print(f"보존(영화별 최신 1개): {len(keep_ids)}개")
        print(f"삭제 대상 job: {len(delete_ids)}개")
        for mid in sorted(by_movie):
            jobs = sorted(by_movie[mid], key=_sort_key, reverse=True)
            keeper = jobs[0].job_id
            others = [j.job_id for j in jobs[1:]]
            if others:
                print(f"  {mid:18s} keep={keeper}  delete={others}")

        if not delete_ids:
            print("\n중복 없음 — 정리할 게 없습니다.")
            return

        if not apply:
            print("\n[dry-run] --apply 를 붙이면 위 삭제 대상 job과 파생 데이터를 제거합니다.")
            return

        # 파생 데이터부터 삭제 후 job 행 삭제.
        n_rcm = (
            db.query(ReviewClusterMap)
            .filter(ReviewClusterMap.job_id.in_(delete_ids))
            .delete(synchronize_session=False)
        )
        n_og = (
            db.query(OpinionGroup)
            .filter(OpinionGroup.job_id.in_(delete_ids))
            .delete(synchronize_session=False)
        )
        n_ph = (
            db.query(LLMPhrase)
            .filter(LLMPhrase.job_id.in_(delete_ids))
            .delete(synchronize_session=False)
        )
        n_job = (
            db.query(BatchJob)
            .filter(BatchJob.job_id.in_(delete_ids))
            .delete(synchronize_session=False)
        )
        db.commit()
        print("\n=== DELETED ===")
        print(f"  review_cluster_map : {n_rcm}")
        print(f"  opinion_groups     : {n_og}")
        print(f"  llm_phrases        : {n_ph}")
        print(f"  batch_jobs         : {n_job}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
