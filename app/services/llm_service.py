import json
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI, APIError, OpenAIError

from app.schemas import (
    LLMRequestSchema,
    LLMResponseSchema,
    LLMResultItem,
    PhraseSentimentItem,
)

# pydantic-settings는 .env의 database_url만 읽고 os.environ까지 전파하지 않으므로
# OPENAI_API_KEY가 .env에만 있는 경우를 위해 모듈 로드 시 한 번 채워둔다.
# 이미 환경에 설정돼 있다면 override=False로 그대로 둔다.
load_dotenv(override=False)


def _get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def infer_sentiment(phrase: str) -> str:
    negative_keywords = [
        "아쉬움", "지루함", "어려움", "이질감", "부정 반응", "아쉬움", "부족", "약함"
    ]
    positive_keywords = [
        "좋음", "높음", "있음", "흥미로움", "긍정 반응", "인상적", "매력적"
    ]

    for keyword in negative_keywords:
        if keyword in phrase:
            return "negative"

    for keyword in positive_keywords:
        if keyword in phrase:
            return "positive"

    return "positive"


def extract_key_phrases_rule_based(text: str) -> List[str]:
    normalized = normalize_text(text)

    topic_keywords = {
        "연기 좋음": ["연기", "배우", "연기력", "캐스팅"],
        "스토리 좋음": ["스토리", "전개", "서사", "결말", "개연성"],
        "스토리 아쉬움": ["스토리", "전개", "서사", "결말", "개연성", "억지", "뜬금"],
        "영상미 좋음": ["영상미", "비주얼", "화면", "촬영", "색감", "스케일", "cg"],
        "연출 좋음": ["연출", "장면", "분위기", "구성"],
        "음향 좋음": ["음악", "ost", "사운드", "음향", "효과음"],
        "전개 지루함": ["지루", "루즈", "늘어", "길다", "러닝타임", "템포"],
        "재미 있음": ["재밌", "재미", "흥미진진", "존잼"],
        "재미 아쉬움": ["노잼", "재미없", "심심"],
        "몰입감 높음": ["몰입", "집중", "긴장감", "빠져들"],
        "감정적으로 좋음": ["감동", "여운", "먹먹", "울림"],
        "메시지 좋음": ["메시지", "주제", "의미"],
        "이해 어려움": ["난해", "복잡", "이해 안", "모르겠"],
    }

    sentiment_hints = {
        "positive": ["좋", "훌륭", "뛰어", "인상적", "압도적", "강렬", "신선", "재밌", "재미있", "감동", "몰입", "매력"],
        "negative": ["아쉽", "별로", "지루", "루즈", "늘어", "실망", "부족", "약하", "어색", "난해", "복잡"],
    }

    scored = []

    for label, keywords in topic_keywords.items():
        score = 0

        for keyword in keywords:
            if keyword in normalized:
                score += 1

        if "좋음" in label or "있음" in label or "높음" in label:
            for hint in sentiment_hints["positive"]:
                if hint in normalized:
                    score += 1

        if "아쉬움" in label or "지루함" in label or "어려움" in label:
            for hint in sentiment_hints["negative"]:
                if hint in normalized:
                    score += 1

        if score > 0:
            scored.append((label, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    phrases = []
    for label, _ in scored:
        if label not in phrases:
            phrases.append(label)

    # 너무 빈약하면 감정 fallback 추가
    if not phrases:
        if any(word in normalized for word in sentiment_hints["positive"]):
            phrases = ["긍정 반응"]
        elif any(word in normalized for word in sentiment_hints["negative"]):
            phrases = ["부정 반응"]
        else:
            phrases = ["기타 의견"]

    # 너무 적으면 보조 표현 추가
    if len(phrases) == 1:
        if any(word in normalized for word in sentiment_hints["positive"]):
            if "긍정 반응" not in phrases:
                phrases.append("긍정 반응")
        elif any(word in normalized for word in sentiment_hints["negative"]):
            if "부정 반응" not in phrases:
                phrases.append("부정 반응")
        else:
            if "기타 의견" not in phrases:
                phrases.append("기타 의견")

    return phrases[:3]


def build_phrase_items(phrases: List[str]) -> List[PhraseSentimentItem]:
    items = []
    for phrase in phrases:
        items.append(
            PhraseSentimentItem(
                text=phrase,
                sentiment=infer_sentiment(phrase),
            )
        )
    return items


def extract_phrases_dummy(payload: LLMRequestSchema) -> LLMResponseSchema:
    results: List[LLMResultItem] = []

    for review in payload.reviews:
        phrases = ["기타 의견"]
        results.append(
            LLMResultItem(
                review_id=review.review_id,
                phrases=build_phrase_items(phrases),
            )
        )

    return LLMResponseSchema(
        job_id=payload.job_id,
        movie_id=payload.movie_id,
        movie_title=payload.movie_title,
        results=results,
    )


def extract_phrases_rule_based(payload: LLMRequestSchema) -> LLMResponseSchema:
    results: List[LLMResultItem] = []

    for review in payload.reviews:
        extracted_phrases = extract_key_phrases_rule_based(review.text)
        phrase_items = build_phrase_items(extracted_phrases)

        results.append(
            LLMResultItem(
                review_id=review.review_id,
                phrases=phrase_items,
            )
        )

    return LLMResponseSchema(
        job_id=payload.job_id,
        movie_id=payload.movie_id,
        movie_title=payload.movie_title,
        results=results,
    )


def extract_phrases_openai(payload: LLMRequestSchema) -> LLMResponseSchema:
    client = _get_openai_client()

    if client is None:
        print("[LLM] OPENAI_API_KEY not found. Fallback to rule_based mode.")
        return extract_phrases_rule_based(payload)

    reviews_json = json.dumps(
        [{"review_id": r.review_id, "text": r.text} for r in payload.reviews],
        ensure_ascii=False,
        separators=(",", ":"),
    )

    system_instruction = """
당신은 한국어 영화 리뷰를 클러스터링하기 좋은 (phrase, sentiment) 쌍으로 정리하는 분석기입니다.

== 작업 흐름 (각 리뷰마다 순서대로) ==
1. 리뷰에서 관객이 평가한 영화 요소를 1~3개 식별합니다.
2. 각 요소에 대해 어떤 점을 평가했는지 짧은 phrase로 작성합니다.
3. phrase에 sentiment("positive" 또는 "negative")를 부여합니다.
4. (text, sentiment) 두 필드를 모두 채워 반환합니다.

== phrase 작성 규칙 ==
- 리뷰 1개당 phrase는 1~3개만. 같은 의미의 phrase를 한 리뷰 안에서 중복하지 않습니다.
- 길이는 보통 2~5어절, 20자 안팎의 짧은 한국어 구문. 리뷰 원문을 길게 복사하지 않습니다.
- 기본 형식: "평가 대상 + 평가" (예: "배우 연기 좋음", "후반 전개 아쉬움", "사운드 압도적").
- 하나의 phrase에는 한 가지 평가 대상만 담습니다. 여러 요소가 섞여 있으면 phrase를 나눕니다.
  예: "음악 연출 연기 좋음" -> ["사운드 좋음", "연출 좋음", "배우 연기 좋음"] 중 핵심만
  예: "영상미와 사운드 경이" -> ["영상미 뛰어남", "사운드 압도적"]
- 너무 일반적인 표현 금지: "좋음", "별로", "명작", "기타 의견", "긍정 반응", "부정 반응".
- 배우/감독/음악감독 등 인물이 평가의 핵심이면 이름을 phrase에 포함해도 됩니다.
  예: "김고은 연기 압도적", "한스 짐머 사운드 압도적".
- 인물명이 핵심이 아니면 일반 범주로 씁니다. 예: "배우 연기 좋음", "감독 연출 좋음".
- review_id는 입력값과 정확히 동일하게 유지합니다.

== 출력 형식 ==
- 출력은 JSON 객체만. 설명, 마크다운, 코드블록은 절대 쓰지 않습니다.
"""

    prompt = f"""
아래 영화 리뷰 배열을 분석하세요.

입력:
{reviews_json}

반환 JSON 형식:
{{
  "results": [
    {{
      "review_id": "입력 review_id",
      "phrases": [
        {{
          "text": "짧은 평가 관점",
          "sentiment": "positive 또는 negative"
        }}
      ]
    }}
  ]
}}

필수 조건:
- results 길이는 입력 리뷰 수와 같아야 합니다.
- 모든 입력 review_id가 정확히 한 번씩 포함되어야 합니다.
- 각 phrase는 text, sentiment 두 필드를 모두 포함해야 합니다.
- sentiment 값은 "positive" 또는 "negative" 중 하나입니다.
- JSON 외의 텍스트는 출력하지 마세요.
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

        results: List[LLMResultItem] = []
        for item in parsed.get("results", []):
            phrase_items = []
            for phrase in item.get("phrases", []):
                phrase_items.append(
                    PhraseSentimentItem(
                        text=phrase["text"],
                        sentiment=phrase["sentiment"],
                    )
                )

            results.append(
                LLMResultItem(
                    review_id=item["review_id"],
                    phrases=phrase_items,
                )
            )

        return LLMResponseSchema(
            job_id=payload.job_id,
            movie_id=payload.movie_id,
            movie_title=payload.movie_title,
            results=results,
        )

    except (ValueError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[LLM] OpenAI response parse failed: {e}")
        return extract_phrases_rule_based(payload)

    except (APIError, OpenAIError, TimeoutError) as e:
        print(f"[LLM] OpenAI call failed: {e}")
        return extract_phrases_rule_based(payload)


def extract_phrases_with_sentiment(
    payload: LLMRequestSchema,
    mode: str = "openai",
) -> LLMResponseSchema:
    if mode == "dummy":
        print("[LLM] mode=dummy")
        return extract_phrases_dummy(payload)

    if mode == "rule_based":
        print("[LLM] mode=rule_based")
        return extract_phrases_rule_based(payload)

    if mode == "openai":
        print("[LLM] mode=openai")
        return extract_phrases_openai(payload)

    raise ValueError(f"Unsupported mode: {mode}")
