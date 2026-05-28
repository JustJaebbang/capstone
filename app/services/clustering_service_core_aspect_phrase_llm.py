from __future__ import annotations

import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple

from openai import OpenAI

from app.schemas import ClusterGroup, ClusterResponseSchema


ALLOWED_CORE_ASPECTS = [
    "연기", "캐릭터", "스토리", "속도감", "연출", "영상미", "음향",
    "분위기", "몰입감", "긴장감", "감정", "메시지", "재미",
    "만족도", "완성도", "관람경험", "기타",
]


class PhraseLLMCoreAspectClusteringService:
    def __init__(self, model: str = "gpt-5.4-nano") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def cluster(self, cluster_response: ClusterResponseSchema) -> ClusterResponseSchema:
        grouped: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        review_count_map: Dict[Tuple[str, str], int] = defaultdict(int)

        for cluster in cluster_response.clusters:
            phrase_aspects = self._classify_phrases_with_llm(
                topic=cluster.topic,
                sentiment=cluster.sentiment,
                phrases=cluster.phrases,
            )

            for phrase, aspect in phrase_aspects.items():
                grouped[(aspect, cluster.sentiment)].append(phrase)

            for aspect in set(phrase_aspects.values()):
                key = (aspect, cluster.sentiment)
                aspect_count = list(phrase_aspects.values()).count(aspect)
                ratio = aspect_count / max(len(cluster.phrases), 1)
                review_count_map[key] += max(1, round(cluster.review_count * ratio))

        result_clusters = self._build_core_clusters(grouped, review_count_map)

        return ClusterResponseSchema(
            job_id=cluster_response.job_id,
            movie_id=cluster_response.movie_id,
            movie_title=cluster_response.movie_title,
            clusters=result_clusters,
        )

    def _classify_phrases_with_llm(
        self,
        topic: str,
        sentiment: str,
        phrases: List[str],
    ) -> Dict[str, str]:
        if not phrases:
            return {}

        prompt = {
            "task": "영화 리뷰 phrase 각각을 가장 적절한 핵심요소로 분류하세요.",
            "allowed_core_aspects": ALLOWED_CORE_ASPECTS,
            "current_cluster_topic": topic,
            "sentiment": sentiment,
            "phrases": phrases,
            "rules": [
                "각 phrase마다 반드시 allowed_core_aspects 중 하나를 선택한다.",
                "기존 cluster topic은 참고만 하고, phrase 자체 의미를 우선한다.",
                "러닝타임, 지루함, 늘어짐, 템포, 호흡은 속도감으로 분류한다.",
                "재관람, 추천, 만족, 불만, 영화값, 돈 아까움, 시간 낭비, 평점은 만족도로 분류한다.",
                "완성도, 작품성, 웰메이드, 명작, 허접함, 퀄리티 평가는 완성도로 분류한다.",
                "아이맥스, 돌비, 4DX, 극장, 영화관, 관람 환경, 특수관은 관람경험으로 분류한다.",
                "CG, 촬영, 화면, 비주얼, 색감, 그래픽, 분장은 영상미로 분류한다.",
                "전개, 개연성, 결말, 각본, 플롯, 서사, 용두사미는 스토리로 분류한다.",
                "장면 구성, 편집, 전환, 감독의 표현 방식은 연출로 분류한다.",
                "사운드, 음악, OST, BGM, 효과음은 음향으로 분류한다.",
                "배우, 연기력, 캐스팅, 딕션은 연기로 분류한다.",
                "인물, 주인공, 빌런, 캐릭터성, 관계성은 캐릭터로 분류한다.",
                "공포감, 오컬트, 서늘함, 장르적 분위기는 분위기로 분류한다.",
                "몰입, 집중, 빠져듦은 몰입감으로 분류한다.",
                "긴장, 쫄림, 서스펜스는 긴장감으로 분류한다.",
                "감동, 여운, 공감, 눈물, 감정선은 감정으로 분류한다.",
                "주제, 상징, 의미, 교훈, 사회적 메시지는 메시지로 분류한다.",
                "재밌음, 노잼, 웃김, 흥미는 재미로 분류한다.",
                "기타는 정말 어디에도 넣기 어려울 때만 선택한다.",
            ],
            "response_format": {
                "items": [
                    {
                        "phrase": "원본 phrase",
                        "core_aspect": "핵심요소",
                    }
                ]
            },
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "너는 영화 리뷰 phrase를 공통 핵심요소로 분류하는 분석기야. "
                            "반드시 JSON 형식으로만 응답해."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(prompt, ensure_ascii=False),
                    },
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                return {phrase: "기타" for phrase in phrases}

            data = json.loads(content)
            items = data.get("items", [])

            result: Dict[str, str] = {}

            for item in items:
                phrase = item.get("phrase")
                aspect = item.get("core_aspect", "기타")

                if phrase not in phrases:
                    continue

                if aspect not in ALLOWED_CORE_ASPECTS:
                    aspect = "기타"

                result[phrase] = aspect

            for phrase in phrases:
                if phrase not in result:
                    result[phrase] = "기타"

            return result

        except Exception as e:
            print(f"[Phrase LLM core aspect error] {e}")
            return {phrase: "기타" for phrase in phrases}

    def _build_core_clusters(
        self,
        grouped: Dict[Tuple[str, str], List[str]],
        review_count_map: Dict[Tuple[str, str], int],
    ) -> List[ClusterGroup]:
        intermediate = []

        for (topic, sentiment), phrases in grouped.items():
            deduped_phrases = self._dedupe_preserve_order(phrases)

            intermediate.append(
                {
                    "topic": topic,
                    "sentiment": sentiment,
                    "count": len(phrases),
                    "review_count": review_count_map[(topic, sentiment)],
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
                    sentiment=item["sentiment"],
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


_default_service = PhraseLLMCoreAspectClusteringService()


def cluster_by_core_aspect_phrase_llm(
    cluster_response: ClusterResponseSchema,
) -> ClusterResponseSchema:
    return _default_service.cluster(cluster_response)