"""기타 클러스터 토픽 재분류 서비스.

용도:
1) 파이프라인 통합용 in-memory API (`reclassify_etc_clusters`)
   - `run_cluster_for_job`에서 호출. `topic == "기타"` 클러스터의 phrase 묶음을
     LLM에 보내 정해진 후보 토픽 중 하나로 교체한다.
2) ad-hoc CLI
   - 클러스터 결과 파일(`data/cluster_result_mv_*.json`)을 직접 재분류하여
     `*_reclassified.json`으로 저장. 원본은 보존.

CLI 사용:
    uv run python -m app.services.topic_service
    uv run python -m app.services.topic_service data/cluster_result_mv_001.json
"""

import glob
import json
import os
import sys
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI, APIError, OpenAIError

from app.schemas import ClusterResponseSchema

# pydantic-settings는 .env의 database_url만 읽고 os.environ까지 전파하지 않으므로
# OPENAI_API_KEY가 .env에만 있는 경우를 위해 모듈 로드 시 한 번 채워둔다.
load_dotenv(override=False)


# 정식 토픽 후보 집합.
# clustering_service_*.topic_keywords 및 labels.LABEL_MAP과 어휘를 정확히 맞춤.
# LLM은 반드시 이 중 하나만 답해야 한다. "기타"도 유효한 답이다.
CANDIDATE_TOPICS: List[str] = [
    "연기",
    "캐릭터",
    "스토리",
    "연출",
    "영상미",
    "음향",
    "속도감",
    "재미",
    "몰입감",
    "감정",
    "메시지",
    "기타",
]

# LLM 프롬프트용: 각 토픽이 무엇을 평가하는지에 대한 한 줄 정의.
TOPIC_DEFINITIONS = {
    "연기": "배우의 연기, 캐스팅, 연기력 평가",
    "캐릭터": "인물 설정, 인물 매력, 관계성, 주조연 캐릭터",
    "스토리": "이야기 내용 — 사건/플롯/전개/결말/개연성/반전/서사",
    "연출": "이야기를 보여주는 방식 — 장면 구성/카메라/편집/컷/분위기 연출",
    "영상미": "미장센, 화면, 색감, 촬영, 비주얼, 스케일, CG/VFX",
    "음향": "음악, OST, 사운드, BGM, 효과음",
    "속도감": "템포, 호흡, 늘어짐, 러닝타임 길이",
    "재미": "영화 전체의 종합적 재미/지루함, 흥미, 유쾌함",
    "몰입감": "몰입, 집중, 흡입력, 긴장감",
    "감정": "감동, 여운, 먹먹함, 공감, 눈물 등 정서적 반응",
    "메시지": "감독/영화가 전달하려는 주제 의식, 상징, 사회적 함의, 교훈",
    "기타": "위 어디에도 속하지 않는 평가 (가격, 상영관, 관람 매너, 흥행, 정치적 논쟁 등)",
}

DEFAULT_INPUT_GLOB = "data/cluster_result_mv_*.json"
# 재분류 결과물(*_reclassified.json)을 다시 입력으로 잡지 않기 위한 표식.
RECLASSIFIED_SUFFIX = "_reclassified"


def _get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def _render_topic_guide() -> str:
    """프롬프트에 넣을 '후보 토픽 + 정의' 블록을 생성."""
    return "\n".join(
        f"- {topic}: {TOPIC_DEFINITIONS.get(topic, '')}" for topic in CANDIDATE_TOPICS
    )


