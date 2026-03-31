from fastapi import FastAPI

from app.routers.movies import router as movies_router
from app.routers.jobs import router as jobs_router
from app.routers.results import router as results_router
from app.routers.reviews import router as reviews_router # 데이터셋 연결 확인용 API
from app.routers.llm import router as llm_router

app = FastAPI(title="Movie Review Analysis System")

app.include_router(movies_router)
app.include_router(jobs_router)
app.include_router(results_router)
app.include_router(reviews_router)
app.include_router(llm_router)

@app.get("/")
def root():
    return {"message": "Movie Review Analysis System API"}