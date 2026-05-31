# 야간 배치 처리 시간 최적화 기록

> 작성일: 2026-05-25
> 범위: CGV 리뷰 수집(collection) 단계
> 결과: **영화당 31% 단축** (257.9s → 177.5s)

---

## 1. 배경

본 프로젝트의 KPI 중 하나는 **일일 배치로 3000건+ 리뷰 처리**. 새벽 cron이 구독된 영화들을 순회하며 CGV에서 리뷰를 수집하고 LLM/클러스터링을 돌리는 구조.

문제 인식 계기 — 영화 2개 첫 수집(`POST /collection/scheduler/trigger-now`)에 30분 가까이 소요. KPI 달성 가능성과 demo 운영 안정성을 위해 병목 진단 및 최적화 필요.

---

## 2. 측정 — 베이스라인 확보

### 측정 대상

| 영화 | movie_id | cgv_code |
|---|---|---|
| 신극장판 은혼 | kobis_20262975 | 30001088 |
| (영화명 생략) | kobis_20263222 | 30001151 |

### 측정 방법

`collection_jobs.started_at` / `finished_at` 컬럼이 작업 시작/종료 시각을 이미 기록 중. 별도 로그 없이 SQL로 wall time 추출.

```sql
SELECT target_movie_id, status,
       EXTRACT(EPOCH FROM (finished_at - started_at)) AS seconds,
       total_fetched, total_inserted
FROM collection_jobs
WHERE mode='scheduled' AND status='completed'
ORDER BY started_at DESC;
```

### 베이스라인 결과 (first-time collection)

| 영화 | wall time | 수집 건수 | 저장 건수 |
|---|---|---|---|
| kobis_20262975 | **257.9초** (4.30분) | 805 | 791 |
| kobis_20263222 | **269.5초** (4.49분) | 832 | 730 |
| **평균 / 합계** | **263.7초 / 527.4초** | 1,637 | 1,521 |

→ 영화당 약 4.4분. 영화 20개 처리하면 ~1.5시간.

### 분석 단계는 매우 빠름 (단, **placeholder 기준**)

| job_id | 영화 | wall time |
|---|---|---|
| job_038 | kobis_20262975 | 2.97s |
| job_037 | kobis_20263222 | 8.58s |
| job_036 | kobis_20259626 | 9.39s |

→ 분석 단계는 영화당 3~10초. **단, 이는 LLM/클러스터링 모듈이 placeholder(`dummy`/`rule_based`)인 상태의 측정**. 실제 모듈(OpenAI 호출, 임베딩) 머지 후 분 단위로 증가 예상.

**결론: 현재 병목은 collection 단계 (분석의 ~30배 시간 소요).**

---

## 3. 진단 — 어디서 시간이 새는가

`fetch_all_reviews()` 코드 분석:

```python
scroll_wait_ms = 1500     # 스크롤 사이 대기
post_load_wait_ms = 5000  # 페이지 로딩 후 초기 대기
no_progress_limit = 2     # 빈 응답 2회 연속이면 종료
```

800 리뷰 → CGV가 페이지당 ~10건씩 응답 → 약 80회 스크롤 필요.

**순수 대기 시간**: 80 × 1.5초 = **120초** (전체 257초의 47%)

→ scroll 사이 대기가 가장 큰 절약 여지.

---

## 4. Phase 1 — 적용한 최적화

### 변경 1: `scroll_wait_ms` 1500 → 1000

스크롤 사이 대기를 33% 단축. CGV 응답 누락 위험을 고려해 보수적으로 1000ms 선택.

```python
# app/collectors/selected_review_collector.py
def fetch_all_reviews(self, cgv_movie_code: str,
                      max_scrolls: int = 2000,
                      scroll_wait_ms: int = 1000,  # was 1500
                      ...):
```

### 변경 2: Playwright Chromium 영화 간 재사용

기존: 영화마다 Chromium 새로 부팅 → 영화당 ~2~5초 부팅 오버헤드 누적.
변경: 야간 배치 시작 시 1개 띄우고 모든 영화가 공유.

```python
# app/services/collection_service.py - refresh_all_subscribed_movies()
shared_cgv_client = CGVReviewClient()
shared_cgv_client._ensure_started()

try:
    for movie_id, source, ext_id in rows:
        job = run_collection_now(..., cgv_client=shared_cgv_client)
finally:
    shared_cgv_client.close()
```

`CGVReviewCollector.__init__`에 `_owns_client` 플래그 추가 — 외부 주입된 client는 영화 처리 후 자동 close 안 함. run-now 호출 경로는 기존대로 영화마다 본인 client 생성/해제.

### 적용 방침

