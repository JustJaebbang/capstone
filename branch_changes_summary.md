# main 대비 변경사항 정리

## 기준

- 현재 브랜치: `feature/seohyun-llm`
- `main`: `1fd0f0e`
- 현재 `HEAD`: `7d423ea`
- 확인일: 2026-05-11

## 결론

`main...HEAD` 기준으로는 현재 브랜치에 커밋된 변경사항이 없습니다.

현재 확인되는 차이는 아직 커밋되지 않은 작업트리 변경사항입니다.

```text
 M app/services/llm_service.py
?? .env.example
?? branch_changes_summary.md
```

`sentiment_eval_app.html`은 임시 사용 후 삭제되었으므로 현재 변경사항에 포함되지 않습니다.

## 파일별 변경사항

| 파일 | 상태 | 내용 |
| --- | --- | --- |
| `app/services/llm_service.py` | 수정됨 | OpenAI 기반 phrase 추출 프롬프트 개선 및 기본 모드 변경 |
| `.env.example` | 신규 파일 | 현재 빈 파일, 기능 변경 없음 |
| `branch_changes_summary.md` | 신규 파일 | 변경사항 정리 문서 |

## `app/services/llm_service.py`

### 1. OpenAI 요청 입력 축소

OpenAI 프롬프트에 전달하는 리뷰 데이터를 필요한 필드만 포함하도록 변경했습니다.

기존에는 리뷰 객체 전체를 `model_dump`로 넘겼지만, 변경 후에는 아래처럼 `review_id`와 `text`만 전달합니다.

```python
reviews_json = json.dumps(
    [{"review_id": r.review_id, "text": r.text} for r in payload.reviews],
    ensure_ascii=False,
    separators=(",", ":"),
)
```

이 변경으로 프롬프트 입력이 더 짧아지고, LLM이 실제 phrase 추출에 필요한 정보에 집중할 수 있습니다.

### 2. phrase 추출 프롬프트 강화

기존 프롬프트는 “각 리뷰에서 핵심 표현 1~5개 추출” 수준의 간단한 지시였습니다.

변경 후에는 다음 기준이 추가되었습니다.

- 리뷰 1개당 phrase를 `1~3개`만 추출
- phrase는 짧은 한국어 구문으로 작성
- 기본 형식은 `평가 대상 + 평가`
- 하나의 phrase에는 하나의 평가 토픽만 포함
- 여러 토픽이 섞인 문장은 phrase를 분리
- `positive`, `negative` 외 sentiment 값 금지
- JSON 객체만 반환하도록 제한

### 3. 클러스터링에 적합한 표현 유도

LLM 결과가 토픽 클러스터링에 바로 쓰일 수 있도록 phrase 작성 규칙이 구체화되었습니다.

예를 들어 다음과 같은 복합 표현은 피하도록 했습니다.

- `영상미 사운드 뛰어남`
- `음악 연출력 좋음`
- `스케일과 영상미 좋음`
- `연기 스토리 좋음`

대신 아래처럼 평가 대상을 분리한 표현을 권장합니다.

- `영상미 뛰어남`
- `사운드 압도적`
- `연출 좋음`
- `스케일 압도적`
- `배우 연기 좋음`

### 4. 결과 검증 조건 추가

LLM 응답에 대해 다음 조건을 프롬프트에 명시했습니다.

- `results` 길이는 입력 리뷰 수와 같아야 함
- 모든 입력 `review_id`가 정확히 한 번씩 포함되어야 함
- sentiment는 반드시 `positive` 또는 `negative`
- JSON 외의 설명, 마크다운, 코드블록 출력 금지

### 5. 기본 실행 모드 변경

`extract_phrases_with_sentiment`의 기본값이 변경되었습니다.

```python
mode: str = "rule_based"
```

에서

```python
mode: str = "openai"
```

로 바뀌었습니다.

따라서 호출자가 별도 모드를 지정하지 않으면 OpenAI 기반 추출이 기본으로 실행됩니다.

단, `OPENAI_API_KEY`가 없거나 OpenAI 응답 파싱/호출이 실패하면 기존처럼 rule-based 방식으로 fallback합니다.

## 영향

- 기본 동작이 rule-based 추출에서 OpenAI 추출로 바뀝니다.
- API 키가 설정된 환경에서는 외부 OpenAI API 호출이 기본 동작이 됩니다.
- API 키가 없는 환경에서는 기존 fallback 로직이 유지됩니다.
- phrase 결과가 더 짧고, 토픽별로 분리되고, 클러스터링에 적합한 형태로 나올 가능성이 높습니다.

## 확인 필요

- `.env.example`은 현재 빈 파일입니다. 실제로 커밋할 파일인지 확인이 필요합니다.
- `app/services/llm_service.py`에는 기존부터 인코딩이 깨져 보이는 한글 문자열이 일부 있습니다. 이번 변경은 OpenAI 프롬프트 중심이지만, rule-based fallback 품질을 보려면 해당 문자열도 별도 점검하는 것이 좋습니다.
- OpenAI 모델명 `gpt-5.4-nano`가 실제 실행 환경에서 사용 가능한지 확인이 필요합니다.

