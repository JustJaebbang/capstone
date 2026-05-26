import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.movies import router as movies_router
from app.routers.jobs import router as jobs_router
from app.routers.reviews import router as reviews_router
from app.routers.llm import router as llm_router
from app.routers.cluster import router as cluster_router
from app.routers.collection import router as collection_router
from app.routers.dashboard import router as dashboard_router
from app.services import scheduler as scheduler_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_service.init_scheduler()
    yield
    # Shutdown
    scheduler_service.shutdown_scheduler()


app = FastAPI(title="Movie Review Analysis System", lifespan=lifespan)

# CORS 설정 — 프론트(localhost:3000)에서 백엔드 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router)
app.include_router(jobs_router)
app.include_router(reviews_router)
app.include_router(llm_router)
app.include_router(cluster_router)
app.include_router(collection_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"message": "Movie Review Analysis System API"}