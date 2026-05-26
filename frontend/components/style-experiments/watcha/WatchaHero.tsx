import type { DashboardMovie, DashboardSummary } from "@/lib/types";
import WatchaSentimentRing from "./WatchaSentimentRing";

type Props = {
  feature: DashboardMovie;
  summary: DashboardSummary;
};

export default function WatchaHero({ feature, summary }: Props) {
  const d = new Date(summary.updated_at);
  const dateLabel = `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
  const topKeyword = feature.top_keywords[0];

  return (
    <section className="border-b border-[#e8e3d6]">
      <div className="mx-auto grid max-w-[1240px] grid-cols-1 gap-14 px-8 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:gap-20 lg:py-28">
        {/* Left column — editorial copy */}
        <div className="flex flex-col">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
            이슈 No.07 · {dateLabel}
          </p>

          <h1 className="mt-7 font-serif text-[58px] font-normal leading-[1.02] tracking-[-0.028em] text-[#161616] sm:text-[72px] lg:text-[88px]">
            관객의 마음을,
            <br />
            <span className="italic text-[#ff2c63]">숫자</span>로 듣다.
          </h1>

          <p className="mt-7 max-w-[470px] text-[16px] leading-[1.75] text-[#3d3a35]">
            평점은 한 자리 숫자에 모든 것을 욱여넣지만,
            우리는 의견을 펼쳐 봅니다. LLM이 리뷰 문장에서 의견 조각을
            골라내고, 군집 엔진이 비슷한 목소리를 한 무리로 묶습니다.
          </p>

          {/* stat strip */}
          <dl className="mt-auto grid grid-cols-3 gap-6 border-t border-[#e8e3d6] pt-8 sm:gap-10">
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                분석 작품
              </dt>
              <dd className="mt-2 flex items-baseline gap-1 font-serif text-[34px] tracking-[-0.02em] text-[#161616] tabular-nums">
                {summary.total_movies}
                <span className="text-[13px] font-normal tracking-tight text-[#6b6760]">
                  편
                </span>
              </dd>
            </div>
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                수집 리뷰
              </dt>
              <dd className="mt-2 flex items-baseline gap-1 font-serif text-[34px] tracking-[-0.02em] text-[#161616] tabular-nums">
                {summary.total_reviews.toLocaleString()}
                <span className="text-[13px] font-normal tracking-tight text-[#6b6760]">
                  개
                </span>
              </dd>
            </div>
            <div>
              <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                평균 호감
              </dt>
              <dd className="mt-2 flex items-baseline gap-1 font-serif text-[34px] tracking-[-0.02em] text-[#ff2c63] tabular-nums">
                {summary.overall_sentiment.positive_percent}
                <span className="text-[13px] font-normal tracking-tight text-[#ff2c63]/70">
                  %
                </span>
              </dd>
            </div>
          </dl>
        </div>

        {/* Right column — feature poster + ring overlay */}
        <div className="relative">
          {/* oversized decorative numeral */}
          <span
            aria-hidden
            className="pointer-events-none absolute -left-4 -top-12 hidden select-none font-serif text-[200px] italic leading-none text-[#efe9d8] lg:block"
          >
            #1
          </span>

          <div
            className="relative aspect-[3/4] w-full overflow-hidden rounded-[10px] shadow-[0_28px_60px_-22px_rgba(20,15,5,0.4)]"
            style={{
              background:
                "radial-gradient(120% 80% at 20% 0%, #2a1424 0%, #4a1f3f 45%, #0d0509 100%)",
            }}
          >
            {/* faux grain */}
            <div
              aria-hidden
              className="pointer-events-none absolute inset-0 opacity-[0.18] mix-blend-overlay"
              style={{
                backgroundImage:
                  "radial-gradient(rgba(255,255,255,0.6) 1px, transparent 1px)",
                backgroundSize: "3px 3px",
              }}
            />

            <div className="absolute inset-0 flex flex-col justify-between p-10">
              <div className="flex items-start justify-between">
                <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-white/55">
                  이 주의 작품
                </p>
                <span className="rounded-full bg-white/10 px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-white/80 backdrop-blur">
                  {feature.source}
                </span>
              </div>

              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-white/55">
                  {feature.release_date} · {feature.genres.join(" · ")}
                </p>
                <h2 className="mt-3 font-serif text-[56px] font-medium leading-[1.02] tracking-[-0.025em] text-white sm:text-[64px]">
                  {feature.movie_title}
                </h2>
                {topKeyword && (
                  <p className="mt-4 max-w-[300px] font-serif text-[15px] italic leading-snug text-white/65">
                    &ldquo;{topKeyword.label}&rdquo;에 대한 이야기가
                    가장 많았습니다.
                  </p>
                )}
              </div>
            </div>

            {/* Sentiment ring overlay — Watcha "score" stand-in */}
            <div className="absolute -bottom-10 -right-8 hidden rounded-full bg-[#fbf9f3] p-3 shadow-[0_14px_30px_-10px_rgba(20,15,5,0.45)] md:block">
              <WatchaSentimentRing
                positivePercent={feature.sentiment.positive_percent}
                size={170}
                thickness={5}
              />
            </div>
          </div>

          {/* Below-poster meta */}
          <div className="mt-6 flex items-center justify-between border-t border-[#e8e3d6] pt-5">
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
              리뷰 {feature.review_count.toLocaleString()} · job{" "}
              {feature.latest_job_id ?? "—"}
            </p>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
              호감 {feature.sentiment.positive_percent}% · 불호{" "}
              {feature.sentiment.negative_percent}%
            </p>
          </div>

          {/* Mobile ring */}
          <div className="mt-8 flex justify-center md:hidden">
            <WatchaSentimentRing
              positivePercent={feature.sentiment.positive_percent}
              size={150}
              thickness={5}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
