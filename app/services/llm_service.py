import json
import os
import re
from typing import List, Optional

from openai import OpenAI, APIError, OpenAIError

from app.schemas import LLMRequestSchema, LLMResponseSchema


# ---------------------------
# OpenAI client
# ---------------------------
def _get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


# ---------------------------
# Rule sets
# ---------------------------
POSITIVE_RULES = [
    (["연기", "배우"], "연기 좋음"),
    (["영상미", "화면", "촬영", "연출"], "영상미 좋음"),
    (["몰입", "집중", "긴장감"], "몰입감 높음"),
    (["무섭", "공포", "소름"], "공포 분위기 강함"),
    (["소재", "설정", "오컬트"], "소재 흥미로움"),
    (["재밌", "존잼", "흥미"], "재미 있음"),
    (["잘 만들", "완성도", "깔끔"], "완성도 좋음"),
]

NEGATIVE_RULES = [
    (["지루", "루즈", "늘어", "재미없"], "전개 지루함"),
    (["개연성", "억지", "뜬금"], "스토리 아쉬움"),
    (["후반", "결말", "마무리"], "후반부 아쉬움"),
    (["이해 안", "모르겠", "난해"], "이해 어려움"),
    (["cg", "괴수", "사무라이"], "설정 이질감"),
    (["실망", "별로", "아쉽"], "완성도 아쉬움"),
]


# ---------------------------
# Text utilities
# ---------------------------
def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def match_rules(text: str) -> List[str]:
    normalized = normalize_text(text)
    phrases: List[str] = []

    for keywords, label in POSITIVE_RULES:
        if any(keyword in normalized for keyword in keywords):
            phrases.append(label)

    for keywords, label in NEGATIVE_RULES:
        if any(keyword in normalized for keyword in keywords):
            phrases.append(label)

    # 중복 제거
    phrases = list(dict.fromkeys(phrases))
    return phrases


def ensure_phrase_count(phrases: List[str], text: str) -> List[str]:
    normalized = normalize_text(text)

    if len(phrases) == 0:
        if "좋" in normalized or "잘" in normalized:
            phrases = ["긍정 반응", "감상 표현"]
        elif "별로" in normalized or "아쉽" in normalized or "실망" in normalized:
            phrases = ["부정 반응", "감상 표현"]
        else:
            phrases = ["기타 의견", "감상 표현"]

    elif len(phrases) == 1:
        if "좋" in normalized or "잘" in normalized:
            phrases.append("긍정 반응")
        elif "별로" in normalized or "아쉽" in normalized or "실망" in normalized:
            phrases.append("부정 반응")
        else:
            phrases.append("감상 표현")

    return phrases[:5]


# ---------------------------
# Mode 1: Dummy
# ---------------------------
def extract_key_phrases_dummy(input_data: dict) -> dict:
    request = LLMRequestSchema.model_validate(input_data)

    results = []
    for review in request.reviews:
        results.append(
            {
                "review_id": review.review_id,
                "key_phrases": ["기타 의견", "감상 표현"],
            }
        )

    response = LLMResponseSchema(
        job_id=request.job_id,
        movie_id=request.movie_id,
        results=results,
    )
    return response.model_dump(mode="json")


# ---------------------------
# Mode 2: Rule-based
# ---------------------------
def extract_key_phrases_rule_based(input_data: dict) -> dict:
    request = LLMRequestSchema.model_validate(input_data)

    results = []

    for review in request.reviews:
        phrases = match_rules(review.text)
        phrases = ensure_phrase_count(phrases, review.text)

        results.append(
            {
                "review_id": review.review_id,
                "key_phrases": phrases,
            }
        )

    response = LLMResponseSchema(
        job_id=request.job_id,
        movie_id=request.movie_id,
        results=results,
    )
    return response.model_dump(mode="json")


# ---------------------------
# Mode 3: OpenAI
# ---------------------------
def extract_key_phrases_openai(input_data: dict) -> dict:
    request = LLMRequestSchema.model_validate(input_data)
    client = _get_openai_client()

    if client is None:
        print("[LLM] OPENAI_API_KEY not found. Fallback to rule_based mode.")
        return extract_key_phrases_rule_based(input_data)

    system_instruction = """
당신은 영화 리뷰 분석가입니다.
주어진 각 리뷰마다 핵심 표현을 2~5개 추출하세요.
각 표현은 짧고 명확한 한국어 구문이어야 합니다.
반드시 review_id를 유지해야 하며, JSON 형식으로만 응답하세요.
"""

    prompt = f"""
분석할 리뷰 데이터:
{json.dumps([r.model_dump(mode="json") for r in request.reviews], ensure_ascii=False, indent=2)}

출력 형식:
{{
  "results": [
    {{
      "review_id": "r1",
      "key_phrases": ["연기 좋음", "스토리 아쉬움"]
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        response_obj = LLMResponseSchema(
            job_id=request.job_id,
            movie_id=request.movie_id,
            results=parsed.get("results", []),
        )
        return response_obj.model_dump(mode="json")

    except (ValueError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[LLM] OpenAI response parse failed: {e}")
        return extract_key_phrases_rule_based(input_data)

    except (APIError, OpenAIError, TimeoutError) as e:
        print(f"[LLM] OpenAI call failed: {e}")
        return extract_key_phrases_rule_based(input_data)


# ---------------------------
# Dispatcher
# ---------------------------
def extract_key_phrases(input_data: dict, mode: str = "rule_based") -> dict:
    if mode == "dummy":
        print("[LLM] mode=dummy")
        return extract_key_phrases_dummy(input_data)

    if mode == "rule_based":
        print("[LLM] mode=rule_based")
        return extract_key_phrases_rule_based(input_data)

    if mode == "openai":
        print("[LLM] mode=openai")
        return extract_key_phrases_openai(input_data)

    raise ValueError(f"Unsupported mode: {mode}")