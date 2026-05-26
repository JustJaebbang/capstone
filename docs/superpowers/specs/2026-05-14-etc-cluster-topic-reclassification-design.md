# 기타 클러스터 토픽 재분류 설계

날짜: 2026-05-14
브랜치: feature/seohyun-llm

## 배경

클러스터 결과 파일(`data/cluster_result_mv_*.json`)에는 `topic == "기타"`로 분류된
클러스터가 존재한다 (예: `mv_001`의 `cl_003`/`cl_005`, `mv_002`의 `cl_001`/`cl_002`).
이 "기타" 클러스터의 phrase들을 LLM에 보내, 정해진 15개 후보 토픽 중 가장 적절한
하나로 재분류한다.

함께, `llm_service.py`는 현재 이번 브랜치에서 phrase별 topic을 부여하도록 확장돼
있는데, 토픽 부여 책임을 LLM 추출 단계에서 분리한다. 클러스터링 모듈이 이미
클러스터 단위 topic을 붙이고, 본 재분류 서비스가 "기타" 클러스터를 보정하므로
phrase 단위 topic 부여는 불필요하다.

## 후보 토픽 (클러스터 모듈 명명법)

연기, 스토리/전개, 캐릭터, 연출, 영상미, 음향/OST, 몰입감/재미, 공포/긴장감,
감정/여운, 메시지/주제, 설정/세계관, 속도감/러닝타임, CG/VFX, 완성도, 기타

`기타`도 유효한 답으로 인정한다 (예: "극장 매너 최악", "시간 낭비"처럼 실제로
어떤 영화 요소에도 속하지 않는 경우).

## 변경 범위

### 1. `app/services/llm_service.py` — topic 부여 코드 제거

- 삭제: `TOPIC_KEYWORDS`, `ALLOWED_TOPICS`, `TOPIC_DESCRIPTIONS`,
  `TOPIC_PHRASE_EXAMPLES`, `_render_topic_guide()`, `_render_topic_examples()`,
  `infer_topic()`, `normalize_topic()`
- `build_phrase_items()`에서 `topic=infer_topic(phrase)` 인자 제거
- `extract_phrases_openai()`: 프롬프트의 topic 집합 / 경계 규칙 / topic별 예시
  블록 제거, 응답 파싱에서 topic 처리 제거. phrase 추출 개선 프롬프트 구조와
  phrase 작성 규칙은 유지. 출력은 `(text, sentiment)`만.
- 안 쓰게 되는 `Dict` import 정리
- 유지: `load_dotenv`, `_get_openai_client`, dummy / rule_based 경로

### 2. `app/schemas.py`

- `PhraseSentimentItem`에서 `topic: Optional[str] = None` 제거.

다운스트림 영향 없음 확인: `PhraseSentimentItem.topic`은 어디서도 소비되지 않고,
`llm_phrases` 테이블(`LLMPhrase` 모델)에 `topic` 컬럼이 없다.

### 3. 신규 `app/services/topic_service.py`

- `CANDIDATE_TOPICS`: 15개 후보 토픽 리스트
- `TOPIC_DEFINITIONS`: 토픽별 한 줄 정의 사전 (프롬프트용)
- `_get_openai_client()`: 자체 헬퍼 (서비스 간 private 함수 import 안 함)
- `classify_etc_cluster(phrases, sentiment) -> str`: OpenAI 1회 호출로 후보 중
  1개 반환. 검증 실패(후보 밖 값 / 빈 응답) 시 `"기타"` 유지.
  모델 `gpt-5.4-nano`, `response_format=json_object`.
- `reclassify_file(input_path) -> output_path`: JSON 로드 → `topic == "기타"`
  클러스터마다 `classify_etc_cluster` 호출 → `topic` 필드만 교체
  (count / sentiment / phrases 불변) → `*_reclassified.json` 저장
- `__main__` 블록: CLI 인자로 파일 경로 받음, 없으면
  `data/cluster_result_mv_*.json` 전체 처리, 변경 요약(기존 → 새 토픽) 출력
- API 키 없으면 경고 출력 후 건너뜀 (기타 유지, crash 없음 — `llm_service.py`의
  "예외를 던지지 않는다" 정책과 일관)

## 호출/출력 정책 (확정)

- 호출 단위: **클러스터 단위** — 기타 클러스터의 모든 phrase + sentiment를 한 번에
  보내고 토픽 1개를 받는다. 클러스터당 1회 호출.
- 출력: **새 파일** `data/cluster_result_mv_XXX_reclassified.json`. 원본 불변.
- 대상 파일: `data/cluster_result_mv_*.json` (새 토픽 명명법). `cluster_results1.json`
  / `cluster_results2.json` (구 명명법)은 범위 밖.

## 비범위

- DB 반영 / 파이프라인 통합 (run-cluster 단계 수정) — 별도 작업.
- 구 명명법 파일 처리.
