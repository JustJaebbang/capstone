from typing import List
from collections import defaultdict

from sklearn.cluster import KMeans

from app.services.embedding_service import EmbeddingService


embedder = EmbeddingService()


def preprocess_text(text: str) -> str:
    remove_words = [
        "너무", "정말",
        "좋다", "좋음", "좋고", "좋았다",
        "별로", "별로다",
        "어색하다", "어색함", "어색해서",
        "인상적이다", "뛰어나다",
        "아름답다", "예쁘다",
        "몰입", "몰입도", "아쉬웠다"
    ]

    for w in remove_words:
        text = text.replace(w, "")

    return text.strip()


def make_topic(texts: list[str]) -> str:
    if not texts:
        return "기타"

    first = texts[0].strip()
    if not first:
        return "기타"

    return first[:10]


def run_kmeans_clustering(phrases) -> List[dict]:
    if not phrases:
        return []

    texts = [preprocess_text(p.text) for p in phrases]

    cleaned_texts = []
    for phrase, cleaned in zip(phrases, texts):
        cleaned_texts.append(cleaned if cleaned else phrase.text)

    embeddings = embedder.encode(cleaned_texts)

    n_clusters = min(4, len(phrases))
    if n_clusters == 0:
        return []

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=50,
    )
    labels = kmeans.fit_predict(embeddings)

    grouped = defaultdict(list)
    for phrase, label in zip(phrases, labels):
        grouped[int(label)].append(phrase)

    results = []
    for cluster_id, items in grouped.items():
        item_texts = [item.text for item in items]
        topic = make_topic(item_texts)

        results.append(
            {
                "cluster_id": int(cluster_id),
                "topic": topic,
                "items": [
                    {
                        "review_id": item.review_id,
                        "text": item.text,
                    }
                    for item in items
                ],
            }
        )

    results.sort(key=lambda x: x["cluster_id"])
    return results