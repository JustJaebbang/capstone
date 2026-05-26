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
    <div className="flex flex-col rounded-2xl border border-gray-200 bg-white p-3.5 shadow-sm">
      {/* 1. 포스터 */}
      <div className="flex h-40 w-full items-center justify-center rounded-lg bg-gray-100 text-xs text-gray-400">
        {movie.poster_url ? (
          <span>이미지</span>
        ) : (
          <span className="px-2 text-center">{movie.movie_title}</span>
        )}
      </div>

      {/* 2. 제목 + 최근 분석 배지 */}
      <div className="mt-3 flex flex-wrap items-start justify-between gap-x-2 gap-y-1">
        <h2 className="text-base font-bold leading-tight text-gray-900">
          {movie.movie_title}
        </h2>

        {isCompleted && (
          <div className="flex shrink-0 items-center gap-1.5 text-[10px]">
            <span className="inline-flex items-center gap-1 whitespace-nowrap rounded-full bg-green-50 px-2 py-0.5 font-semibold text-green-700">
              ✓ 최근 분석
            </span>
            <span className="whitespace-nowrap text-gray-400">
              {formatDateTime(movie.job_completed_at)}
            </span>
          </div>
        )}
      </div>

      {/* 3. 배지 줄 */}
      <div className="mt-2 flex flex-wrap gap-1.5 text-[10px]">
        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">
          {movie.release_year}
        </span>
        <span className="rounded-full bg-blue-50 px-2 py-0.5 text-blue-700">
          {movie.source.toUpperCase()}
        </span>
        {movie.genres.map((genre) => (
          <span
            key={genre}
            className="rounded-full bg-purple-50 px-2 py-0.5 text-purple-700"
          >
            {genre}
          </span>
        ))}
        {movie.is_active && (
          <span className="rounded-full bg-green-50 px-2 py-0.5 text-green-700">
            활성
          </span>
        )}
      </div>

      {/* 4. 메모 + ID */}
      {movie.notes && (
        <p className="mt-2 text-xs text-gray-500">{movie.notes}</p>
      )}
      <p className="mt-1 text-[10px] text-gray-400">ID: {movie.movie_id}</p>

      {/* 5. 감성 비율 */}
      <div className="mt-3 border-t border-gray-100 pt-3">
        <p className="text-[10px] font-semibold uppercase tracking-wide text-gray-500">
          감성 비율
        </p>
        <div className="mt-2 flex items-center gap-3">
          <SentimentDonut
            positivePercent={movie.sentiment.positive_percent}
            negativePercent={movie.sentiment.negative_percent}
            size={64}
            strokeWidth={12}
          />
          <div className="flex flex-col gap-0.5 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-green-600">긍정</span>
              <span className="font-bold text-green-600">
                {movie.sentiment.positive_percent}%
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-red-600">부정</span>
              <span className="font-bold text-red-600">
                {movie.sentiment.negative_percent}%
              </span>
            </div>
            <p className="mt-0.5 text-[10px] text-gray-400">
              총 리뷰 {movie.review_count.toLocaleString()}개
            </p>
          </div>
        </div>
      </div>

      {/* 6. TOP 키워드 */}
      <div className="mt-3 border-t border-gray-100 pt-3">
        <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-gray-500">
          TOP 키워드
        </p>
        <div className="flex flex-col gap-1">
          {movie.top_keywords.map((kw) => (
            <KeywordRow key={kw.rank} keyword={kw} />
          ))}
        </div>
      </div>

      {/* 7. 개봉일 + 분석 시작 버튼 */}
      <div className="mt-3 flex items-center justify-between gap-2 border-t border-gray-100 pt-3 text-[10px] text-gray-500">
        <span className="whitespace-nowrap">
          ⭐ {movie.release_date ?? "-"}
        </span>
        <button
          type="button"
          onClick={handleSelect}
          className="rounded-lg bg-blue-600 px-3 py-1.5 text-center text-xs font-semibold text-white hover:bg-blue-700"
        >
          분석 시작
        </button>
      </div>
    </div>
  );
}
