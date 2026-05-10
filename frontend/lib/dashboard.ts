import type {
  DashboardMoviesResponse,
  DashboardSummary,
} from "./types";

import summaryMock from "./mock/dashboard-summary.json";
import moviesMock from "./mock/dashboard-movies.json";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// 백엔드 대시보드 API가 준비될 때까지 mock 사용.
// .env에 NEXT_PUBLIC_USE_MOCK_DASHBOARD=false 를 넣으면 실제 API 호출.
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_DASHBOARD !== "false";

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  if (USE_MOCK) {
    return summaryMock as DashboardSummary;
  }

  const res = await fetch(`${BASE_URL}/dashboard/summary`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`대시보드 summary 조회 실패: ${res.status}`);
  }
  return res.json();
}

export async function fetchDashboardMovies(): Promise<DashboardMoviesResponse> {
  if (USE_MOCK) {
    return moviesMock as DashboardMoviesResponse;
  }

  const res = await fetch(`${BASE_URL}/dashboard/movies`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`대시보드 movies 조회 실패: ${res.status}`);
  }
  return res.json();
}