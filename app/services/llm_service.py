import json
import os
from pathlib import Path
from typing import Optional

from openai import OpenAI, APIError, OpenAIError

from app.schemas import LLMRequestSchema, LLMResponseSchema


def _get_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def extract_key_phrases_openai(input_data: dict) -> dict:
    """README 9-2 규격(job_id, movie_id, results)에 맞게 OpenAI API를 활용해 핵심 표현을 추출한다."""
    request = LLMRequestSchema.model_validate(input_data)

    client = _get_openai_client()

    # API 키가 없으면 즉시 더미 결과로 폴백하여 파이프라인을 유지한다.
    if client is None:
        return extract_key_phrases_dummy(input_data)

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
        return response_obj.model_dump(mode="json")

    except (ValueError, json.JSONDecodeError, KeyError, TypeError):
        # 응답 JSON 파싱 실패 시에도 서비스는 계속 동작해야 한다.
        return extract_key_phrases_dummy(input_data)
    except (APIError, OpenAIError, TimeoutError):
        # OpenAI 호출 실패 시 더미 결과로 폴백한다.
        return extract_key_phrases_dummy(input_data)


def extract_key_phrases_dummy(input_data: dict) -> dict:
    """README 9-2 규격(job_id, movie_id, results)에 맞는 고정 더미 LLM 결과를 생성한다."""
    request = LLMRequestSchema.model_validate(input_data)

    # 하드코딩된 더미 결과
    results = [
        {
            "review_id": "r1",
            "key_phrases": ["연기 좋음", "스토리 지루함"],
        },

    ]

    response = LLMResponseSchema(
        job_id=request.job_id,
        movie_id=request.movie_id,
        results=results,
    )
    return response.model_dump(mode="json")


def process_json_file(input_filepath: str, output_filepath: str, use_openai: bool = False) -> None:
    """요청 JSON(README 9-1)을 읽어 응답 JSON(README 9-2)로 저장한다.
    
    Args:
        input_filepath: 입력 JSON 파일 경로
        output_filepath: 출력 JSON 파일 경로
        use_openai: True면 OpenAI API 사용, False면 더미 데이터 사용
    """
    input_path = Path(input_filepath)
    output_path = Path(output_filepath)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_filepath}")

    with input_path.open("r", encoding="utf-8") as f:
        input_data = json.load(f)

    # use_openai 플래그에 따라 함수 선택
    if use_openai:
        output_data = extract_key_phrases_openai(input_data)
    else:
        output_data = extract_key_phrases_dummy(input_data)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)