"""파묘·듄을 네이버 시드(mv_00x) → KOBIS id(kobis_xxx) + CGV 소스로 전환.

파이프라인은 'KOBIS movie_id → CGV 매핑 → 수집' 구조라, 임의 시드 id인
mv_001/mv_002 형태는 이 흐름을 타지 못한다. 실제 KOBIS movieCd로 만든
새 movie 행으로 교체하고, 기존 네이버 리뷰·분석을 모두 삭제한 뒤
CGV에서 재수집·재분석한다.

각 영화:
  1) 기존 mv_00x의 파생 분석 + 리뷰 + movie 행 삭제
  2) kobis_<movieCd> 새 movie 행 생성 (source=cgv, cgv_movie_code 포함)
  3) CGV 전량 수집 + 분석 파이프라인

실행:
  uv run python scripts/migrate_naver_to_cgv.py          # dry-run
  uv run python scripts/migrate_naver_to_cgv.py --apply  # 실제 실행
"""

import sys
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.db.models.batch_job import BatchJob  # noqa: E402
from app.db.models.llm_phrase import LLMPhrase  # noqa: E402
from app.db.models.movie import Movie  # noqa: E402
from app.db.models.movie_summary import MovieSummary  # noqa: E402
from app.db.models.opinion_group import OpinionGroup  # noqa: E402
from app.db.models.review import Review  # noqa: E402
from app.db.models.review_cluster_map import ReviewClusterMap  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services import collection_service, job_service  # noqa: E402

# 전환 대상: 기존 시드 id -> (KOBIS movieCd, 제목, 개봉일, 장르, CGV 코드)
MIGRATIONS = [
    {
        "old_id": "mv_001",
        "kobis_cd": "20234675",
        "title": "파묘",
        "release_date": date(2024, 2, 22),
        "genre": "미스터리",
        "cgv_code": "88012",
    },
    {
        "old_id": "mv_002",
        "kobis_cd": "20236295",
        "title": "듄: 파트2",
        "release_date": date(2024, 2, 28),
        "genre": "액션",
        "cgv_code": "87947",
    },
]


def _delete_movie_data(db, movie_id: str) -> dict:
    """movie_id에 연결된 모든 파생 + 리뷰 + movie 행 삭제."""
    job_ids = [j.job_id for j in db.query(BatchJob.job_id).filter(BatchJob.movie_id == movie_id).all()]
    counts = {}
    if job_ids:
        counts["review_cluster_map"] = db.query(ReviewClusterMap).filter(
            ReviewClusterMap.job_id.in_(job_ids)).delete(synchronize_session=False)
        counts["opinion_groups"] = db.query(OpinionGroup).filter(
            OpinionGroup.job_id.in_(job_ids)).delete(synchronize_session=False)
        counts["llm_phrases"] = db.query(LLMPhrase).filter(
            LLMPhrase.job_id.in_(job_ids)).delete(synchronize_session=False)
        counts["batch_jobs"] = db.query(BatchJob).filter(
            BatchJob.job_id.in_(job_ids)).delete(synchronize_session=False)
    counts["movie_summary"] = db.query(MovieSummary).filter(
        MovieSummary.movie_id == movie_id).delete(synchronize_session=False)
    counts["reviews"] = db.query(Review).filter(
        Review.movie_id == movie_id).delete(synchronize_session=False)
    counts["movies"] = db.query(Movie).filter(
        Movie.movie_id == movie_id).delete(synchronize_session=False)
    return counts


def main(apply: bool):
    db = SessionLocal()
    try:
        print("=== 전환 계획 ===")
        for mg in MIGRATIONS:
            old = db.query(Movie).filter(Movie.movie_id == mg["old_id"]).one_or_none()
            rev = db.query(Review).filter(Review.movie_id == mg["old_id"]).count()
            new_id = f"kobis_{mg['kobis_cd']}"
            exists = db.query(Movie).filter(Movie.movie_id == new_id).one_or_none() is not None
            print(f"  {mg['old_id']} ({old.movie_title if old else '?'}, naver, reviews={rev})")
            print(f"    -> {new_id} (source=cgv, cgv_code={mg['cgv_code']}, title={mg['title']!r})"
                  + ("  [경고: 새 id 이미 존재!]" if exists else ""))

        if not apply:
            print("\n[dry-run] --apply 를 붙이면: 네이버 데이터 삭제 → 새 kobis 행 생성 → CGV 수집+분석")
            return

        # 1) 삭제 + 2) 새 movie 행 생성 (한 트랜잭션)
        new_ids = []
        for mg in MIGRATIONS:
            print(f"\n[{mg['old_id']} -> kobis_{mg['kobis_cd']}] 네이버 데이터 삭제...", flush=True)
            counts = _delete_movie_data(db, mg["old_id"])
            print(f"    deleted: {counts}", flush=True)

            new_id = f"kobis_{mg['kobis_cd']}"
            now = datetime.utcnow()
            db.add(Movie(
                movie_id=new_id,
                movie_title=mg["title"],
                release_year=mg["release_date"].year,
                release_date=mg["release_date"],
                source="cgv",
                genre=mg["genre"],
                cgv_movie_code=mg["cgv_code"],
                registered_at=now,
                updated_at=now,
            ))
            new_ids.append((new_id, mg["cgv_code"], mg["title"]))
        db.commit()
        print("\n새 kobis movie 행 생성 완료.")
    finally:
        db.close()

    # 3) CGV 수집 + 분석 (각 영화)
    for new_id, cgv_code, title in new_ids:
        print(f"\n=== {new_id} ({title}) CGV 수집 ===", flush=True)
        job = collection_service.run_collection_now(
            movie_id=new_id, cgv_movie_code=cgv_code, source="cgv",
            mode="scheduled", depth="full",
        )
        print(f"수집 status={job.status} fetched={job.total_fetched} inserted={job.total_inserted}", flush=True)
        if job.status != "completed":
            print(f"수집 실패: {job.error_message}", flush=True)
            continue
        if job.total_inserted == 0:
            print("새 리뷰 없음 → 분석 스킵", flush=True)
            continue
        bj = job_service.run_full_pipeline(movie_id=new_id)
        print(f"분석 완료: {bj.job_id} ({bj.status})", flush=True)


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
