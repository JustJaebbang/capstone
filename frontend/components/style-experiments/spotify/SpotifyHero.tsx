import type { DashboardMovie, DashboardSummary } from "@/lib/types";

type Props = {
  featured: DashboardMovie;
  summary: DashboardSummary;
};

export default function SpotifyHero({ featured, summary }: Props) {
  const positive = summary.overall_sentiment.positive_percent;
  const negative = summary.overall_sentiment.negative_percent;

  return (
    <section className="relative">
      {/* gradient atmosphere — bleeds into the page below */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[420px]"
        style={{
          background:
            "linear-gradient(180deg, #1db954 0%, rgba(29, 185, 84, 0.45) 30%, rgba(18,18,18,0.95) 80%, #121212 100%)",
        }}
      />

      <div className="flex items-end gap-6 px-8 pb-6 pt-20 sm:gap-8 sm:pt-24">
        {/* "album" cover */}
        <div
          className="flex h-[232px] w-[232px] shrink-0 items-end justify-start overflow-hidden rounded-md p-5"
          style={{
            background:
              "linear-gradient(135deg, #064e2c 0%, #0a0a0a 80%), radial-gradient(at 30% 30%, rgba(30,215,96,0.55), transparent 60%)",
            boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
          }}
        >
          <div>
            <p
              className="text-[10.5px] uppercase text-[#cbcbcb]"
              style={{ fontWeight: 600, letterSpacing: "0.05em" }}
            >
              Today&apos;s mix
            </p>
            <p
              className="mt-2 text-[28px] leading-[1.05] text-white"
              style={{ fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              영화 리뷰
              <br />
              해부 라이브
            </p>
          </div>
        </div>

        {/* meta cluster */}
        <div className="flex min-w-0 flex-1 flex-col gap-3 pb-2">
          <p
            className="text-[12px] text-white"
            style={{ fontWeight: 700 }}
          >
            Playlist
          </p>
          <h1
            className="text-white"
            style={{
              fontFamily:
                "var(--font-geist-sans), 'Apple SD Gothic Neo', system-ui, sans-serif",
              fontSize: "clamp(48px, 7vw, 96px)",
              fontWeight: 700,
              lineHeight: 1,
              letterSpacing: "-0.04em",
            }}
          >
            오늘의 의견 톱{summary.top_keywords_overall.length}.
          </h1>
          <p
            className="max-w-2xl text-[14px] text-[#cbcbcb]"
            style={{ fontWeight: 400 }}
          >
            관객이 가장 많이 한 말, 그날의 감성 비율, 그리고 방금 끝난 배치까지 —
            한 화면에서 같이 듣는 분석 플레이리스트.
          </p>

          {/* author + counts */}
          <div className="mt-1 flex flex-wrap items-center gap-1 text-[14px] text-white">
            <span
              className="flex h-6 w-6 items-center justify-center rounded-full text-[11px] text-black"
              style={{
                background:
                  "linear-gradient(135deg,#1ed760 0%, #14833b 100%)",
                fontWeight: 700,
              }}
            >
              R
            </span>
            <span style={{ fontWeight: 700 }}>review.os</span>
            <span className="mx-1 text-[#b3b3b3]">·</span>
            <span className="text-[#b3b3b3]">{positive}% 긍정 · {negative}% 부정</span>
            <span className="mx-1 text-[#b3b3b3]">·</span>
            <span className="text-[#b3b3b3]">
              {summary.total_movies}개 영화
            </span>
            <span className="mx-1 text-[#b3b3b3]">·</span>
            <span className="text-[#b3b3b3]">
              {summary.total_reviews.toLocaleString()}개 리뷰
            </span>
            <span className="mx-1 text-[#b3b3b3]">,</span>
            <span className="text-[#b3b3b3]">
              평균 {summary.avg_processing_seconds.toFixed(1)}초
            </span>
          </div>
        </div>
      </div>

      {/* action row */}
      <div className="flex items-center gap-4 px-8 pb-6">
        <button
          type="button"
          aria-label="Play featured analysis"
          className="flex h-14 w-14 items-center justify-center rounded-full text-black transition-transform hover:scale-105"
          style={{
            background: "#1ed760",
            boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
          }}
        >
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className="h-6 w-6">
            <path d="M7.05 3.606l13.49 7.788a.7.7 0 010 1.212L7.05 20.394A.7.7 0 016 19.788V4.212a.7.7 0 011.05-.606z" />
          </svg>
        </button>

        <button
          type="button"
          aria-label="Follow"
          className="flex h-8 w-8 items-center justify-center rounded-full border border-[#7c7c7c] text-[#b3b3b3] hover:scale-105 hover:text-white"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M1.75 7.5a6.25 6.25 0 1112.5 0v.5h-1.5v-.5a4.75 4.75 0 10-9.5 0v.5h-1.5v-.5z" />
            <path d="M6 9.25a2 2 0 114 0v3.25a2 2 0 11-4 0V9.25z" />
          </svg>
        </button>

        <button
          type="button"
          aria-label="More"
          className="flex h-8 w-8 items-center justify-center text-[#b3b3b3] hover:text-white"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-5 w-5">
            <path d="M3 8a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM9.5 8a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM14.5 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
          </svg>
        </button>

        <div className="ml-auto flex items-center gap-3 text-[#b3b3b3]">
          <span className="text-[14px]">List</span>
          <button
            type="button"
            aria-label="View as list"
            className="flex h-8 w-8 items-center justify-center hover:text-white"
          >
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M15 14.25H1a.75.75 0 010-1.5h14a.75.75 0 010 1.5zM15 8.75H1a.75.75 0 010-1.5h14a.75.75 0 010 1.5zM15 3.25H1a.75.75 0 010-1.5h14a.75.75 0 010 1.5z" />
            </svg>
          </button>
        </div>
      </div>

      <p className="px-8 pb-3 text-[12px] text-[#b3b3b3]">
        현재 라이브 분석:{" "}
        <span className="text-white" style={{ fontWeight: 700 }}>
          {featured.movie_title}
        </span>{" "}
        · {featured.review_count.toLocaleString()}개 리뷰
      </p>
    </section>
  );
}
