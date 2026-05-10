import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.services.final_service import collect_reviews_for_cluster  # noqa: E402
from app.services.result_service import (  # noqa: E402
    save_movie_summary_to_db,
    save_opinion_groups_to_db,
    save_review_cluster_map_to_db,
)
from app.services.review_service import fetch_reviews  # noqa: E402

CLUSTER_PATH = BASE_DIR / "data" / "cluster_results.json"
LLM_PATH = BASE_DIR / "data" / "llm_results.json"
FINAL_PATH = BASE_DIR / "data" / "final_results.json"


def _read_json_array(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _index_by_job_id(items: list[dict]) -> dict[str, dict]:
    return {item["job_id"]: item for item in items}


def main():
    cluster_items = _read_json_array(CLUSTER_PATH)
    llm_index = _index_by_job_id(_read_json_array(LLM_PATH))
    final_items = _read_json_array(FINAL_PATH)

    cluster_count = 0
    rcm_count = 0

    for cluster_result in cluster_items:
        job_id = cluster_result["job_id"]
        movie_id = cluster_result["movie_id"]

        save_opinion_groups_to_db(
            job_id=job_id, movie_id=movie_id, cluster_result=cluster_result
        )
        cluster_count += len(cluster_result["clusters"])

        llm_result = llm_index.get(job_id)
        if llm_result is None:
            print(f"[backfill] llm_result missing for {job_id}, skipping rcm")
            continue

        source_reviews = fetch_reviews(movie_id=movie_id, review_limit=10_000)
        source_reviews_data = [
            {"review_id": r.review_id, "text": r.text} for r in source_reviews
        ]

        mapping_rows = []
        for cluster in cluster_result["clusters"]:
            matched = collect_reviews_for_cluster(
                cluster=cluster,
                llm_result=llm_result,
                source_reviews=source_reviews_data,
            )
            for review in matched:
                mapping_rows.append(
                    {
                        "job_id": job_id,
                        "cluster_id": cluster["cluster_id"],
                        "review_id": review.review_id,
                    }
                )

        save_review_cluster_map_to_db(job_id=job_id, mapping=mapping_rows)
        rcm_count += len(mapping_rows)
        print(
            f"[backfill] {job_id}: opinion_groups={len(cluster_result['clusters'])}, "
            f"review_cluster_map={len(mapping_rows)}"
        )

    final_items_sorted = sorted(final_items, key=lambda x: x["job_id"])
    summary_count = 0
    for final_result in final_items_sorted:
        save_movie_summary_to_db(
            movie_id=final_result["movie_id"],
            sentiment_ratio=final_result["summary"]["sentiment_ratio"],
        )
        summary_count += 1

    print(
        f"[backfill] totals: opinion_groups={cluster_count}, "
        f"review_cluster_map={rcm_count}, movie_summary={summary_count}"
    )


if __name__ == "__main__":
    main()
