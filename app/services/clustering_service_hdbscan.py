from collections import defaultdict
from typing import List

import hdbscan

from app.services.embedding_service import EmbeddingService


embedding_service = EmbeddingService()

# 1. 의미 통합 (핵심)
NORMALIZATION_MAP = {
    "전개 지루함": "스토리 아쉬움",
    "후반부 아쉬움": "스토리 아쉬움",
    "긍정 반응": "재미 있음",
}

# 2. 저정보 phrase (제거 대상)
LOW_INFO_PHRASES = {
    "감상 표현",
}

# 3. 완전 일치 치환 (깔끔한 topic용)
EXACT_REPLACE_MAP = {
    "연기 좋음": "연기",
    "영상미 좋음": "영상미",
    "완성도 좋음": "완성도",
}


def preprocess_text(text: str) -> str:
    text = text.strip()

    # 완전 일치 치환
    if text in EXACT_REPLACE_MAP:
        return EXACT_REPLACE_MAP[text]

    return text


def normalize_phrase(text: str) -> str:
    text = text.strip()
    return NORMALIZATION_MAP.get(text, text)


def make_topic(texts: list[str]) -> str:
    if not texts:
        return "기타"

    first = texts[0].strip()
    if not first:
        return "기타"

    return first[:10]


def run_hdbscan_clustering(phrases) -> List[dict]:
    if not phrases:
        return []

    # 🔥 1. 전처리 + 정규화 + 저정보 제거
    normalized_texts = []
    valid_indices = []

    for idx, phrase in enumerate(phrases):
        cleaned = preprocess_text(phrase.text)
        base_text = cleaned if cleaned else phrase.text
        normalized = normalize_phrase(base_text)

        # ❗ 저정보 phrase 제거
        if normalized in LOW_INFO_PHRASES:
            continue

        normalized_texts.append(normalized)
        valid_indices.append(idx)

    if not normalized_texts:
        return []

    # 🔥 2. 임베딩
    embeddings = embedding_service.encode(normalized_texts)

    # 🔥 3. HDBSCAN
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        min_samples=1,
        metric="euclidean",
        cluster_selection_method="eom",
    )

    labels = clusterer.fit_predict(embeddings)

    # 🔥 4. 그룹핑
    grouped = defaultdict(list)
    noise_items = []

    for i, label in enumerate(labels):
        original_idx = valid_indices[i]
        phrase = phrases[original_idx]

        item = {
            "review_id": phrase.review_id,
            "text": phrase.text,
            "normalized_text": normalized_texts[i],
        }

        if label == -1:
            noise_items.append(item)
            continue

        grouped[int(label)].append(item)

    # 🔥 5. 1차 cluster 생성
    temp_results = []
    for cluster_id, items in grouped.items():
        item_texts = [item["normalized_text"] for item in items]
        topic = make_topic(item_texts)

        temp_results.append(
            {
                "cluster_id": int(cluster_id),
                "topic": topic,
                "items": [
                    {
                        "review_id": item["review_id"],
                        "text": item["text"],
                    }
                    for item in items
                ],
            }
        )

    # 🔥 6. 같은 topic 병합
    merged_by_topic = defaultdict(list)

    for cluster in temp_results:
        merged_by_topic[cluster["topic"]].extend(cluster["items"])

    # 🔥 7. 최종 결과
    results = []
    for new_cluster_id, (topic, items) in enumerate(merged_by_topic.items()):
        results.append(
            {
                "cluster_id": new_cluster_id,
                "topic": topic,
                "items": items,
            }
        )

    # 🔥 8. noise → 기타
    if 0 < len(noise_items) <= max(3, len(normalized_texts) // 5):
        results.append(
            {
                "cluster_id": len(results),
                "topic": "기타",
                "items": [
                    {
                        "review_id": item["review_id"],
                        "text": item["text"],
                    }
                    for item in noise_items
                ],
            }
        )

    results.sort(key=lambda x: x["cluster_id"])
    return results