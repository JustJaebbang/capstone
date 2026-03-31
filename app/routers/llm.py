from fastapi import APIRouter

from app.schemas import LLMRequestSchema, LLMResponseSchema
from app.services.llm_service import extract_key_phrases_dummy, extract_key_phrases_openai

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/extract", response_model=LLMResponseSchema)
def extract_key_phrases(payload: LLMRequestSchema, use_openai: bool = False):
    """
    LLM 핵심 표현 추출 엔드포인트
    
    Args:
        payload: LLM 요청 스키마 (job_id, movie_id, reviews 등)
        use_openai: True면 OpenAI API 사용, False면 더미 데이터 사용 (default: False)
    """
    if use_openai:
        result = extract_key_phrases_openai(payload.model_dump(mode="json"))
    else:
        result = extract_key_phrases_dummy(payload.model_dump(mode="json"))
    
    return LLMResponseSchema.model_validate(result)
