"""
End-to-end pipeline 회귀 가드.

POST /batch/jobs → run-llm → run-cluster → build-final 전체 흐름을 자동 실행 후
read endpoint으로 결과 검증. 끝에 테스트 잡 흔적을 5개 저장소에서 정리하여
반복 실행해도 누적되지 않음.

성공 시 exit 0, 하나라도 실패 시 exit 1.
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from app.db.models.batch_job import BatchJob  # noqa: E402
from app.db.models.llm_phrase import LLMPhrase  # noqa: E402
from app.db.models.opinion_group import OpinionGroup  # noqa: E402
from app.db.models.review_cluster_map import ReviewClusterMap  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas import (  # noqa: E402
    ClusterResponseSchema,
    FinalResultSchema,
    LLMResponseSchema,
    OpinionGroupListResponse,
    OpinionGroupReviewsResponse,
)

client = TestClient(app)

TEST_MOVIE_ID = "mv_001"
TEST_TARGET_DATE = "2026-05-10"
TEST_REVIEW_LIMIT = 10
TEST_CLUSTER_MODE = "hdbscan"
TEST_LLM_MODE = "rule_based"

JSON_PATHS: dict = {}  # all dual-write JSON paths sunsetted post-Stage 4

results: list[tuple[str, bool, str | None]] = []


def record(name: str, ok: bool, msg: str | None = None) -> None:
    results.append((name, ok, msg))
    if ok:
        print(f"  [PASS] {name}")
    else:
        print(f"  [FAIL] {name}: {msg}")


def _cleanup_db(job_id: str) -> dict:
    counts = {}
    db = SessionLocal()
    try:
        counts["review_cluster_map"] = (
            db.query(ReviewClusterMap)
            .filter(ReviewClusterMap.job_id == job_id)
            .delete(synchronize_session=False)
        )
        counts["opinion_groups"] = (
            db.query(OpinionGroup)
            .filter(OpinionGroup.job_id == job_id)
            .delete(synchronize_session=False)
        )
        counts["llm_phrases"] = (
            db.query(LLMPhrase)
            .filter(LLMPhrase.job_id == job_id)
            .delete(synchronize_session=False)
        )
        counts["batch_jobs"] = (
            db.query(BatchJob)
            .filter(BatchJob.job_id == job_id)
            .delete(synchronize_session=False)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return counts


def _cleanup_json(job_id: str) -> dict:
    counts = {}
    for key, path in JSON_PATHS.items():
        if not path.exists():
            counts[key] = 0
            continue
        items = json.loads(path.read_text(encoding="utf-8"))
        before = len(items)
        items = [it for it in items if it.get("job_id") != job_id]
        path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        counts[key] = before - len(items)
    return counts


def cleanup(job_id: str) -> None:
    if job_id is None:
        return
    print(f"\n--- cleanup test job_id={job_id} ---")
    db_counts = _cleanup_db(job_id)
    print(f"  db rows deleted: {db_counts}")
    json_counts = _cleanup_json(job_id)
    print(f"  json entries removed: {json_counts}")


def main() -> int:
    test_job_id: str | None = None
    expected_clusters: int | None = None
    expected_review_count: int | None = None
    sample_cluster_id: str | None = None

    print("=== Pipeline e2e ===")

    try:
        # Step 1: create
        r = client.post(
            "/batch/jobs",
            json={"movie_id": TEST_MOVIE_ID, "target_date": TEST_TARGET_DATE},
        )
        if r.status_code != 200:
            record("POST /batch/jobs", False, f"status={r.status_code}, body={r.text}")
            return 1
        body = r.json()
        test_job_id = body["job_id"]
        record("POST /batch/jobs", True)

        db = SessionLocal()
        try:
            row = (
                db.query(BatchJob).filter(BatchJob.job_id == test_job_id).one_or_none()
            )
            record(
                "batch_jobs row created",
                row is not None,
                None if row else "row not found in DB",
            )
        finally:
            db.close()

        # Step 2: run-llm
        r = client.post(
            f"/batch/jobs/{test_job_id}/run-llm",
            params={
                "review_limit": TEST_REVIEW_LIMIT,
                "source_mode": "dataset",
                "llm_mode": TEST_LLM_MODE,
            },
        )
        if r.status_code != 200:
            record("POST run-llm", False, f"status={r.status_code}, body={r.text}")
            return 1
        body = r.json()
        record(
            "POST run-llm",
            len(body["results"]) == TEST_REVIEW_LIMIT,
            f"results={len(body['results'])}, expected={TEST_REVIEW_LIMIT}",
        )
        expected_review_count = TEST_REVIEW_LIMIT

        db = SessionLocal()
        try:
            n = (
                db.query(LLMPhrase)
                .filter(LLMPhrase.job_id == test_job_id)
                .count()
            )
            record(
                "llm_phrases populated",
                n > 0,
                None if n > 0 else "no phrases in DB",
            )
        finally:
            db.close()

        # Step 3: run-cluster
        r = client.post(
            f"/batch/jobs/{test_job_id}/run-cluster",
            params={"cluster_mode": TEST_CLUSTER_MODE},
        )
        if r.status_code != 200:
            record("POST run-cluster", False, f"status={r.status_code}, body={r.text}")
            return 1
        body = r.json()
        expected_clusters = len(body["clusters"])
        record(
            "POST run-cluster",
            expected_clusters > 0,
            None if expected_clusters > 0 else "no clusters returned",
        )
        if body["clusters"]:
            sample_cluster_id = body["clusters"][0]["cluster_id"]

        db = SessionLocal()
        try:
            n = (
                db.query(OpinionGroup)
                .filter(OpinionGroup.job_id == test_job_id)
                .count()
            )
            record(
                "opinion_groups populated",
                n == expected_clusters,
                f"db={n}, expected={expected_clusters}",
            )
        finally:
            db.close()

        # Step 4: build-final
        r = client.post(f"/batch/jobs/{test_job_id}/build-final")
        if r.status_code != 200:
            record("POST build-final", False, f"status={r.status_code}, body={r.text}")
            return 1
        body = r.json()
        has_summary = (
            "summary" in body
            and "top_opinions" in body["summary"]
            and "sentiment_ratio" in body["summary"]
        )
        record(
            "POST build-final",
            has_summary,
            None if has_summary else "summary structure missing",
        )

        db = SessionLocal()
        try:
            n = (
                db.query(ReviewClusterMap)
                .filter(ReviewClusterMap.job_id == test_job_id)
                .count()
            )
            record(
                "review_cluster_map populated",
                n > 0,
                None if n > 0 else "no rcm rows",
            )
        finally:
            db.close()

        # Step 5: GET endpoint validations
        r = client.get(f"/batch/jobs/{test_job_id}/llm-result")
        try:
            assert r.status_code == 200
            LLMResponseSchema.model_validate(r.json())
            record("GET llm-result schema", True)
        except Exception as e:
            record("GET llm-result schema", False, str(e))

        r = client.get(f"/batch/jobs/{test_job_id}/cluster-result")
        try:
            assert r.status_code == 200
            ClusterResponseSchema.model_validate(r.json())
            record("GET cluster-result schema", True)
        except Exception as e:
            record("GET cluster-result schema", False, str(e))

        r = client.get(f"/batch/jobs/{test_job_id}/final-result")
        try:
            assert r.status_code == 200
            body = r.json()
            FinalResultSchema.model_validate(body)
            assert (
                body["summary"]["sentiment_ratio"]["total_review_count"]
                == TEST_REVIEW_LIMIT
            ), f"total_review_count={body['summary']['sentiment_ratio']['total_review_count']}"
            record("GET final-result schema + total_review_count", True)
        except Exception as e:
            record("GET final-result schema + total_review_count", False, str(e))

        r = client.get(f"/batch/jobs/{test_job_id}/opinion-groups")
        try:
            assert r.status_code == 200
            body = r.json()
            OpinionGroupListResponse.model_validate(body)
            assert (
                len(body["items"]) == expected_clusters
            ), f"items={len(body['items'])}, expected={expected_clusters}"
            record("GET opinion-groups items count matches", True)
        except Exception as e:
            record("GET opinion-groups items count matches", False, str(e))

        if sample_cluster_id:
            r = client.get(
                f"/batch/jobs/{test_job_id}/opinion-groups/{sample_cluster_id}/reviews",
                params={"page": 1, "page_size": 5},
            )
            try:
                assert r.status_code == 200
                body = r.json()
                OpinionGroupReviewsResponse.model_validate(body)
                assert body["page"] == 1
                assert body["page_size"] == 5
                record("GET opinion-group reviews paginated", True)
            except Exception as e:
                record("GET opinion-group reviews paginated", False, str(e))

    finally:
        cleanup(test_job_id)

    print()
    fails = [r for r in results if not r[1]]
    if fails:
        print(f"verify_pipeline_e2e: FAIL ({len(fails)} case(s))")
        return 1
    print(f"verify_pipeline_e2e: PASS ({len(results)} case(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
