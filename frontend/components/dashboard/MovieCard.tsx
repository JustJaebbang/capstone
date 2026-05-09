"use client";

import { useRouter } from "next/navigation";
import type { DashboardMovie } from "@/lib/types";
import SentimentDonut from "./SentimentDonut";
import KeywordRow from "./KeywordRow";

type Props = {
  movie: DashboardMovie;
};

function formatDateTime(iso: string | null): string {
  if (!iso) return "-";
  const d = new Date(iso);
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${month}월 ${day}일 ${hh}:${mm}`;
}

export default function MovieCard({ movie }: Props) {
  const router = useRouter();
  const isCompleted = movie.job_status === "completed";

  const handleSelect = () => {
    router.push(`/movies/${movie.movie_id}/analyzing`);
  };

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex gap-5">
        {/* 좌측: 포스터 */}
        <div className="flex h-44 w-32 shrink-0 items-center justify-center rounded-xl bg-gray-100 text-xs text-gray-400">
          {movie.poster_url ? (
            <span>이미지</span>
          ) : (
            <span className="px-2 text-center">{movie.movie_title}</span>
          )}
        </div>

        {/* 중앙 + 우측 */}
        <div className="flex flex-1 flex-col">
          {/* 상단: 제목 + 분석 상태 */}
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {movie.movie_title}
              </h2>

             <div className="mt-2 flex flex-wrap gap-2 text-xs">
                <span className="rounded-full bg-gray-100 px-2.5 py-1 text-gray-600">
                  {movie.release_year}
                </span>
                {movie.genres.map((genre) => (
                  <span
                    key={genre}
                    className="rounded-full bg-purple-50 px-2.5 py-1 text-purple-700"
                  >
                    {genre}
                  </span>
                ))}
                <span className="rounded-full bg-blue-50 px-2.5 py-1 text-blue-700">
                  {movie.source}
                </span>
                {movie.is_active && (
                  <span className="rounded-full bg-green-50 px-2.5 py-1 text-green-700">
                    활성
                  </span>
                )}
              </div>

              {movie.notes && (
                <p className="mt-2 text-sm text-gray-500">{movie.notes}</p>
              )}
              <p className="mt-1 text-xs text-gray-400">ID: {movie.movie_id}</p>
            </div>

            {/* 분석 완료 배지 */}
            {isCompleted && (
              <div className="flex items-center gap-2 text-xs">
                <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-2.5 py-1 font-semibold text-green-700">
                  ✓ 최근 분석
                </span>
                <span className="text-gray-400">
                  {formatDateTime(movie.job_completed_at)}
                </span>
              </div>
            )}
          </div>

          {/* 중간: 감성 비율 + TOP 키워드 + 버튼 */}
          <div className="mt-4 grid grid-cols-[auto_1fr_auto] items-center gap-6">
            {/* 감성 비율 */}
            <div className="flex items-center gap-4">
              <div>
                <p className="text-xs font-semibold text-gray-500">감성 비율</p>
                <SentimentDonut
                  positivePercent={movie.sentiment.positive_percent}
                  negativePercent={movie.sentiment.negative_percent}
                  size={88}
                  strokeWidth={14}
                />
              </div>

              <div className="flex flex-col gap-1 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-green-600 font-semibold">긍정</span>
                  <span className="text-green-600 font-bold">
                    {movie.sentiment.positive_percent}%
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-red-600 font-semibold">부정</span>
                  <span className="text-red-600 font-bold">
                    {movie.sentiment.negative_percent}%
                  </span>
                </div>
                <p className="mt-1 text-xs text-gray-400">
                  총 리뷰 {movie.review_count.toLocaleString()}개
                </p>
              </div>
            </div>

            {/* TOP 키워드 */}
            <div>
              <p className="mb-2 text-xs font-semibold text-gray-500">
                TOP 키워드
              </p>
              <div className="flex flex-col gap-1.5">
                {movie.top_keywords.map((kw) => (
                  <KeywordRow key={kw.rank} keyword={kw} />
                ))}
              </div>
            </div>

            {/* 버튼 — 분석 시작 */}
            <button
              type="button"
              onClick={handleSelect}
              className="rounded-xl bg-blue-600 px-5 py-3 text-center text-sm font-semibold text-white hover:bg-blue-700"
            >
              분석 시작
            </button>
          </div>

          {/* 하단 메타 */}
          <div className="mt-4 flex items-center gap-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
            <span>⭐ 개봉일: {movie.release_date ?? "-"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}