"""movies 테이블의 CGV 코드 보유 영화 전체에 대해 일일배치를 직접 수행.

기본 일일배치(refresh_all_subscribed_movies)는 '구독된' 영화만 돌지만,
이 스크립트는 movies 전체를 대상으로 한다.

각 영화:
  1) run_collection_now(depth='full')로 CGV 재수집 (공유 브라우저)
  2) 새 리뷰(total_inserted>0)가 있으면 run_full_pipeline로 분석

reviews/movies 원본 보존, 분석 파생물만 영화별 새 job으로 갱신.
실패는 영화 단위로 건너뛰며 배치 전체를 멈추지 않는다.

실행:
  uv run python scripts/batch_all_movies.py            # dry-run (대상만 출력)
  uv run python scripts/batch_all_movies.py --apply    # 실제 실행
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.collectors.selected_review_collector import CGVReviewClient  # noqa: E402
from app.db.models.movie import Movie  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services import collection_service, job_service  # noqa: E402


def targets():
    db = SessionLocal()
    try:
        movies = db.query(Movie).order_by(Movie.movie_id).all()
        # source 는 메타데이터 출처(kobis/naver)지 수집처가 아니다.
        # CGV 수집 대상 = cgv_movie_code 보유 AND naver 시드가 아닌 영화.
        # naver 영화(mv_001/mv_002)의 코드는 CGV 코드가 아니므로 제외한다.
        return [
            (m.movie_id, m.cgv_movie_code, m.movie_title)
            for m in movies
            if m.cgv_movie_code and m.source != "naver"
        ]
    finally:
        db.close()


def main(apply: bool):
    rows = targets()
    print(f"=== 대상: CGV 코드 보유 영화 {len(rows)}개 ===")
    for mid, code, title in rows:
        print(f"  {mid:18s} cgv={code:10s} {title}")

    if not apply:
        print("\n[dry-run] --apply 를 붙이면 실제 수집+분석을 실행합니다.")
        return

    summary = {"attempted": 0, "collected": 0, "collect_failed": 0,
               "analyzed": 0, "analysis_failed": 0, "no_new": 0}

    shared = None
    try:
        shared = CGVReviewClient()
        shared._ensure_started()
        print("\n[batch] 공유 CGV 브라우저 시작됨")
    except Exception as e:
        print(f"\n[batch] 공유 브라우저 시작 실패, 영화별 개별 클라이언트로 진행: {e}")
        shared = None

    try:
        for i, (mid, code, title) in enumerate(rows, 1):
            summary["attempted"] += 1
            print(f"\n[{i}/{len(rows)}] {mid} ({title}) 수집 시작...", flush=True)
            try:
                job = collection_service.run_collection_now(
                    movie_id=mid,
                    cgv_movie_code=code,
                    source="cgv",
                    mode="scheduled",
                    depth="full",
                    cgv_client=shared,
                )
            except Exception as e:
                print(f"     수집 실패: {e}", flush=True)
                summary["collect_failed"] += 1
                continue

            if job.status != "completed":
                print(f"     수집 실패(status={job.status}): {job.error_message}", flush=True)
                summary["collect_failed"] += 1
                continue

            summary["collected"] += 1
            print(f"     수집 완료: fetched={job.total_fetched} inserted={job.total_inserted}", flush=True)

            if job.total_inserted == 0:
                print("     새 리뷰 없음 → 분석 스킵", flush=True)
                summary["no_new"] += 1
                continue

            print("     분석 파이프라인 실행...", flush=True)
            try:
                bj = job_service.run_full_pipeline(movie_id=mid)
                print(f"     분석 완료: {bj.job_id} ({bj.status})", flush=True)
                summary["analyzed"] += 1
            except Exception as e:
                print(f"     분석 실패: {e}", flush=True)
                summary["analysis_failed"] += 1
    finally:
        if shared is not None:
            try:
                shared.close()
            except Exception:
                pass

    print("\n=== DONE ===")
    for k, v in summary.items():
        print(f"  {k:18s}: {v}")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
