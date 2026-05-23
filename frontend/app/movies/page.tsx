import Link from "next/link";

import {
  fetchDashboardMovies,
  fetchDashboardSummary,
} from "@/lib/dashboard";

import MovieCardGrid from "@/components/dashboard/MovieCardGrid";
import RecentNoticeBanner from "@/components/dashboard/RecentNoticeBanner";

export default async function MoviesPage() {
  const [moviesResponse, summary] = await Promise.all([
    fetchDashboardMovies(),
    fetchDashboardSummary(),
  ]);

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto max-w-7xl">
        {/* 최근 분석 공지 */}
        <RecentNoticeBanner activities={summary.recent_activities} />

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

        {/* 본문 */}
        <div className="flex flex-col gap-6">
          <MovieCardGrid movies={moviesResponse.items} />
        </div>
      </div>
    </main>
  );
}