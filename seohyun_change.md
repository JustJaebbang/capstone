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
