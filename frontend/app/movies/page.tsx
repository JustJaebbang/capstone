import Link from "next/link";

import {
  fetchDashboardMovies,
  fetchDashboardSummary,
} from "@/lib/dashboard";

import StatCardGrid from "@/components/dashboard/StatCardGrid";
import MovieCardGrid from "@/components/dashboard/MovieCardGrid";
import DashboardSidebar from "@/components/dashboard/DashboardSidebar";
import ServiceFlowBanner from "@/components/dashboard/ServiceFlowBanner";

export default async function MoviesPage() {
  // 두 API 병렬 호출 (mock이라도 패턴은 동일)
  const [summary, moviesResponse] = await Promise.all([
    fetchDashboardSummary(),
    fetchDashboardMovies(),
  ]);

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto max-w-7xl">
        {/* 헤더 */}
        <div className="mb-8 flex items-start justify-between">
          <div>
            <p className="text-sm font-semibold text-blue-600">
              Movie Review Analysis
            </p>
            <h1 className="mt-2 text-3xl font-bold text-gray-900">
              분석 대상 영화 목록
            </h1>
            <p className="mt-2 text-gray-600">
              백엔드 API에서 불러온 영화 목록입니다.
            </p>
          </div>

          <Link
            href="/"
            className="rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-100"
          >
            🏠 홈으로
          </Link>
        </div>

        {/* 본문 — 좌측 컨텐츠 + 우측 사이드바 */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
          {/* 좌측 컬럼 */}
          <div className="flex flex-col gap-6">
            <StatCardGrid summary={summary} />
            <MovieCardGrid movies={moviesResponse.items} />
            <ServiceFlowBanner />
          </div>

          {/* 우측 사이드바 */}
          <DashboardSidebar summary={summary} />
        </div>
      </div>
    </main>
  );
}