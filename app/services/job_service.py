import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.schemas import BatchJobSchema, CreateBatchJobRequest

DATA_PATH = Path("data/jobs.json")


def _read_jobs() -> List[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_jobs(jobs: List[dict]) -> None:
    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def list_jobs() -> List[BatchJobSchema]:
    return [BatchJobSchema(**job) for job in _read_jobs()]


def get_job(job_id: str) -> Optional[BatchJobSchema]:
    jobs = list_jobs()
    for job in jobs:
        if job.job_id == job_id:
            return job
    return None


def create_job(payload: CreateBatchJobRequest, movie_title: str) -> BatchJobSchema:
    jobs = _read_jobs()
    new_job = BatchJobSchema(
        job_id=f"job_{len(jobs)+1:03d}",
        movie_id=payload.movie_id,
        movie_title=movie_title,
        target_date=payload.target_date,
        status="queued",
        created_at=datetime.now(),
        started_at=None,
        finished_at=None,
    )
    jobs.append(new_job.model_dump(mode="json"))
    _write_jobs(jobs)
    return new_job