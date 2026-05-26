## 파일 변경 기록

이 문서는 `app/routers/llm.py`, `app/services/llm_service.py`를 제외한 변경사항만 기록한다.

## 1) app/services/pipeline_service.py

### 변경 내용
- `run_llm_pipeline_for_job(job_id: str)` 함수 시그니처 단순화
  - 이전: `run_llm_pipeline_for_job(job_id: str, use_openai: bool = False)`
  - 현재: `run_llm_pipeline_for_job(job_id: str)`
- 함수 내부 분기 제거
  - `if use_openai:` 조건문 완전 제거
  - 중앙 모드 디스패처(`LLM_MODE`) 기반 단일 흐름으로 통일
- 파이프라인 실행 전후 디버그 로그 추가
  - 시작: `[LLM] pipeline start: job_id=..., mode=..., review_count=...`
  - 완료: `[LLM] pipeline done: job_id=..., mode=..., result_count=...`

### 효과
- 모드 선택 정책이 `app.services.llm_service`의 `LLM_MODE`에 중앙화됨
- 파이프라인 코드는 모드에 무관한 순수 데이터 흐름으로 단순화
- 실행 모드 변경 시 환경변수 설정만으로 즉시 반영 가능

## 2) app/routers/llm.py

### 변경 내용
- `/extract` 엔드포인트 시그니처 단순화
  - 이전: `extract_key_phrases(payload: LLMRequestSchema, use_openai: bool = False)`
  - 현재: `extract_key_phrases(payload: LLMRequestSchema)`
- 함수 내부 분기 제거
  - `if use_openai:` 조건문 완전 제거
  - 중앙 모드 디스패처(`LLM_MODE`) 기반 단일 흐름으로 통일
- API 호출 전후 디버그 로그 추가
  - 시작: `[LLM] router extract: job_id=..., mode=..., review_count=...`
  - 완료: `[LLM] router done: job_id=..., mode=..., result_count=...`

### 효과
- 외부 클라이언트가 모드를 직접 제어할 수 없음 (정책 일관성 보장)
- 모드 변경은 서버 환경변수 `LLM_MODE` 설정으로만 가능
- API 인터페이스 개선으로 불필요한 선택지 제거

## 3) app/routers/jobs.py

### 변경 내용
- `/batch/jobs/{job_id}/run` 엔드포인트 시그니처 단순화
  - 이전: `run_batch_job(job_id: str, use_openai: bool = False)`
  - 현재: `run_batch_job(job_id: str)`
- 함수 호출 수정
  - 이전: `run_llm_pipeline_for_job(job_id=job_id, use_openai=use_openai)`
  - 현재: `run_llm_pipeline_for_job(job_id=job_id)`
- 예외 처리 개선
  - 예외 체인 명시: `raise HTTPException(...) from e`

### 효과
- 배치 실행 API도 중앙 모드 정책 적용
- 외부 클라이언트가 모드를 직접 제어할 수 없음
- 모드 변경은 서버 환경변수 `LLM_MODE`로만 가능

## 4) app/services/llm_service.py

### 변경 내용

- OpenAI 요청용 리뷰 입력 생성 방식 개선
  - 이전: `payload.reviews`를 `model_dump()` 후 들여쓰기 포함 JSON으로 전달
  - 현재: `review_id`, `text`만 추려 `reviews_json`으로 만들고, 불필요한 공백 없이 전달
- OpenAI 시스템 프롬프트 상세화
  - 단순한 "영화 리뷰 분석가" 지시에서 클러스터링에 적합한 핵심 평가 phrase 추출 규칙으로 확장
  - 리뷰당 phrase 개수를 1~3개로 제한
  - 하나의 phrase에 하나의 평가 대상 토픽만 담도록 명시
  - 너무 일반적인 표현과 `기타 의견`, `긍정 반응`, `부정 반응` 사용 금지
  - 배우, 감독, 음악감독 등 인물명이 핵심 평가 대상일 때 phrase에 포함 가능하도록 규칙 추가
- OpenAI 사용자 프롬프트 보강
  - 모든 입력 `review_id`를 정확히 한 번씩 포함하도록 명시
  - `results` 길이가 입력 리뷰 수와 같아야 한다는 조건 추가
  - sentiment 값은 `"positive"` 또는 `"negative"`만 허용하도록 재강조
  - 복합 phrase 금지 예시와 권장 phrase 예시 추가
- `extract_phrases_with_sentiment()` 기본 실행 모드 변경
  - 이전: `mode: str = "rule_based"`
  - 현재: `mode: str = "openai"`
- 파일 끝 newline 복구

### 효과
- LLM 출력 phrase가 이후 클러스터링에 더 적합한 짧고 일관된 라벨 형태로 정리됨
- 복합 토픽이 한 phrase에 섞이는 문제를 줄여 클러스터 품질 개선 기대
- 입력 리뷰 수와 출력 결과 수의 불일치 가능성을 프롬프트 단계에서 완화
- 기본 호출 시 rule-based가 아니라 OpenAI 기반 추출을 우선 사용
- backup 브랜치의 최신 LLM 프롬프트/동작 정책이 현재 브랜치에 반영됨
