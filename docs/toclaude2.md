# toclaude.md

# Real Data 기반 영화 리뷰 수집 시스템 설계 문서 (v2)

## 프로젝트 목적

현재 프로젝트는:

```text
영화 리뷰
→ LLM 표현 추출
→ 감정 분석
→ 임베딩
→ 클러스터링
→ 최종 의견 요약
```

구조의 파이프라인 시스템이다.

기존에는 dataset 기반으로 동작했지만,
이제부터는 실제 영화 사이트 데이터(real data)를 수집하여
Supabase PostgreSQL 기반으로 전체 파이프라인을 동작시키려고 한다.

---

# 핵심 설계 원칙

```text
1. PostgreSQL(Supabase)을 단일 source of truth로 사용
2. JSON 파일 저장 구조 제거
3. Collector는 데이터 수집 + DB 저장만 수행
4. 분석 파이프라인은 reviews 테이블만 바라본다
5. 공식 API 우선 사용
6. 리뷰 수집은 우선 1개 source만 진행
7. 구조 완성 후 source 추가 확장
```

---

# 현재 기술 스택

```text
Backend:
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL (Supabase)
- Alembic

AI:
- sentence-transformers
- HDBSCAN

Frontend:
- 현재 Next.js 개발 중
```

---

# 현재 파이프라인 구조

```text
reviews
→ run-llm
→ llm_phrases
→ run-cluster
→ opinion_groups
→ build-final
→ frontend
```

현재 목표는:

```text
외부 API / 리뷰 수집
→ reviews DB 저장
→ 기존 파이프라인 그대로 실행
```

구조를 만드는 것이다.

---

# 요구사항 수정 사항 (중요)

## 1. 영화 목록 수집 데이터 최소화

영화 목록 수집 시 필요한 데이터는 아래만 사용한다.

```text
- 영화 제목
- 영화 포스터
- 영화 개봉일
- 영화 장르
- 영화 출처(source)
```

불필요한 상세 메타데이터는 초기 단계에서 제외한다.

예:

```text
감독
배우
러닝타임
줄거리
관람등급
```

등은 현재 필요하지 않다.

---

## 2. 리뷰 수집 source 최소화

초기 단계에서는:

```text
네이버
CGV
롯데시네마
메가박스
```

모두 구현하지 않는다.

우선:
```text
초기 source 선정 시:
- 로그인 없이 접근 가능
- 정적 HTML 기반
- 페이지네이션 구조 단순
- 리뷰 노출량 충분
- anti-bot 강도가 낮은 구조 우선

트래픽이 많고
접근이 상대적으로 쉽고 크롤링하기에 좋은 source 1개만 선택

1차 MVP에서는 source_movie_map 보류
source 확장 단계에서 추가 검토
```

해서 진행한다.

구조 완성 후 source를 추가 확장한다.

---

# 추천 source 선택 기준

아래 기준으로 source를 선정해줘.

```text
1. 리뷰 접근 난이도
2. 페이지 구조 안정성
3. 트래픽 규모
4. 크롤링 유지보수 난이도
5. 리뷰 데이터 양
```

선정 후:

* 왜 그 source를 선택했는지 설명
* 나머지 source는 왜 후순위인지 설명

---

# 영화 목록 수집 전략

## 목적

Frontend에 최신 영화 목록 제공.

예시:

* 현재 상영작
* 최신 개봉작
* 인기 영화

---

## 영화 목록 수집 방식

공식 API 우선 사용.

우선순위:

```text
1. KOBIS Open API
2. KMDb Open API
3. 기타 보조 API
```

---

## 저장 데이터 구조

movies 테이블 기준:

```text
movie_id
movie_title
poster_url
release_date
genre
source
created_at
updated_at
```

---

# 리뷰 수집 전략

## 목표

특정 영화에 대한 리뷰를 수집하여:

```text
reviews 테이블 저장
→ 기존 분석 파이프라인 연결
```

구조로 사용.

---

# 리뷰 수집 source 정책

초기에는 source 1개만 구현.

선정된 source 기준으로:

```text
- collector 구현
- 리뷰 수집
- 중복 제거
- DB 저장
```

까지만 진행.

---

# 리뷰 저장 구조

reviews 테이블 확장:

```text
review_id
movie_id
source
external_review_id
author
rating
text
written_at
collected_at
text_hash
is_processed
```

