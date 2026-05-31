from fastapi import APIRouter

from app.schemas import DashboardMoviesResponse, DashboardSummaryResponse
from app.services.dashboard_service import (
    get_dashboard_movies,
    get_dashboard_summary,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/movies", response_model=DashboardMoviesResponse)
def read_dashboard_movies():
    return get_dashboard_movies()


@router.get("/summary", response_model=DashboardSummaryResponse)
def read_dashboard_summary():
    return get_dashboard_summary()
