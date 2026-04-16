from fastapi import APIRouter

from app.schemas import LLMRequestSchema, LLMResponseSchema
from app.services.llm_service import extract_phrases_with_sentiment

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/extract", response_model=LLMResponseSchema)
def extract_key_phrases(
    payload: LLMRequestSchema,
    mode: str = "rule_based",
) -> LLMResponseSchema:
    result = extract_phrases_with_sentiment(payload, mode=mode)
    return result