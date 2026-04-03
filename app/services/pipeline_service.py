import requests

from app.schemas import LLMRequestSchema, ReviewItem, ClusterRequestSchema, PhraseItem
from app.services.job_service import get_job, update_job_status
from app.services.llm_service import extract_key_phrases_dummy, extract_key_phrases_openai
from app.services.review_service import fetch_reviews
from app.services.result_service import save_llm_result, get_llm_result_by_job_id

def build_llm_request(
    job, 
    review_limit: int = 50, 
    source_mode: str = "dataset",
    ) -> LLMRequestSchema:
    """
    리뷰 데이터 원본(dataset or real)에서 리뷰를 B -> C 요청 스키마로 변환한다.
    """
    source_reviews = fetch_reviews(
        movie_id=job.movie_id,
        review_limit=review_limit,
        source_mode=source_mode,
    )

    reviews = [
        ReviewItem(
            review_id=review.review_id,
            text=review.text,
        )
        for review in source_reviews
    ]

    return LLMRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        target_date=job.target_date,
        reviews=reviews,
    )


def call_llm_api(payload: dict, llm_mode: str = "rule_based") -> dict:
    """
    B -> C 실제 API 호출
    C는 /llm/extract 엔드포인트를 통해 동작한다.
    """
    url = f"http://127.0.0.1:8000/llm/extract?mode={llm_mode}"

    response = requests.post(url, json=payload, timeout=60)

    if response.status_code != 200:
        raise Exception(f"LLM API failed: {response.status_code}, {response.text}")

    return response.json()



def run_llm_pipeline_for_job(
    job, 
    review_limit: int = 50, 
    source_mode: str = "dataset", 
    llm_mode: str = "rule_based",
    ) -> dict:
    """
    dataset -> B -> C -> B 전체 실행
    """
    # 1. 데이터 소스에서 리뷰를 읽고 B → C 스키마 생성
    llm_request = build_llm_request(
        job=job, 
        review_limit=review_limit,
        source_mode=source_mode,
        )
    payload = llm_request.model_dump(mode="json")

    print(f"[Pipeline] source_mode = {source_mode}")
    print(f"[Pipeline] llm_mode = {llm_mode}")
    
    total_reviews = len(payload["reviews"])
    print(f"[Pipeline] selected reviews = {total_reviews}")

    # 2. C 호출
    llm_result = call_llm_api(payload, llm_mode=llm_mode)
    
    # 3. 입력 리뷰 수 == 출력 결과 수 검증
    input_count = len(payload["reviews"])
    output_count = len(llm_result["results"])

    if input_count != output_count:
        raise ValueError(
            f"LLM result count mismatch: input={input_count}, output={output_count}"
        )
    
    save_llm_result(
        job_id=job.job_id,
        movie_id=job.movie_id,
        result_data=llm_result,
    )
    print(f"[Pipeline] llm results received: {output_count}")
    print("[Pipeline] llm_results saved")
    
    return llm_result


def build_cluster_request_from_llm_result(job, llm_result: dict) -> ClusterRequestSchema:
    """
    C->B 결과를 B->D 요청 스키마로 변환
    """
    phrases = []

    for result_item in llm_result["results"]:
        review_id = result_item["review_id"]

        for phrase_text in result_item["key_phrases"]:
            phrases.append(
                PhraseItem(
                    review_id=review_id,
                    text=phrase_text,
                )
            )

    return ClusterRequestSchema(
        job_id=job.job_id,
        movie_id=job.movie_id,
        movie_title=job.movie_title,
        phrases=phrases,
    )


def build_cluster_request_for_job(job) -> ClusterRequestSchema:
    """
    저장된 llm_results.json에서 해당 job의 결과를 읽고
    B->D 요청 스키마로 변환
    """
    llm_saved = get_llm_result_by_job_id(job.job_id)
    
    if llm_saved is None:
        raise ValueError(f"LLM result not found for job_id={job.job_id}")

    llm_result = llm_saved["result"]
    
    return build_cluster_request_from_llm_result(job=job, llm_result=llm_result)
