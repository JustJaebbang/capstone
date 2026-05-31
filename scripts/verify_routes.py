"""
HTTP 계약 회귀 가드.

FastAPI TestClient로 라우터 endpoint별 status code · 응답 shape · 에러 경로를 검증한다.
read-only + POST validation 중심. 파이프라인 mutation은 별도 e2e 대상.

성공 시 exit 0, 하나라도 실패 시 exit 1.
"""

import json
import sys
from pathlib import Path
from typing import Callable

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.schemas import (  # noqa: E402
    CreateBatchJobResponse,
    JobStatusResponse,
    LLMResponseSchema,
    ClusterResponseSchema,
    FinalResultSchema,
    MovieSchema,
    OpinionGroupListResponse,
    OpinionGroupReviewsResponse,
)


client = TestClient(app)

EXISTING_JOB = "job_058"
EXISTING_CLUSTER = "cl_001"
MISSING_JOB = "does_not_exist"
MISSING_CLUSTER = "cl_999"


Case = tuple[str, bool, str | None]


def _ok(name: str) -> Case:
    return (name, True, None)


def _fail(name: str, msg: str) -> Case:
    return (name, False, msg)


def _check(name: str, fn: Callable[[], None]) -> Case:
    try:
        fn()
    except AssertionError as e:
        return _fail(name, str(e) or "assertion failed")
    except Exception as e:
        return _fail(name, f"{type(e).__name__}: {e}")
    return _ok(name)


# -------------------- GET endpoints --------------------

def get_root():
    r = client.get("/")
    assert r.status_code == 200, f"status={r.status_code}"
    body = r.json()
    assert "message" in body, f"missing 'message': {body}"


def get_movies():
    r = client.get("/movies")
    assert r.status_code == 200, f"status={r.status_code}"
    body = r.json()
    assert isinstance(body, list), f"not a list: {type(body)}"
    assert len(body) > 0, "movies list empty"
    for item in body:
        MovieSchema.model_validate(item)


def get_job_status_happy():
    r = client.get(f"/batch/jobs/{EXISTING_JOB}")
    assert r.status_code == 200, f"status={r.status_code}"
    JobStatusResponse.model_validate(r.json())


def get_job_status_404():
    r = client.get(f"/batch/jobs/{MISSING_JOB}")
    assert r.status_code == 404, f"status={r.status_code}, body={r.text}"


def get_llm_result_happy():
    r = client.get(f"/batch/jobs/{EXISTING_JOB}/llm-result")
    assert r.status_code == 200, f"status={r.status_code}"
    body = r.json()
    LLMResponseSchema.model_validate(body)
    assert len(body["results"]) > 0, "no llm results"


def get_llm_result_404():
    r = client.get(f"/batch/jobs/{MISSING_JOB}/llm-result")
    assert r.status_code == 404, f"status={r.status_code}"


def get_cluster_result_happy():
    r = client.get(f"/batch/jobs/{EXISTING_JOB}/cluster-result")
    assert r.status_code == 200, f"status={r.status_code}"
    body = r.json()
    ClusterResponseSchema.model_validate(body)


def get_cluster_result_404():
    r = client.get(f"/batch/jobs/{MISSING_JOB}/cluster-result")
    assert r.status_code == 404, f"status={r.status_code}"


def get_final_result_happy():
    r = client.get(f"/batch/jobs/{EXISTING_JOB}/final-result")
    assert r.status_code == 200, f"status={r.status_code}"
    body = r.json()
    FinalResultSchema.model_validate(body)


def get_final_result_404():
    r = client.get(f"/batch/jobs/{MISSING_JOB}/final-result")
    assert r.status_code == 404, f"status={r.status_code}"


def get_opinion_groups_happy():
    r = client.get(f"/batch/jobs/{EXISTING_JOB}/opinion-groups")
    assert r.status_code == 200, f"status={r.status_code}"
    OpinionGroupListResponse.model_validate(r.json())


def get_opinion_groups_404():
    r = client.get(f"/batch/jobs/{MISSING_JOB}/opinion-groups")
    assert r.status_code in (400, 404), f"status={r.status_code}"