def classify_etc_cluster(
    client: OpenAI,
    phrases: List[str],
    sentiment: str,
) -> str:
    """기타 클러스터의 phrase 묶음을 LLM에 보내 후보 토픽 중 1개를 받는다.

    - OpenAI 1회 호출. 응답으로 topic / confidence / is_mixed 를 받는다.
    - confidence 가 high 가 아니거나(여러 주제가 비등하게 섞여) is_mixed 가 true
      이면 분류를 신뢰하지 않고 "기타"를 그대로 유지한다.
    - 응답이 후보 집합 밖이거나 비어 있어도 "기타"를 유지한다.
    - API 오류·파싱 실패 시에도 예외를 던지지 않고 "기타"를 반환한다.
    """
    topic_guide = _render_topic_guide()
    candidate_str = ", ".join(CANDIDATE_TOPICS)
    phrases_json = json.dumps(phrases, ensure_ascii=False)

    system_instruction = f"""
당신은 한국어 영화 리뷰에서 추출된 평가 표현(phrase) 묶음을 보고,
이 묶음이 어떤 영화 평가 토픽에 속하는지 판단하는 분류기입니다.

== 후보 토픽 (반드시 이 중 정확히 하나만 사용) ==
{topic_guide}

== 판단 규칙 ==
- 묶음 안의 phrase 다수가 공통으로 가리키는 평가 대상을 하나 고릅니다.
- "기타"를 제외한 후보 중 명확히 들어맞는 것이 있으면 그것을 선택합니다.
- 어느 영화 요소에도 속하지 않는 평가(가격, 상영관, 관람 매너, 흥행, 정치적
  논쟁 등)가 중심이면 topic 을 "기타"로 둡니다.
- confidence: 고른 topic 이 이 묶음을 얼마나 잘 대표하는지.
  - "high": 묶음의 대다수 phrase 가 그 topic 하나로 명확히 모임.
  - "medium": 그 topic 이 우세하지만 애매하거나 근거가 약함.
  - "low": 어느 topic 도 뚜렷하게 우세하지 않음.
- is_mixed: 묶음의 phrase 들이 둘 이상의 서로 다른 topic 으로 비등하게 나뉘어
  있으면 true, 한 topic 으로 수렴하면 false.
- 출력은 JSON 객체만. 설명, 마크다운, 코드블록은 절대 쓰지 않습니다.
"""

    prompt = f"""
아래는 한 클러스터에 묶인 평가 표현(phrase) 목록입니다.
이 클러스터의 sentiment는 "{sentiment}" 입니다.

phrases:
{phrases_json}

이 클러스터에 가장 적절한 토픽 하나를 후보 집합에서 골라 아래 형식으로만 답하세요.

반환 JSON 형식:
{{"topic": "{candidate_str} 중 하나", "confidence": "high|medium|low", "is_mixed": true 또는 false}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-nano",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        topic = (parsed.get("topic") or "").strip()
        confidence = (parsed.get("confidence") or "").strip().lower()
        is_mixed = bool(parsed.get("is_mixed"))

        if topic not in CANDIDATE_TOPICS:
            print(f"[Topic] 후보 밖 응답 '{topic}' -> '기타' 유지")
            return "기타"

        # LLM이 후보 topic을 골랐어도, 확신이 낮거나 여러 주제가 섞여 있으면
        # 잘못된 강제 분류보다 "기타" 유지가 안전하다.
        if is_mixed:
            print(f"[Topic] 여러 주제 혼합 (제안 '{topic}') -> '기타' 유지")
            return "기타"

        if confidence != "high":
            print(
                f"[Topic] confidence={confidence or '없음'} "
                f"(제안 '{topic}') -> '기타' 유지"
            )
            return "기타"

        return topic

    except (ValueError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[Topic] 응답 파싱 실패: {e} -> '기타' 유지")
        return "기타"

    except (APIError, OpenAIError, TimeoutError) as e:
        print(f"[Topic] OpenAI 호출 실패: {e} -> '기타' 유지")
        return "기타"


def reclassify_etc_clusters(response: ClusterResponseSchema) -> ClusterResponseSchema:
    """파이프라인 통합용. ClusterResponseSchema 안의 topic=="기타" 클러스터를
    in-place 재분류하고 같은 객체를 반환한다.

    - OPENAI_API_KEY가 없으면 전체 스킵 (원본 반환).
    - phrases가 비어있는 클러스터는 LLM 호출하지 않음.
    - cluster_id, count, review_count, phrases, sentiment는 보존. topic만 변경.
    """
    client = _get_openai_client()
    if client is None:
        print("[Topic] OPENAI_API_KEY not found. Skip reclassification.")
        return response

    changed = 0
    for cluster in response.clusters:
        if cluster.topic != "기타":
            continue
        if not cluster.phrases:
            continue
        new_topic = classify_etc_cluster(
            client,
            list(cluster.phrases),
            cluster.sentiment,
        )
        if new_topic != cluster.topic:
            print(f"[Topic] {cluster.cluster_id}: 기타 -> {new_topic}")
            cluster.topic = new_topic
            changed += 1

    print(f"[Topic] reclassified {changed} '기타' cluster(s)")
    return response


def reclassify_file(client: OpenAI, input_path: str) -> Tuple[str, List[Tuple[str, str]]]:
    """클러스터 결과 파일 1개를 읽어 기타 클러스터를 재분류한다 (CLI용).

    반환: (출력 파일 경로, [(cluster_id, 새 토픽), ...]).
    `topic` 필드만 교체하고 count / sentiment / phrases 는 건드리지 않는다.
    원본은 보존하고 `*_reclassified.json`으로 새로 쓴다.
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    changes: List[Tuple[str, str]] = []

    for cluster in data.get("clusters", []):
        if cluster.get("topic") != "기타":
            continue

        new_topic = classify_etc_cluster(
            client,
            cluster.get("phrases", []),
            cluster.get("sentiment", ""),
        )
        cluster["topic"] = new_topic
        changes.append((cluster.get("cluster_id", "?"), new_topic))

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_reclassified{ext}"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path, changes


def main(argv: List[str]) -> int:
    if len(argv) > 1:
        paths = argv[1:]
    else:
        # 기본 글로브는 이전 실행이 만든 *_reclassified.json 을 다시 입력으로
        # 잡지 않도록 걸러낸다 (명시적 인자로는 허용).
        paths = [
            p
            for p in sorted(glob.glob(DEFAULT_INPUT_GLOB))
            if RECLASSIFIED_SUFFIX not in os.path.basename(p)
        ]

    if not paths:
        print(f"[Topic] 처리할 파일이 없습니다 (패턴: {DEFAULT_INPUT_GLOB})")
        return 1

    client = _get_openai_client()
    if client is None:
        print("[Topic] OPENAI_API_KEY가 없습니다. 재분류를 건너뜁니다.")
        return 1

    for input_path in paths:
        print(f"\n[Topic] 처리: {input_path}")
        output_path, changes = reclassify_file(client, input_path)

        if not changes:
            print("  기타 클러스터 없음 — 변경 사항 없음")
        else:
            for cluster_id, new_topic in changes:
                marker = "(유지)" if new_topic == "기타" else "->"
                print(f"  {cluster_id}: 기타 {marker} {new_topic}")

        print(f"  저장: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
