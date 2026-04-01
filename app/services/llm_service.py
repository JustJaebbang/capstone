import json
import os
from pathlib import Path
from typing import Literal, Optional, cast

from openai import OpenAI, APIError, OpenAIError

from app.schemas import LLMRequestSchema, LLMResponseSchema


LLMMode = Literal["rule_based", "openai", "dummy"]

# 규칙 기반 추출기 설정
RULE_BASED_POSITIVE_CUES = [
    "좋",
    "훌륭",
    "완벽",
    "최고",
    "재밌",
    "재미",
    "인상",
    "탄탄",
    "몰입",
    "추천",
]

RULE_BASED_NEGATIVE_CUES = [
    "아쉽",
    "별로",
    "지루",
    "루즈",
    "실망",
    "부족",
    "억지",
    "지겹",
    "실패",
    "약함",
]

RULE_BASED_ASPECT_RULES = [
    {
        "keywords": ["연기", "배우", "캐스팅"],
        "positive": "연기 좋음",
        "negative": "연기 아쉬움",
        "mixed": "연기 호불호",
        "neutral": "연기 언급",
    },
    {
        "keywords": ["스토리", "전개", "서사"],
        "positive": "스토리 좋음",
        "negative": "스토리 아쉬움",
        "mixed": "스토리 호불호",
        "neutral": "스토리 언급",
    },
    {
        "keywords": ["영상미", "연출", "화면", "미장센"],
        "positive": "영상미 좋음",
        "negative": "영상미 아쉬움",
        "mixed": "영상미 호불호",
        "neutral": "영상미 언급",
    },
    {
        "keywords": ["몰입", "긴장감", "흡입력"],
        "positive": "몰입감 높음",
        "negative": "몰입감 낮음",
        "mixed": "몰입감 호불호",
        "neutral": "몰입감 언급",
    },
    {
        "keywords": ["음악", "오에스티", "ost", "o.s.t", "사운드트랙", "배경음", "bgm"],
        "positive": "음악 좋음",
        "negative": "음악 아쉬움",
        "mixed": "음악 호불호",
        "neutral": "음악 언급",
    },
]

RULE_BASED_FALLBACK_PHRASES = ["기타 의견", "전반적 감상"]


def _debug_log(message: str) -> None:
    """디버그 메시지를 콘솔에 출력한다."""
    print(f"[LLM] {message}", flush=True)


def _safe_exception_message(exc: Exception) -> str:
    """예외 메시지를 안전하게 추출한다."""
    text = str(exc).strip()
    return text if text else exc.__class__.__name__


def _resolve_llm_mode() -> LLMMode:
    """환경변수 또는 기본값으로 LLM 실행 모드를 결정한다."""
    raw_mode = os.getenv("LLM_MODE", "rule_based").strip().lower()
    if raw_mode in {"rule_based", "openai", "dummy"}:
        return cast(LLMMode, raw_mode)
    return "rule_based"


# 실행 모드는 환경변수 LLM_MODE 또는 이 값을 수정해서 전환한다.
LLM_MODE: LLMMode = _resolve_llm_mode()


def _get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def extract_key_phrases_openai(input_data: dict) -> dict:
    """README 9-2 규격(job_id, movie_id, results)에 맞게 OpenAI API를 활용해 핵심 표현을 추출한다."""
    request = LLMRequestSchema.model_validate(input_data)
    _debug_log(
        f"openai mode start: job_id={request.job_id}, movie_id={request.movie_id}, review_count={len(request.reviews)}"
    )

    client = _get_openai_client()

    # API 키가 없으면 즉시 규칙 기반 결과로 폴백하여 파이프라인을 유지한다.
    if client is None:
        _debug_log(f"openai fallback to rule_based: reason=missing_api_key job_id={request.job_id}")
        return extract_key_phrases_rule_based(input_data)

    # 1. 시스템 프롬프트
    system_instruction = """
당신은 영화 리뷰 분석가입니다.
주어진 리뷰들의 핵심 내용을 추출하세요.
각 리뷰마다 2~5개의 짧은 명사형 구문(key_phrases)으로 정리하세요.
반드시 제공된 JSON 형식으로만 반응하세요.
"""

    # 2. 사용자 프롬프트 (리뷰 데이터)
    prompt = f"""
분석할 리뷰 데이터:
{json.dumps(request.reviews, ensure_ascii=False, indent=2)}

출력 형식 (JSON):
{{
  "results": [
    {{"review_id": "r1", "key_phrases": ["표현1", "표현2"]}},
    {{"review_id": "r2", "key_phrases": ["표현1", "표현2", "표현3"]}}
  ]
}}
"""

    try:
        # 3. OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        # 4. LLM 결과 파싱
        llm_response_text = response.choices[0].message.content
        llm_result = json.loads(llm_response_text)

        # 5. 응답 구성 (README 9-2 규격)
        response_obj = LLMResponseSchema(
            job_id=request.job_id,
            movie_id=request.movie_id,
            results=llm_result.get("results", []),
        )
        _debug_log(f"openai success: job_id={request.job_id}, result_count={len(response_obj.results)}")
        return response_obj.model_dump(mode="json")

    except (ValueError, json.JSONDecodeError, KeyError, TypeError) as exc:
        # 응답 JSON 파싱 실패 시에도 서비스는 계속 동작해야 한다.
        _debug_log(
            f"openai fallback to rule_based: reason=parse_error error={_safe_exception_message(exc)} job_id={request.job_id}"
        )
        return extract_key_phrases_rule_based(input_data)
    except (APIError, OpenAIError, TimeoutError) as exc:
        # OpenAI 호출 실패 시 규칙 기반 결과로 폴백한다.
        _debug_log(
            f"openai fallback to rule_based: reason=api_error error={_safe_exception_message(exc)} job_id={request.job_id}"
        )
        return extract_key_phrases_rule_based(input_data)


