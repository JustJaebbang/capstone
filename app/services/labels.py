import json
import logging
import os
from collections import Counter
from typing import List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

LABEL_MAP = {
    ("연기", "positive"): "연기가 좋아요",
    ("연기", "negative"): "연기가 아쉬워요",
    ("캐릭터", "positive"): "캐릭터가 매력적이에요",
    ("캐릭터", "negative"): "캐릭터가 아쉬워요",
    ("스토리", "positive"): "스토리가 좋아요",
    ("스토리", "negative"): "스토리가 아쉬워요",
    ("연출", "positive"): "연출이 좋아요",
    ("연출", "negative"): "연출이 아쉬워요",
    ("영상미", "positive"): "영상미가 좋아요",
    ("영상미", "negative"): "영상미가 아쉬워요",
    ("음향", "positive"): "음향이 좋아요",
    ("음향", "negative"): "음향이 아쉬워요",
    ("속도감", "positive"): "전개 속도감이 좋아요",
    ("속도감", "negative"): "전개가 늘어져요",
    ("재미", "positive"): "재미있어요",
    ("재미", "negative"): "재미가 아쉬워요",
    ("몰입감", "positive"): "몰입감이 높아요",
    ("몰입감", "negative"): "몰입감이 떨어져요",
    ("감정", "positive"): "감정적으로 와닿아요",
    ("감정", "negative"): "감정선이 아쉬워요",
    ("메시지", "positive"): "메시지가 인상적이에요",
    ("메시지", "negative"): "메시지가 아쉬워요",
    ("분위기", "positive"): "분위기가 좋아요",
    ("분위기", "negative"): "분위기가 아쉬워요",
    ("긴장감", "positive"): "긴장감이 넘쳐요",
    ("긴장감", "negative"): "긴장감이 부족해요",
    ("만족도", "positive"): "전반적으로 만족스러워요",
    ("만족도", "negative"): "전반적으로 아쉬워요",
    ("완성도", "positive"): "완성도가 높아요",
    ("완성도", "negative"): "완성도가 아쉬워요",
    ("관람경험", "positive"): "관람 경험이 좋아요",
    ("관람경험", "negative"): "관람 경험이 아쉬워요",
    ("기타", "positive"): "긍정적인 반응이 있어요",
    ("기타", "negative"): "아쉬운 반응이 있어요",
}


def make_label(topic: str, sentiment: str) -> str:
    return LABEL_MAP.get((topic, sentiment), f"{topic} ({sentiment})")


# --- top_opinions용 LLM 라벨 생성 -------------------------------------------
# top3 의견 라벨을, 클러스터에서 가장 많이 언급된 대표 phrase들을 근거로
# 구어체 한 줄로 생성한다(구체성 우선). 키 누락·API 오류·파싱 실패 시에는
# 해당 항목을 make_label()로 폴백하고 그 사실을 logger.warning으로 남긴다.

LABEL_MODEL = "gpt-5.4-nano"
REPRESENTATIVE_N = 15

_client: Optional[OpenAI] = None
_client_init_failed = False


def _get_client() -> Optional[OpenAI]:
    global _client, _client_init_failed
    if _client is None and not _client_init_failed:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            _client_init_failed = True
            return None
        _client = OpenAI(api_key=api_key)
    return _client


def _representative_phrases(cluster: dict, llm_result: dict, n: int) -> List[str]:
    """클러스터 phrase 중 리뷰에서 가장 많이 언급된 상위 n개를 대표로 뽑는다.
    phrase_llm은 dedup하면서 빈도를 버리므로, 원본 llm_result에서 다시 센다.
    """
    phrase_set = set(cluster.get("phrases", []))
    counts: Counter = Counter()
    for item in llm_result["results"]:
        for phrase in item["phrases"]:
            text = phrase["text"]
            if text in phrase_set:
                counts[text] += 1

    top = [text for text, _ in counts.most_common(n)]
    # 빈도가 잡히지 않은 phrase로 부족분 보충 (원래 순서 유지)
    if len(top) < n:
        seen = set(top)
        for text in cluster.get("phrases", []):
            if text not in seen:
                top.append(text)
                if len(top) >= n:
                    break
    return top[:n]


def generate_top_opinion_labels(
    clusters: List[dict],
    llm_result: dict,
    job_id: str = "",
) -> List[str]:
    """top 클러스터들의 구어체 라벨을 배치 1회 호출로 생성.

    반환 길이는 clusters와 동일하고 순서가 정렬되어 있다. 어떤 이유로든
    생성에 실패한 항목은 make_label() 폴백으로 채우고 경고 로그를 남긴다.
    """
    if not clusters:
        return []

    fallback = [make_label(c["topic"], c["sentiment"]) for c in clusters]

    client = _get_client()
    if client is None:
        logger.warning(
            "[label] OPENAI_API_KEY 없음 - top_opinions %d개 전부 make_label 폴백 (job=%s)",
            len(clusters), job_id,
        )
        return fallback

    items = [
        {
            "index": i,
            "topic": c["topic"],
            "sentiment": c["sentiment"],
            "phrases": _representative_phrases(c, llm_result, REPRESENTATIVE_N),
        }
        for i, c in enumerate(clusters)
    ]
    prompt = {
        "지시": "각 항목은 한 영화의 같은 주제·감정 리뷰 표현 묶음이다. 항목마다 "
                "추출된 표현의 구체 내용을 살려 구어체 한 줄 라벨을 만들어라.",
        "items": items,
        "규칙": [
            "topic 이름만 반복하지 말고 표현 속 구체 포인트(소재/장면/대상)를 반영한다.",
            "구어체로, 30자 이내, '~다는 반응이 많아요/~했다는 평이 많아요' 류.",
            "sentiment가 negative면 아쉬움·불만이 분명히 드러나야 한다.",
            "여러 항목에서 같은 핵심 단어를 반복하지 말고 서로 구별되게 쓴다.",
        ],
        "출력형식": {"labels": [{"index": 0, "label": "..."}]},
    }

    try:
        response = client.chat.completions.create(
            model=LABEL_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "너는 영화 리뷰 의견 묶음을 구어체 한 줄 라벨로 요약하는 카피라이터다. 반드시 JSON만 답한다.",
                },
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        by_index = {
            int(row["index"]): (row.get("label") or "").strip()
            for row in data.get("labels", [])
            if "index" in row
        }
    except Exception as e:
        logger.warning(
            "[label] LLM 라벨 생성 실패(%s) - top_opinions %d개 전부 폴백 (job=%s)",
            e, len(clusters), job_id,
        )
        return fallback

    labels: List[str] = []
    missing = []
    for i, c in enumerate(clusters):
        label = by_index.get(i)
        if label:
            labels.append(label)
        else:
            labels.append(fallback[i])
            missing.append(f"{c['topic']}/{c['sentiment']}")

    if missing:
        logger.warning(
            "[label] %d개 항목 라벨 누락 - make_label 폴백: %s (job=%s)",
            len(missing), ", ".join(missing), job_id,
        )
    return labels