def get_opinion_group_reviews_happy():
    r = client.get(
        f"/batch/jobs/{EXISTING_JOB}/opinion-groups/{EXISTING_CLUSTER}/reviews",
        params={"page": 1, "page_size": 5},
    )
    assert r.status_code == 200, f"status={r.status_code}"
    body = r.json()
    OpinionGroupReviewsResponse.model_validate(body)
    assert body["page"] == 1
    assert body["page_size"] == 5


def get_opinion_group_reviews_missing_cluster():
    r = client.get(
        f"/batch/jobs/{EXISTING_JOB}/opinion-groups/{MISSING_CLUSTER}/reviews"
    )
    assert r.status_code == 400, f"status={r.status_code}, body={r.text}"


# -------------------- POST endpoints --------------------

def post_create_batch_job_happy():
    r = client.post(
        "/batch/jobs",
        json={"movie_id": "mv_001", "target_date": "2026-05-10"},
    )
    assert r.status_code == 200, f"status={r.status_code}, body={r.text}"
    body = r.json()
    CreateBatchJobResponse.model_validate(body)
    assert body["status"] == "queued"


def post_create_batch_job_missing_movie():
    r = client.post(
        "/batch/jobs",
        json={"movie_id": "mv_does_not_exist", "target_date": "2026-05-10"},
    )
    assert r.status_code == 404, f"status={r.status_code}"


def post_create_batch_job_missing_field():
    r = client.post("/batch/jobs", json={"movie_id": "mv_001"})
    assert r.status_code == 422, f"status={r.status_code}"


def post_create_batch_job_invalid_date():
    r = client.post(
        "/batch/jobs",
        json={"movie_id": "mv_001", "target_date": "not-a-date"},
    )
    assert r.status_code == 422, f"status={r.status_code}"


def post_run_llm_404():
    r = client.post(f"/batch/jobs/{MISSING_JOB}/run-llm")
    assert r.status_code == 404, f"status={r.status_code}"


def post_run_cluster_404():
    r = client.post(f"/batch/jobs/{MISSING_JOB}/run-cluster")
    assert r.status_code == 404, f"status={r.status_code}"


def post_build_final_404():
    r = client.post(f"/batch/jobs/{MISSING_JOB}/build-final")
    assert r.status_code == 404, f"status={r.status_code}"


# -------------------- Runner --------------------

def main() -> int:
    sections = {
        "GET endpoints": [
            ("GET /", get_root),
            ("GET /movies", get_movies),
            ("GET /batch/jobs/{id} happy", get_job_status_happy),
            ("GET /batch/jobs/{id} 404", get_job_status_404),
            ("GET .../llm-result happy", get_llm_result_happy),
            ("GET .../llm-result 404", get_llm_result_404),
            ("GET .../cluster-result happy", get_cluster_result_happy),
            ("GET .../cluster-result 404", get_cluster_result_404),
            ("GET .../final-result happy", get_final_result_happy),
            ("GET .../final-result 404", get_final_result_404),
            ("GET .../opinion-groups happy", get_opinion_groups_happy),
            ("GET .../opinion-groups 404", get_opinion_groups_404),
            ("GET .../opinion-groups/{cid}/reviews happy", get_opinion_group_reviews_happy),
            ("GET .../opinion-groups/{cid}/reviews missing cluster", get_opinion_group_reviews_missing_cluster),
        ],
        "POST endpoints": [
            ("POST /batch/jobs happy", post_create_batch_job_happy),
            ("POST /batch/jobs missing movie 404", post_create_batch_job_missing_movie),
            ("POST /batch/jobs missing field 422", post_create_batch_job_missing_field),
            ("POST /batch/jobs invalid date 422", post_create_batch_job_invalid_date),
            ("POST .../run-llm 404", post_run_llm_404),
            ("POST .../run-cluster 404", post_run_cluster_404),
            ("POST .../build-final 404", post_build_final_404),
        ],
    }

    total_fail = 0
    for section, cases in sections.items():
        print(f"\n=== {section} ===")
        for name, fn in cases:
            case = _check(name, fn)
            if case[1]:
                print(f"  [PASS] {case[0]}")
            else:
                print(f"  [FAIL] {case[0]}: {case[2]}")
                total_fail += 1

    print()
    if total_fail > 0:
        print(f"verify_routes: FAIL ({total_fail} case(s))")
        return 1
    print("verify_routes: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
