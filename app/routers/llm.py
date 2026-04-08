from fastapi import APIRouter, HTTPException

from app.schemas import LLMRequestSchema, LLMResponseSchema


router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/extract", response_model=LLMResponseSchema)
def extract_key_phrases_api(payload: LLMRequestSchema, mode: str = "rule_based"):
    try:
        result = extract_key_phrases_api(payload.model_dump(mode="json"), mode=mode)
        return LLMResponseSchema.model_validate(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))