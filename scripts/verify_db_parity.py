"""
DB ↔ JSON 동등성 회귀 가드.

Phase 2b 사고: fallback 경로가 결과를 채워서 parity 테스트가 사실상 JSON↔JSON 비교에 그쳤음.
이 스크립트는 fallback을 절대 거치지 않고 DB 헬퍼와 JSON 파일을 직접 비교한다.

성공 시 exit 0, 불일치 시 exit 1. CI/수동 실행 모두 사용 가능.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Phase 4d: all dual-write parity sections sunsetted. JSON write removed for all units.


def _read_json_array(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _index_by_job_id(items: list[dict]) -> dict[str, dict]:
    return {item["job_id"]: item for item in items}


def _parse_dt(value):
    return datetime.fromisoformat(value) if value else None


def _parse_date(value):
    return date.fromisoformat(value) if value else None


def _phrase_set(phrases: list[dict]) -> frozenset:
    return frozenset((p["text"], p["sentiment"]) for p in phrases)


def _diff_lines(label: str, actual, expected) -> list[str]:
    return [
        f"  - {label}",
        f"      json: {expected}",
        f"      db  : {actual}",
    ]


# Phase 4a: jobs section sunsetted. jobs.json no longer written.


# Phase 4b: llm_phrases section sunsetted. llm_results.json no longer written.


# Phase 4c: opinion_groups section sunsetted. cluster_results.json no longer written.


def main() -> int:
    sections: list = []

    total_failures = 0
    for name, fn in sections:
        failures = fn()
        if failures:
            print(f"[FAIL] {name}: {len(failures)} issue(s)")
            for line in failures:
                print(line)
            total_failures += len(failures)
        else:
            print(f"[PASS] {name}")

    if total_failures > 0:
        print(f"\nverify_db_parity: FAIL ({total_failures} issue(s))")
        return 1

    print("\nverify_db_parity: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