---

# 중복 방지 정책

우선순위:

```text
1. source + external_review_id
2. source + movie_id + text_hash
```

---

# Collector Layer 설계

새로운 collector 계층 추가.

구조:

```text
app/
├─ collectors/
│  ├─ base.py
│  ├─ movie_api_client.py
│  └─ selected_review_collector.py
```

---

# Collector 역할

Collector는 아래 역할만 수행.

```text
1. 외부 API/페이지 요청
2. 데이터 파싱
3. 내부 표준 schema 변환
4. DB 저장 요청
```

Collector는 아래 작업 금지.

```text
LLM 실행 금지
Clustering 금지
Final result 생성 금지
```

---

# 표준 수집 스키마

## CollectedMovie

```json
{
  "source": "kobis",
  "movie_title": "파묘",
  "poster_url": "https://...",
  "release_date": "2024-02-22",
  "genre": "공포"
}
```

---

## CollectedReview

```json
{
  "source": "selected_source",
  "external_review_id": "abc123",
  "movie_id": "mv_001",
  "author": "user***",
  "rating": 9.0,
  "text": "배우 연기가 좋았다",
  "written_at": "2026-05-24T10:00:00"
}
```

---

# 실행 모드 설계

## 1. 실시간 실행 모드

사용자가 분석 요청 시:

```text
요청된 영화의 리뷰 수집
→ DB 저장
→ 분석 파이프라인 실행
```

---

## 2. 예약 배치 모드

매일 특정 시간 자동 실행.

예:

```text

**고객 요청이 있을때**
매일 03:00
→ 요청된 영화의 리뷰 수집
→ DB 저장
→ 미처리 리뷰 분석
→ 결과 갱신
```

---

# 스케줄러 구조

초기 단계 추천:

```text
APScheduler
```
```text
APScheduler를 사용할 경우, FastAPI 개발 환경의 uvicorn --reload에서 scheduler가 중복 실행될 수 있으므로 중복 실행 방지 로직을 고려해야 한다.
운영 환경에서는 단일 프로세스 실행 또는 별도 worker/cron 방식으로 분리하는 것을 검토한다.
```
목표:

* FastAPI 내부에서 batch 실행
* source별 수집 가능
* mode별 실행 가능

---

# 신규 테이블 설계

## collection_jobs

```text
collection_job_id
source
mode
target_movie_id
status
started_at
finished_at
total_fetched
total_inserted
error_message
```

---

# 기존 분석 파이프라인 연결 원칙

분석 파이프라인은 collector를 몰라야 한다.

즉:

```text
run-llm:
reviews 테이블만 조회

run-cluster:
llm_phrases 테이블만 조회

build-final:
opinion_groups 기반 조회
```

---

# 구현 순서 (중요)

아래 순서대로 진행해줘.

---

## 1단계

```text
현재 DB 구조 점검
movies/reviews 테이블 구조 확정
필요 컬럼 추가
```

---

## 2단계

```text
KOBIS/KMDb 기반 영화 목록 수집 구현
movies 저장
```

---

## 3단계

```text
리뷰 source 1개 선정
선정 이유 설명
```

---

## 4단계

```text
selected_review_collector.py 구현
```

---

## 5단계

```text
리뷰 수집
→ reviews 저장
→ 중복 제거
```

---

## 6단계

```text
실시간 실행 모드 구현
```

예:

```http
POST /collection/reviews/run-now
```

---

## 7단계

```text
예약 배치 모드 구현
```

예:

```text
매일 특정 시각 자동 수집
```

---

## 8단계

```text
기존 run-llm → run-cluster → build-final
파이프라인과 연결
```

---

# 매우 중요한 설계 원칙

## PostgreSQL이 정본이다.

```text
DB = source of truth
JSON = 제거 대상
```

---

# Claude에게 요청 사항

아래 기준으로 진행해줘.

```text
1. 한번에 전체 구현하지 말 것
2. 단계별로 진행할 것
3. 각 단계 완료 후 왜 그렇게 설계했는지 설명할 것
4. 기존 pipeline을 최대한 깨지 않게 진행할 것
5. 필요한 파일만 최소 수정할 것
6. 각 단계별 수정 파일 목록을 명확히 제시할 것
7. DB schema 변경 시 Alembic migration도 같이 제시할 것
8. collector와 pipeline은 반드시 분리할 것
```
