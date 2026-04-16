import json
from pathlib import Path
from typing import List, Optional

from app.schemas import FinalResultSchema

LLM_RESULTS_PATH = Path("data/llm_results.json")
CLUSTER_RESULTS_PATH = Path("data/cluster_results.json")
FINAL_RESULTS_PATH = Path("data/final_results.json")


def _read_json_array(path: Path) -> list[dict]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_array(path: Path, data: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_llm_result(job_id: str, movie_id: str, result_data: dict) -> None:
    data = _read_json_array(LLM_RESULTS_PATH)

    # 같은 job_id 결과가 있으면 덮어쓰기
    data = [item for item in data if item.get("job_id") != job_id]

    # wrapper 없이 원본 그대로 저장
    data.append(result_data)

    _write_json_array(LLM_RESULTS_PATH, data)


def get_llm_result_by_job_id(job_id: str) -> Optional[dict]:
    data = _read_json_array(LLM_RESULTS_PATH)

    for item in data:
        if item.get("job_id") == job_id:
            return item

    return None


def save_cluster_result(job_id: str, movie_id: str, result_data: dict) -> None:
    data = _read_json_array(CLUSTER_RESULTS_PATH)

    data = [item for item in data if item.get("job_id") != job_id]
    data.append(result_data)

    _write_json_array(CLUSTER_RESULTS_PATH, data)


def get_cluster_result_by_job_id(job_id: str):
    data = _read_json_array(CLUSTER_RESULTS_PATH)

    for item in data:
        if item.get("job_id") == job_id:
            return item

    return None


def save_final_result(job_id: str, movie_id: str, result_data: dict) -> None:
    data = _read_json_array(FINAL_RESULTS_PATH)

    data = [item for item in data if item.get("job_id") != job_id]
    data.append(result_data)

    _write_json_array(FINAL_RESULTS_PATH, data)


def get_final_result_by_job_id(job_id: str):
    data = _read_json_array(FINAL_RESULTS_PATH)

    for item in data:
        if item.get("job_id") == job_id:
            return item

    return None


def list_final_results() -> List[FinalResultSchema]:
    data = _read_json_array(FINAL_RESULTS_PATH)
    return [FinalResultSchema(**item) for item in data]


def get_result_by_movie_id(movie_id: str) -> Optional[FinalResultSchema]:
    for result in list_final_results():
        if result.movie_id == movie_id:
            return result
    return None