import json
import os
import re
from typing import List, Optional

from openai import OpenAI, APIError, OpenAIError

from app.schemas import (
    LLMRequestSchema,
    LLMResponseSchema,
    LLMResultItem,
    PhraseSentimentItem,
)


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
당신은 한국어 영화 리뷰를 클러스터링하기 좋은 핵심 평가 phrase로 정리하는 분석기입니다.

목표:
- 각 리뷰에서 관객이 평가한 영화 요소를 짧고 대표성 있는 phrase로 추출합니다.
- phrase는 이후 토픽 클러스터링에 바로 사용되므로, 너무 추상적이거나 긴 문장형 표현을 피합니다.
- 각 phrase에는 반드시 sentiment를 positive 또는 negative 중 하나로 붙입니다.
- 출력은 반드시 JSON 객체만 반환합니다. 설명, 마크다운, 코드블록은 절대 쓰지 않습니다.

phrase 작성 규칙:
- 리뷰 1개당 1~3개만 추출합니다.
- phrase는 보통 2~5어절, 20자 안팎의 짧은 한국어 구문으로 씁니다.
- 기본 형식은 "평가 대상 + 평가"입니다.
  예: "배우 연기 좋음", "후반 전개 아쉬움", "사운드 압도적", "영상미 뛰어남", "장르 전환 어색함", "몰입감 좋음"
- 하나의 phrase에는 평가 대상 토픽을 반드시 하나만 담습니다.
- 여러 요소가 한 문장에 섞이면 한 phrase에 몰아넣지 말고, 핵심 요소별로 분리합니다.
  예: "음악 연출 연기 스토리 영상미 좋음" -> "사운드 좋음", "연출 좋음", "영상미 좋음" 중 중요한 것만 최대 3개
  예: "스케일 스토리 영상미 OST 좋음" -> "스케일 압도적", "서사 좋음", "영상미 좋음", "사운드 좋음" 중 중요한 것만 최대 3개
  예: "영상미와 사운드 경이" -> "영상미 뛰어남", "사운드 압도적"
  예: "음악 연출력 미침" -> "사운드 좋음", "연출 좋음"
- "영상미 사운드", "음악 연출", "연기 스토리", "스케일 영상미"처럼 두 개 이상의 토픽을 한 phrase에 함께 쓰지 않습니다.
- 복합 감상문은 아래 토픽 중 가장 직접적인 평가 대상으로 쪼갭니다.
  토픽 예: 배우 연기, 인물 존재감, 전개, 서사, 연출, 영상미, 사운드, 액션, 몰입감, 공포감, 장르 전환, 개연성, 러닝타임, 극장 체험
- 리뷰 원문을 그대로 길게 복사하지 말고 클러스터링하기 쉬운 표준 표현으로 바꿉니다.
  예: "반지의 제왕 급" -> "스케일 압도적" 또는 "서사 완성도 높음"
  예: "끝나는게 아쉬움" -> "몰입감 좋음" 또는 "러닝타임 아쉬움"
- 너무 일반적인 표현은 피합니다: "좋음", "별로", "재밌음", "기타 의견", "명작", "아쉬움"
- "기타", "기타 의견", "긍정 반응", "부정 반응"은 사용하지 않습니다.
- 배우, 감독, 음악감독 같은 인물이 평가의 핵심 대상이면 이름을 phrase에 포함해도 됩니다.
  예: "티모시 연기 좋음", "김고은 연기 압도적", "한스 짐머 사운드 압도적"
- 인물명이 핵심이 아니면 범주로 일반화합니다.
  예: "배우 연기 좋음", "감독 연출 좋음"
- 같은 의미의 phrase를 한 리뷰 안에서 중복하지 않습니다.
- review_id는 입력값과 정확히 동일하게 유지합니다.
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
- sentiment 값은 반드시 "positive" 또는 "negative"만 사용하세요.
- phrase는 토픽 라벨로 쓸 수 있게 구체적인 평가 대상이 드러나야 합니다.
- 한 phrase에 "음악/연출/연기/스토리/영상미"처럼 여러 토픽을 나열하지 마세요.
- 복합 phrase를 만들 바에는 phrase 개수를 늘려 분리하세요. 단, 리뷰당 최대 3개를 넘기지 마세요.
- 금지 예: "영상미 사운드 뛰어남", "음악 연출력 좋음", "스케일과 영상미 좋음", "연기 스토리 좋음"
- 권장 예: "영상미 뛰어남", "사운드 압도적", "연출 좋음", "스케일 압도적", "배우 연기 좋음"
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
            phrase_items = [
                PhraseSentimentItem(
                    text=phrase["text"],
                    sentiment=phrase["sentiment"],
                )
                for phrase in item.get("phrases", [])
            ]

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
