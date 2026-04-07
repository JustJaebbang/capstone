from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Tuple

import hdbscan
import numpy as np
from sentence_transformers import SentenceTransformer

from app.schemas import (
    ClusterGroup,
    ClusterRequestSchema,
    ClusterResponseSchema,
    PhraseItem,
)


class HDBSCANClusteringService:
    """
    D 모듈 전용 클러스터링 서비스

    역할:
    - PhraseItem(review_id, text, sentiment) 리스트를 입력으로 받음
    - 문장 임베딩 후 HDBSCAN으로 1차 군집화
    - 군집별 topic 추론
    - 같은 topic 안에서도 sentiment(positive/negative) 기준으로 다시 분리
    - ClusterResponseSchema 형태로 반환
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        min_cluster_size: int = 2,
        min_samples: int | None = 1,
    ) -> None:
        self.model = SentenceTransformer(model_name)
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples

        # topic 후보 키워드 사전
        self.topic_keywords: Dict[str, List[str]] = {
            "연기": [
                "연기", "배우", "배역", "캐스팅", "호연", "열연", "연기력",
                "캐릭터 소화", "연기 좋", "연기 아쉽"
            ],
            "캐릭터": [
                "캐릭터", "인물", "주인공", "조연", "빌런", "서브", "관계성",
                "인물 설정", "인물 매력"
            ],
            "스토리": [
                "스토리", "서사", "전개", "구성", "플롯", "개연성", "결말",
                "반전", "후반부", "중반부", "초반부", "내용"
            ],
            "연출": [
                "연출", "장면", "씬", "편집", "구도", "연출력", "컷", "전환",
                "연출 좋", "연출 아쉽"
            ],
            "영상미": [
                "영상미", "미장센", "화면", "비주얼", "색감", "촬영", "영상",
                "구도", "배경미"
            ],
            "음향": [
                "음향", "음악", "ost", "사운드", "bgm", "효과음", "소리"
            ],
            "속도감": [
                "속도감", "템포", "호흡", "늘어짐", "지루", "루즈", "빠르",
                "전개 속도"
            ],
            "재미": [
                "재미", "재밌", "흥미", "유쾌", "웃기", "즐겁", "볼만", "재미있"
            ],
            "몰입감": [
                "몰입", "집중", "긴장감", "빠져들", "몰입감", "흡입력"
            ],
            "감정": [
                "감정", "여운", "울림", "감동", "눈물", "먹먹", "감정선",
                "공감", "슬픔", "전율"
            ],
            "메시지": [
                "메시지", "의미", "주제", "사회적", "상징", "전달", "해석",
                "풍자", "교훈"
            ],
        }

    def cluster(self, request: ClusterRequestSchema) -> ClusterResponseSchema:
        phrases = request.phrases

        if not phrases:
            return ClusterResponseSchema(
                job_id=request.job_id,
                movie_id=request.movie_id,
                movie_title=request.movie_title,
                clusters=[],
            )

        if len(phrases) == 1:
            single = phrases[0]
            topic = self._infer_topic([single.text])

            return ClusterResponseSchema(
                job_id=request.job_id,
                movie_id=request.movie_id,
                movie_title=request.movie_title,
                clusters=[
                    ClusterGroup(
                        cluster_id="cl_001",
                        topic=topic,
                        sentiment=single.sentiment,
                        count=1,
                        review_count=1,
                        phrases=[single.text],
                    )
                ],
            )

        texts = [p.text for p in phrases]
        embeddings = self._embed_texts(texts)
        labels = self._run_hdbscan(embeddings)

        # 1차: HDBSCAN 라벨 기준으로 묶기
        raw_clusters: Dict[int, List[PhraseItem]] = defaultdict(list)
        noise_items: List[PhraseItem] = []

        for label, phrase in zip(labels, phrases):
            if label == -1:
                noise_items.append(phrase)
            else:
                raw_clusters[int(label)].append(phrase)

        # 2차: 각 raw cluster마다 topic 추론
        # 3차: 같은 topic 안에서 sentiment별로 재분리
        final_groups: Dict[Tuple[str, str], List[PhraseItem]] = defaultdict(list)

        for _, items in raw_clusters.items():
            topic = self._infer_topic([item.text for item in items])
            for item in items:
                final_groups[(topic, item.sentiment)].append(item)

        # noise 처리:
        # 버리지 말고 각 phrase를 개별 topic 판단 후 (topic, sentiment)에 편입
        for item in noise_items:
            topic = self._infer_topic([item.text])
            final_groups[(topic, item.sentiment)].append(item)

        cluster_groups = self._build_cluster_groups(final_groups)

        return ClusterResponseSchema(
            job_id=request.job_id,
            movie_id=request.movie_id,
            movie_title=request.movie_title,
            clusters=cluster_groups,
        )

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings

    def _run_hdbscan(self, embeddings: np.ndarray) -> np.ndarray:
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=False,
        )
        labels = clusterer.fit_predict(embeddings)
        return labels

    def _infer_topic(self, texts: List[str]) -> str:
        """
        키워드 기반 topic 추론
        - 여러 phrase가 들어오면 전체 점수 합산
        - 가장 점수가 높은 topic 선택
        - 전부 0점이면 기타
        """
        joined = " ".join(texts).lower()
        topic_scores: Dict[str, int] = {}

        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in joined:
                    score += joined.count(keyword)
            topic_scores[topic] = score

        best_topic, best_score = max(topic_scores.items(), key=lambda x: x[1])

        if best_score == 0:
            return "기타"
        return best_topic

    def _build_cluster_groups(
        self,
        final_groups: Dict[Tuple[str, str], List[PhraseItem]],
    ) -> List[ClusterGroup]:
        """
        (topic, sentiment) 기준 그룹을 ClusterGroup 리스트로 변환
        정렬 기준:
        1) count 내림차순
        2) review_count 내림차순
        3) topic 오름차순
        4) sentiment 오름차순
        """
        intermediate = []

        for (topic, sentiment), items in final_groups.items():
            deduped_phrases = self._dedupe_preserve_order([item.text for item in items])
            review_ids = {item.review_id for item in items}

            intermediate.append(
                {
                    "topic": topic,
                    "sentiment": sentiment,
                    "count": len(items),
                    "review_count": len(review_ids),
                    "phrases": deduped_phrases,
                }
            )

        intermediate.sort(
            key=lambda x: (
                -x["count"],
                -x["review_count"],
                x["topic"],
                x["sentiment"],
            )
        )

        results: List[ClusterGroup] = []
        for idx, item in enumerate(intermediate, start=1):
            results.append(
                ClusterGroup(
                    cluster_id=f"cl_{idx:03}",
                    topic=item["topic"],
                    sentiment=item["sentiment"],  # type: ignore[arg-type]
                    count=item["count"],
                    review_count=item["review_count"],
                    phrases=item["phrases"],
                )
            )

        return results

    @staticmethod
    def _dedupe_preserve_order(values: List[str]) -> List[str]:
        seen = set()
        deduped = []

        for value in values:
            normalized = value.strip()
            if not normalized:
                continue
            if normalized not in seen:
                seen.add(normalized)
                deduped.append(normalized)

        return deduped


# 프로젝트에서 바로 import해서 쓰기 쉽게 함수형 래퍼도 제공
_default_service = HDBSCANClusteringService()


def cluster_phrases_with_hdbscan(
    request: ClusterRequestSchema,
) -> ClusterResponseSchema:
    return _default_service.cluster(request)