- ✅ 보수적 변경 (대기 시간을 0으로 만들지 않음)
- ✅ 동작 호환성 유지 (run-now는 기존 동작 그대로)
- ✅ 실패 격리 (shared client 시작 실패 시 fallback)

---

## 5. 결과 — Phase 1 적용 후 측정

**같은 영화, 동일 환경에서 reviews 테이블만 비우고 재측정** (실험 변수 통제).

| 영화 | 베이스라인 | Phase 1 | 변화 | fetched | inserted |
|---|---|---|---|---|---|
| kobis_20262975 | 257.9s | **177.5s** | **-31.2%** | 806 | 792 |
| kobis_20263222 | 269.5s | **184.1s** | **-31.7%** | 842 | 740 |
| **2영화 합계** | **527.4s** | **361.6s** | **-31.4%** | | |
| **2영화 합계 (분)** | 8.79분 | 6.03분 | **-2.76분** | | |

### 정합성 검증

- 수집 데이터 손실 없음 (오히려 fetched 수가 미세하게 더 많음: 805→806, 832→842)
- 중복 처리 정상 작동 (UNIQUE / text_hash dedup)
- 오류 0건

### 절감의 출처 분해

| 출처 | 예상 효과 | 실측 |
|---|---|---|
| scroll_wait_ms 1500→1000 | 영화당 ~80초 | -80.4초, -85.4초 (예상 정확히 적중) |
| Chromium 1회 부팅 | 영화당 ~2~5초 | 측정 노이즈 안에 포함 |

→ 대부분의 절감은 scroll_wait_ms 감축에서 발생. shared client는 작지만 0은 아님.

---

## 6. KPI 달성 가능성

영화 1개 ~3분 (Phase 1 기준).

| 시나리오 | 처리 시간 |
|---|---|
| 영화 5개 (각 ~800 리뷰) | ~15분 |
| 영화 10개 | ~30분 |
| 영화 20개 (총 ~16,000 리뷰) | ~1시간 |
| 1영화에 3000 리뷰 집중 | ~11분 |

새벽 03:00 cron 시작 → 영화 20개라도 04:00 완료. **운영 안정성 확보.**

---

## 7. 의사결정 — Phase 2 보류

Phase 1 결과 충분. 추가 최적화는 demo 이후 또는 분석 모듈 머지 후로 미룸.

### Phase 2 후보 (보류)

| 후보 | 예상 효과 | 리스크 | 판단 |
|---|---|---|---|
| scroll_wait_ms 1000 → 800 | -20% 추가 | CGV 응답 누락 가능 | 보류 |
| post_load_wait_ms 5000 → 3000 | -2초/영화 | 안티봇 챌린지 지연 | 보류 |
| Playwright 2개 병렬 | 시간 ½ | Cloudflare 차단 | demo 직전엔 위험 |
| 분석 파이프라인 최적화 | TBD | placeholder 머지 후 측정 필요 | 머지 후 결정 |

### 보류 사유

1. **현 수준이 KPI 만족** — 새벽 batch에서 영화 20개 1시간 내. demo 안정성 충분
2. **placeholder 머지 시 재측정 필요** — Seohyun/Junhee가 실제 LLM + 임베딩 통합 후 분석 단계 시간이 어떻게 변하는지 보고 다음 병목 결정
3. **안티봇 위험** — demo 직전에 CGV 차단 트리거하면 복구 어려움. 보수적으로 운영

---

## 8. 발표 시 핵심 메시지

1. 운영 데이터를 직접 측정해서 (DB의 timestamp 컬럼만으로) 베이스라인 확보. 별도 측정 인프라 없이 의사결정 가능
2. 추측이 아닌 데이터 기반 진단 — "분석이 느릴 것"이라는 처음 추측은 틀렸고, 실제 병목은 수집의 scroll 대기였음
3. **31% 단축**, 코드 변경 라인 수 적음 (단순 파라미터 + 라이프사이클 조정)
4. 비파괴적 변경 — 데이터 손실 없음, 호환성 유지, 실패 격리
5. **남은 과제** — 실제 LLM/클러스터 모듈 통합 후 분석 단계 재측정이 다음 마일스톤

---

## 9. 참고 — 적용 코드 위치

| 변경 | 파일 | 라인 (대략) |
|---|---|---|
| scroll_wait_ms 기본값 | `app/collectors/selected_review_collector.py` | `fetch_all_reviews` 시그니처 |
| Chromium 소유권 플래그 | `app/collectors/selected_review_collector.py` | `CGVReviewCollector.__init__` |
| client 외부 주입 | `app/services/collection_service.py` | `run_collection_now`, `_run_source_collector` |
| 영화 간 client 공유 | `app/services/collection_service.py` | `refresh_all_subscribed_movies` |

측정 SQL은 §2 참조.
