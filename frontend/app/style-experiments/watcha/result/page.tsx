import Link from "next/link";

import WatchaFontStyles from "@/components/style-experiments/watcha/WatchaFontStyles";
import WatchaSentimentRing from "@/components/style-experiments/watcha/WatchaSentimentRing";
import WatchaResultBody from "@/components/style-experiments/watcha/WatchaResultBody";
import WatchaFooter from "@/components/style-experiments/watcha/WatchaFooter";
import { WATCHA_RESULT_MOCK } from "@/components/style-experiments/watcha/watcha-result-mock";

function posterGradient(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  const palettes: Array<[string, string, string]> = [
    ["#1a1424", "#3b1a3f", "#0d0810"],
    ["#0e1f1c", "#1e3f3a", "#070f0d"],
    ["#2a1a14", "#5a2a1a", "#180a05"],
    ["#0d172a", "#1e2a4a", "#05080f"],
  ];
  const [a, b, c] = palettes[h % palettes.length];
  return `radial-gradient(120% 80% at 20% 0%, ${a} 0%, ${b} 55%, ${c} 100%)`;
}

function formatCompleted(iso: string): string {
  const d = new Date(iso);
  const yy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${yy}.${mm}.${dd} · ${hh}:${mi}`;
}

export default function WatchaResultPage() {
  const { movie, sentiment, opinion_groups, reviews_by_cluster } =
    WATCHA_RESULT_MOCK;

  return (
    <main className="min-h-screen bg-[#fbf9f3] text-[#161616] antialiased selection:bg-[#ff2c63]/85 selection:text-white">
      <WatchaFontStyles />

      <div className="watcha-page">
        {/* ── Nav ─────────────────────────────────────── */}
        <header className="sticky top-0 z-30 border-b border-[#e8e3d6] bg-[#fbf9f3]/85 backdrop-blur">
          <div className="mx-auto flex max-w-[1240px] items-center justify-between px-8 py-5">
            <Link
              href="/style-experiments/watcha"
              className="flex items-baseline gap-1"
            >
              <span className="font-serif text-[26px] font-medium tracking-[-0.02em] text-[#161616]">
                review
              </span>
              <span className="font-serif text-[26px] italic font-medium text-[#ff2c63]">
                pedia
              </span>
              <span className="ml-2 hidden font-mono text-[10px] uppercase tracking-[0.24em] text-[#9a958b] sm:inline">
                / analysis
              </span>
            </Link>
            <div className="flex items-center gap-3">
              <span className="hidden font-mono text-[11px] uppercase tracking-[0.18em] text-[#9a958b] md:inline">
                {movie.job_id} · {formatCompleted(movie.completed_at)}
              </span>
              <Link
                href="/style-experiments/watcha"
                className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760] hover:bg-[#f0ece0]"
              >
                ← 대시보드
              </Link>
            </div>
          </div>
        </header>

        {/* ── Hero ────────────────────────────────────── */}
        <section className="border-b border-[#e8e3d6]">
          <div className="mx-auto max-w-[1240px] px-8 py-16 lg:py-24">
            <Link
              href="/style-experiments/watcha"
              className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#6b6760] hover:text-[#ff2c63]"
            >
              ← collection
            </Link>

            <div className="mt-10 grid grid-cols-1 gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:gap-20">
              {/* Poster */}
              <div className="relative">
                <span
                  aria-hidden
                  className="pointer-events-none absolute -left-4 -top-12 hidden select-none font-serif text-[180px] italic leading-none text-[#efe9d8] lg:block"
                >
                  #1
                </span>
                <div
                  className="relative aspect-[3/4] w-full overflow-hidden rounded-[10px] shadow-[0_28px_60px_-22px_rgba(20,15,5,0.4)]"
                  style={{ background: posterGradient(movie.poster_seed) }}
                >
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
                        분석 결과 · vol.07
                      </p>
                      <span className="rounded-full bg-white/10 px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-white/80 backdrop-blur">
                        {movie.source}
                      </span>
                    </div>
                    <div>
                      <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-white/55">
                        {movie.release_date} · {movie.genres.join(" · ")}
                      </p>
                      <h2 className="mt-3 font-serif text-[56px] font-medium leading-[1.02] tracking-[-0.025em] text-white sm:text-[64px]">
                        {movie.title}
                      </h2>
                    </div>
                  </div>
                  {/* completed band */}
                  <div className="pointer-events-none absolute inset-x-0 bottom-0 h-[3px] bg-[#27ae60]" />
                </div>
              </div>

              {/* Meta */}
              <div className="flex flex-col">
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  Issue No.07 · 분석 완료
                </p>
                <h1 className="mt-5 font-serif text-[58px] font-normal leading-[1.02] tracking-[-0.028em] text-[#161616] sm:text-[72px] lg:text-[84px]">
                  관객은 <span className="italic text-[#ff2c63]">호감</span>으로
                  <br />
                  답했습니다.
                </h1>
                <p className="mt-6 max-w-[480px] text-[16px] leading-[1.75] text-[#3d3a35]">
                  총 {sentiment.total_review_count.toLocaleString()}건의 리뷰가
                  {" "}
                  {opinion_groups.length}개 의견 군집으로 묶였습니다. 가장 큰
                  목소리는{" "}
                  <em className="not-italic font-medium text-[#161616]">
                    &ldquo;{opinion_groups[0]?.label}&rdquo;
                  </em>
                  였습니다.
                </p>

                <div className="mt-10 flex items-center gap-10">
                  <WatchaSentimentRing
                    positivePercent={sentiment.positive_percent}
                    size={180}
                    thickness={6}
                  />
                  <div className="flex flex-col gap-3">
                    <div>
                      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                        positive
                      </p>
                      <p className="mt-1 flex items-baseline gap-1 font-serif text-[26px] leading-none text-[#ff2c63] tabular-nums">
                        {sentiment.positive_percent}%
                        <span className="text-[12px] font-normal text-[#9a958b]">
                          · {sentiment.positive_review_count.toLocaleString()}건
                        </span>
                      </p>
                    </div>
                    <div>
                      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                        negative
                      </p>
                      <p className="mt-1 flex items-baseline gap-1 font-serif text-[26px] leading-none text-[#0f4c5c] tabular-nums">
                        {sentiment.negative_percent}%
                        <span className="text-[12px] font-normal text-[#9a958b]">
                          · {sentiment.negative_review_count.toLocaleString()}건
                        </span>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Stat strip */}
                <dl className="mt-12 grid grid-cols-3 gap-6 border-t border-[#e8e3d6] pt-8 sm:gap-10">
                  <div>
                    <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                      총 리뷰
                    </dt>
                    <dd className="mt-2 font-serif text-[32px] leading-none text-[#161616] tabular-nums">
                      {sentiment.total_review_count.toLocaleString()}
                      <span className="ml-1 text-[13px] font-normal text-[#6b6760]">
                        건
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                      의견 군집
                    </dt>
                    <dd className="mt-2 font-serif text-[32px] leading-none text-[#161616] tabular-nums">
                      {opinion_groups.length}
                      <span className="ml-1 text-[13px] font-normal text-[#6b6760]">
                        groups
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                      대표 의견
                    </dt>
                    <dd className="mt-2 font-serif text-[22px] leading-tight tracking-[-0.01em] text-[#161616]">
                      {opinion_groups[0]?.label ?? "—"}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </section>

        {/* ── Sentiment narrative ────────────────────── */}
        <section className="border-b border-[#e8e3d6] bg-[#f5f1e6]">
          <div className="mx-auto max-w-[1240px] px-8 py-20">
            <div className="grid grid-cols-1 gap-10 lg:grid-cols-[0.7fr_1.3fr] lg:gap-16">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  Editor&apos;s note · 01
                </p>
                <h2 className="mt-4 font-serif text-[36px] leading-[1.1] tracking-[-0.02em] text-[#161616] sm:text-[44px]">
                  호감과 불호의 <span className="italic">사이</span>
                </h2>
              </div>
              <div>
                {/* wide sentiment bar */}
                <div className="flex h-10 w-full overflow-hidden rounded-full">
                  <div
                    className="flex items-center justify-end pr-4 text-white"
                    style={{
                      width: `${sentiment.positive_percent}%`,
                      background: "#ff2c63",
                    }}
                  >
                    <span className="font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                      긍정 {sentiment.positive_percent}%
                    </span>
                  </div>
                  <div
                    className="flex items-center justify-start pl-4 text-white"
                    style={{
                      width: `${sentiment.negative_percent}%`,
                      background: "#0f4c5c",
                    }}
                  >
                    <span className="font-mono text-[11px] font-medium uppercase tracking-[0.18em]">
                      부정 {sentiment.negative_percent}%
                    </span>
                  </div>
                </div>

                <p className="mt-6 font-serif text-[18px] leading-[1.7] tracking-[-0.005em] text-[#3d3a35]">
                  관객의 {sentiment.positive_percent}%가 호감을, {sentiment.negative_percent}%가 불호를
                  남겼습니다. 비율 자체보다 중요한 것은{" "}
                  <em className="not-italic font-medium text-[#161616]">
                    어떤 이야기가 호감을, 어떤 이야기가 불호를 만들었는지
                  </em>
                  입니다. 아래의 의견 군집이 그 결을 보여줍니다.
                </p>

                <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 font-mono text-[11px] uppercase tracking-[0.18em] text-[#6b6760]">
                  <span>
                    positive · {sentiment.positive_review_count.toLocaleString()}건
                  </span>
                  <span className="text-[#dcd6c5]">·</span>
                  <span>
                    negative · {sentiment.negative_review_count.toLocaleString()}건
                  </span>
                  <span className="text-[#dcd6c5]">·</span>
                  <span>total · {sentiment.total_review_count.toLocaleString()}건</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Interactive opinion-group body ─────────── */}
        <WatchaResultBody
          groups={opinion_groups}
          reviewsByCluster={reviews_by_cluster}
        />

        <WatchaFooter updatedAt={movie.completed_at} />
      </div>
    </main>
  );
}
