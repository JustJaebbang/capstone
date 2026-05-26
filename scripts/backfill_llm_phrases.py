import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.services.result_service import save_llm_phrases_to_db  # noqa: E402

LLM_RESULTS_PATH = BASE_DIR / "data" / "llm_results.json"


def main():
    if not LLM_RESULTS_PATH.exists():
        print(f"[backfill] {LLM_RESULTS_PATH} not found, nothing to do")
        return

    items = json.loads(LLM_RESULTS_PATH.read_text(encoding="utf-8"))

    total_phrases = 0
    for item in items:
        job_id = item["job_id"]
        movie_id = item["movie_id"]
        save_llm_phrases_to_db(job_id=job_id, movie_id=movie_id, result_data=item)
        n = sum(len(r["phrases"]) for r in item["results"])
        total_phrases += n
        print(f"[backfill] {job_id}: reviews={len(item['results'])}, phrases={n}")

    print(f"[backfill] totals: jobs={len(items)}, phrases={total_phrases}")


if __name__ == "__main__":
    main()