def extract_key_phrases_dummy(input_data: dict) -> dict:
    """README 9-2 규격(job_id, movie_id, results)에 맞는 입력 반영형 더미 결과를 생성한다."""
    request = LLMRequestSchema.model_validate(input_data)
    _debug_log(
        f"dummy mode start: job_id={request.job_id}, movie_id={request.movie_id}, review_count={len(request.reviews)}"
    )

    # 모든 리뷰에 대해 고정 더미 key_phrases 반환
    results = [
        {
            "review_id": review.review_id,
            "key_phrases": ["연기 좋음", "스토리 지루함"],
        }
        for review in request.reviews
    ]

    response = LLMResponseSchema(
        job_id=request.job_id,
        movie_id=request.movie_id,
        results=results,
    )
    _debug_log(f"dummy mode success: job_id={request.job_id}, result_count={len(response.results)}")
    return response.model_dump(mode="json")


def extract_key_phrases_rule_based(input_data: dict) -> dict:
    """README 9-2 규격(job_id, movie_id, results)에 맞는 입력 반영형 규칙 기반 결과를 생성한다."""
    request = LLMRequestSchema.model_validate(input_data)
    _debug_log(
        f"rule_based mode start: job_id={request.job_id}, movie_id={request.movie_id}, review_count={len(request.reviews)}"
    )

    def _extract_key_phrases_from_text(text: str) -> list[str]:
        """단일 리뷰 텍스트에서 key_phrases를 추출한다."""
        normalized = text.lower().strip()
        has_positive = any(cue in normalized for cue in RULE_BASED_POSITIVE_CUES)
        has_negative = any(cue in normalized for cue in RULE_BASED_NEGATIVE_CUES)

        phrases = []
        for rule in RULE_BASED_ASPECT_RULES:
            if not any(keyword in normalized for keyword in rule["keywords"]):
                continue

            if has_positive and has_negative:
                phrases.append(rule["mixed"])
            elif has_negative:
                phrases.append(rule["negative"])
            elif has_positive:
                phrases.append(rule["positive"])
            else:
                phrases.append(rule["neutral"])

        # 순서 유지 중복 제거
        deduped = list(dict.fromkeys(phrases))

        if not deduped:
            deduped.extend(RULE_BASED_FALLBACK_PHRASES)

        # 최소 2개 보장
        while len(deduped) < 2:
            for fallback in RULE_BASED_FALLBACK_PHRASES:
                if fallback not in deduped:
                    deduped.append(fallback)
                    break

        # 리뷰당 2~5개 제한
        return deduped[:5]

    # 모든 리뷰에 대해 규칙 기반 추출 수행
    results = [
        {
            "review_id": review.review_id,
            "key_phrases": _extract_key_phrases_from_text(review.text),
        }
        for review in request.reviews
    ]

    response = LLMResponseSchema(
        job_id=request.job_id,
        movie_id=request.movie_id,
        results=results,
    )
    _debug_log(f"rule_based mode success: job_id={request.job_id}, result_count={len(response.results)}")
    return response.model_dump(mode="json")


def extract_key_phrases_by_mode(input_data: dict, mode: LLMMode = LLM_MODE) -> dict:
    """설정된 모드에 맞는 LLM 처리 함수를 호출한다."""
    handlers = {
        "rule_based": extract_key_phrases_rule_based,
        "openai": extract_key_phrases_openai,
        "dummy": extract_key_phrases_dummy,
    }

    handler = handlers.get(mode)
    if handler is None:
        raise ValueError(f"Unsupported LLM mode: {mode}")

    _debug_log(f"dispatch mode={mode}")
    return handler(input_data)


def process_json_file(
    input_filepath: str,
    output_filepath: str,
) -> None:
    """요청 JSON(README 9-1)을 읽어 응답 JSON(README 9-2)로 저장한다.
    
    Args:
        input_filepath: 입력 JSON 파일 경로
        output_filepath: 출력 JSON 파일 경로
    """
    input_path = Path(input_filepath)
    output_path = Path(output_filepath)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_filepath}")

    with input_path.open("r", encoding="utf-8") as f:
        input_data = json.load(f)

    output_data = extract_key_phrases_by_mode(input_data)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)