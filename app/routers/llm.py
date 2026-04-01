from fastapi import APIRouter

from app.schemas import LLMRequestSchema, LLMResponseSchema
from app.services.llm_service import (
    LLM_MODE,
    extract_key_phrases_by_mode,
)

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/extract", response_model=LLMResponseSchema)
def extract_key_phrases(payload: LLMRequestSchema):
    """
    LLM 핵심 표현 추출 엔드포인트
    
    Args:
        payload: LLM 요청 스키마 (job_id, movie_id, reviews 등)
        실행 모드: app.services.llm_service의 LLM_MODE 값을 사용
    """
    print(
        f"[LLM] router extract: job_id={payload.job_id}, movie_id={payload.movie_id}, mode={LLM_MODE}, review_count={len(payload.reviews)}",
        flush=True,
    )

    result = extract_key_phrases_by_mode(
        payload.model_dump(mode="json"),
        mode=LLM_MODE,
    )

    print(
        f"[LLM] router done: job_id={payload.job_id}, mode={LLM_MODE}, result_count={len(result.get('results', []))}",
        flush=True,
    )
    
    return LLMResponseSchema.model_validate(result)
