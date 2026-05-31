"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Granularity = "day" | "week";

type TrafficPoint = { date: string; count: number };

type TrafficResponse = {
  movie_id: string;
  movie_title: string;
  granularity: Granularity;
  total_reviews: number;
  points: TrafficPoint[];
};

type Props = {
  movieId: string;
};

// "2026-05-03" → "5/3" (축 라벨용 — 연도 생략으로 가독성 확보)
function shortDate(iso: string): string {
  const [, m, d] = iso.split("-");
  if (!m || !d) return iso;
  return `${Number(m)}/${Number(d)}`;
}

// 툴팁 헤더용 — granularity 주(週)면 "주 시작" 뉘앙스 추가
function tooltipDate(iso: string, granularity: Granularity): string {
  return granularity === "week" ? `${shortDate(iso)} 주` : shortDate(iso);
}

type TooltipPayload = { payload: TrafficPoint };

function WatchaTooltip({
  active,
  payload,
  granularity,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  granularity: Granularity;
}) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload;
  return (
    <div className="rounded-[8px] border border-[#e8e3d6] bg-white px-3 py-2 shadow-[0_8px_24px_-12px_rgba(20,15,5,0.35)]">
      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
        {tooltipDate(point.date, granularity)}
      </p>
      <p className="mt-0.5 font-serif text-[16px] font-medium tabular-nums text-[#ff2c63]">
        {point.count.toLocaleString()}
        <span className="ml-1 text-[12px] font-normal text-[#6b6760]">건</span>
      </p>
    </div>
  );
}

export default function ReviewTrafficChart({ movieId }: Props) {
  const [granularity, setGranularity] = useState<Granularity>("day"); // 기본 일별
  const [cache, setCache] = useState<
    Partial<Record<Granularity, TrafficResponse>>
  >({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const data = cache[granularity];

  useEffect(() => {
    if (!movieId) return;
    if (cache[granularity]) return; // 이미 받은 모드는 재호출 안 함 (캐싱)

    let cancelled = false;

    async function fetchTraffic() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const res = await fetch(
          `/api/review-traffic?movieId=${encodeURIComponent(
            movieId
          )}&granularity=${granularity}`,
          { cache: "no-store" }
        );

        if (!res.ok) {
          throw new Error(`트래픽 API 요청 실패: ${res.status}`);
        }

        const json: TrafficResponse = await res.json();
        if (!cancelled) {
          setCache((current) => ({ ...current, [granularity]: json }));
        }
      } catch {
        if (!cancelled) {
          setErrorMessage("트래픽 데이터를 불러오지 못했습니다.");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchTraffic();

    return () => {
      cancelled = true;
    };
  }, [movieId, granularity, cache]);

  const points = data?.points ?? [];
  const hasData = points.length > 0;

  return (
    <div className="rounded-[10px] border border-[#e8e3d6] bg-white p-7">
      {/* 헤더: 제목 + 우측 상단 [일별][주별] 토글 */}
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="font-serif text-[20px] font-medium text-[#161616]">
          리뷰 트래픽
        </h2>
        <div className="flex gap-1">
          {(["day", "week"] as Granularity[]).map((g) => {
            const isActive = granularity === g;
            return (
              <button
                key={g}
                type="button"
                onClick={() => setGranularity(g)}
                aria-pressed={isActive}
                className={`rounded-full border px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.2em] transition-colors ${
                  isActive
                    ? "border-[#ff2c63] text-[#ff2c63]"
                    : "border-[#e8e3d6] text-[#9a958b] hover:border-[#dcd6c5] hover:text-[#6b6760]"
                }`}
              >
                {g === "day" ? "일별" : "주별"}
              </button>
            );
          })}
        </div>
      </div>

      {/* 본문: 빈 movieId / 에러 / 로딩 / 빈 데이터 / 차트 */}
      <div className="mt-5 h-[220px]">
        {!movieId ? (
          <div className="flex h-full items-center justify-center rounded-[8px] border border-dashed border-[#dcd6c5] bg-[#fbf9f3] text-sm text-[#9a958b]">
            트래픽 데이터가 없습니다.
          </div>
        ) : errorMessage ? (
          <div className="flex h-full items-center justify-center rounded-[8px] border border-dashed border-[#dcd6c5] bg-[#fbf9f3] text-sm text-[#9a958b]">
            {errorMessage}
          </div>
        ) : isLoading && !data ? (
          <div className="flex h-full items-center justify-center rounded-[8px] border border-dashed border-[#e8e3d6] bg-[#fbf9f3] font-mono text-[11px] uppercase tracking-[0.2em] text-[#9a958b]">
            불러오는 중…
          </div>
        ) : !hasData ? (
          <div className="flex h-full items-center justify-center rounded-[8px] border border-dashed border-[#dcd6c5] bg-[#fbf9f3] text-sm text-[#9a958b]">
            집계된 리뷰 트래픽이 없습니다.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={points}
              margin={{ top: 8, right: 12, bottom: 4, left: -8 }}
            >
              <CartesianGrid stroke="#efe9d8" vertical={false} />
              <XAxis
                dataKey="date"
                tickFormatter={shortDate}
                tick={{ fontSize: 11, fill: "#9a958b" }}
                stroke="#e8e3d6"
                tickLine={false}
                minTickGap={24}
              />
              <YAxis
                allowDecimals={false}
                width={44}
                tick={{ fontSize: 11, fill: "#9a958b" }}
                stroke="#e8e3d6"
                tickLine={false}
              />
              <Tooltip
                cursor={{ stroke: "#e8e3d6", strokeWidth: 1 }}
                content={<WatchaTooltip granularity={granularity} />}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#ff2c63"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: "#ff2c63", stroke: "#fff", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* 푸터: 총 리뷰 수 (ElementScoreChart 푸터 톤과 동일) */}
      <p className="mt-5 border-t border-[#e8e3d6] pt-4 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760]">
        총 리뷰: {data ? data.total_reviews.toLocaleString() : "—"}건
      </p>
    </div>
  );
}
