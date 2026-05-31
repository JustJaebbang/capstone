import json
import sys
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.db.models.batch_job import BatchJob  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402


JOBS_PATH = BASE_DIR / "data" / "jobs.json"


def _parse_dt(value):
    return datetime.fromisoformat(value) if value else None


def _parse_date(value):
    return date.fromisoformat(value) if value else None


def main():
    if not JOBS_PATH.exists():
        print(f"[backfill] {JOBS_PATH} not found, nothing to do")
        return

    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    db = SessionLocal()
    inserted = 0
    skipped = 0

    try:
        for j in jobs:
            existing = (
                db.query(BatchJob).filter(BatchJob.job_id == j["job_id"]).one_or_none()
            )
            if existing is not None:
                skipped += 1
                continue

            db.add(
                BatchJob(
                    job_id=j["job_id"],
                    movie_id=j["movie_id"],
                    movie_title=j["movie_title"],
                    target_date=_parse_date(j["target_date"]),
                    status=j["status"],
                    created_at=_parse_dt(j["created_at"]),
                    started_at=_parse_dt(j.get("started_at")),
                    finished_at=_parse_dt(j.get("finished_at")),
                )
            )
            inserted += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"[backfill] inserted={inserted}, skipped={skipped}, total_in_json={len(jobs)}")


if __name__ == "__main__":
    main()
