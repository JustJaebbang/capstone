## 파일 변경 기록


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
