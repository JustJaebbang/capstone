import Link from "next/link";
import {
  Archivo_Black,
  JetBrains_Mono,
  Black_Han_Sans,
  IBM_Plex_Sans_KR,
} from "next/font/google";

import dashboardMoviesJson from "@/lib/mock/dashboard-movies.json";
import dashboardSummaryJson from "@/lib/mock/dashboard-summary.json";
import type {
  DashboardMoviesResponse,
  DashboardSummary,
} from "@/lib/types";

import BrutalStatBlock from "@/components/style-experiments/brutalist/BrutalStatBlock";
import BrutalSentimentBar from "@/components/style-experiments/brutalist/BrutalSentimentBar";
import BrutalKeywordList from "@/components/style-experiments/brutalist/BrutalKeywordList";
import BrutalActivityLog from "@/components/style-experiments/brutalist/BrutalActivityLog";
import BrutalMovieBlock from "@/components/style-experiments/brutalist/BrutalMovieBlock";
import BrutalMarquee from "@/components/style-experiments/brutalist/BrutalMarquee";

const display = Archivo_Black({
  subsets: ["latin"],
  weight: "400",
  variable: "--brutal-display",
  display: "swap",
});
const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--brutal-mono",
  display: "swap",
});
const displayKR = Black_Han_Sans({
  subsets: ["latin"],
  weight: "400",
  variable: "--brutal-display-kr",
  display: "swap",
});
const bodyKR = IBM_Plex_Sans_KR({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--brutal-body-kr",
  display: "swap",
});

const summary = dashboardSummaryJson as unknown as DashboardSummary;
const movies = (dashboardMoviesJson as unknown as DashboardMoviesResponse).items;

function stampNow(iso: string): string {
  const d = new Date(iso);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${yyyy}.${mm}.${dd} ${hh}:${mi}`;
}

const marqueeItems = [
  ...movies.map((m) => `▸ ${m.movie_title}`),
  "▸ OPINION CLUSTERING / HDBSCAN",
  "▸ DAILY BATCH PIPELINE",
  "▸ B = ORCHESTRATOR · C = LLM · D = CLUSTER",
  "▸ DO NOT MODIFY API SCHEMAS",
];

const fontStack = `${display.variable} ${mono.variable} ${displayKR.variable} ${bodyKR.variable}`;

export default function BrutalistDashboardPage() {
  const totalKeywordsAcrossMovies = movies.reduce(
    (sum, m) => sum + m.top_keywords.reduce((s, k) => s + k.count, 0),
    0,
  );

  return (
    <main
      className={`${fontStack} relative min-h-screen overflow-hidden bg-[#ece6d6] text-[#0a0a0a]`}
    >
      {/* page-scoped CSS (fonts, marquee keyframes, noise grain) */}
      <style>{`
        main { font-family: var(--brutal-body-kr), system-ui, sans-serif; }
        .font-display    { font-family: var(--brutal-display), Impact, sans-serif; }
        .font-display-kr { font-family: var(--brutal-display-kr), var(--brutal-display), Impact, sans-serif; }
        .font-mono       { font-family: var(--brutal-mono), ui-monospace, monospace; }
        .font-body-kr    { font-family: var(--brutal-body-kr), system-ui, sans-serif; }

        @keyframes brutal-marquee {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }
        @keyframes brutal-blink {
          0%, 60% { opacity: 1; } 61%, 100% { opacity: 0; }
        }
        .brutal-blink { animation: brutal-blink 1.1s steps(2, end) infinite; }

        /* Cream paper noise — built from layered SVGs, no asset needed */
        .brutal-paper {
          background-image:
            radial-gradient(rgba(10,10,10,0.07) 1px, transparent 1px),
            radial-gradient(rgba(10,10,10,0.05) 1px, transparent 1px);
          background-size: 14px 14px, 22px 22px;
          background-position: 0 0, 7px 11px;
        }
      `}</style>

      {/* ═══════════ SYSTEM BAR ═══════════ */}
      <div className="border-b-[3px] border-[#0a0a0a] bg-[#0a0a0a] text-[#ece6d6]">
        <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-x-6 gap-y-1 px-6 py-2 font-mono text-[11px] tracking-[0.22em] uppercase">
          <span className="flex items-center gap-2">
            <span className="brutal-blink inline-block h-2 w-2 bg-[#FFE600]" />
            REVIEW.OS // v0.1.brutal
          </span>
          <span className="flex flex-1 items-center gap-6 text-[#ece6d6]/70">
            <span>FEED ▸ POSTGRES</span>
            <span>MODE ▸ DAILY-BATCH</span>
            <span>NODE ▸ B-ORCHESTRATOR</span>
          </span>
          <span className="flex items-center gap-2 text-[#FFE600]">
            STAMP ▸ {stampNow(summary.updated_at)}
          </span>
        </div>
      </div>

      <BrutalMarquee items={marqueeItems} />

      {/* ═══════════ HERO ═══════════ */}
      <section className="relative border-b-[3px] border-[#0a0a0a] brutal-paper">
        <div className="mx-auto grid max-w-[1440px] grid-cols-1 gap-6 px-6 py-12 md:grid-cols-[1.4fr_1fr]">
          {/* left — title */}
          <div className="relative">
            <p className="flex items-center gap-3 font-mono text-[11px] tracking-[0.28em] uppercase">
              <span className="border-2 border-[#0a0a0a] bg-[#FFE600] px-2 py-0.5">
                FILE / 001
              </span>
              <span>MOVIE-REVIEW · OPINION CLUSTER REPORT</span>
            </p>

            <h1
              className="font-display-kr mt-5 text-[#0a0a0a]"
              style={{
                fontSize: "clamp(56px, 9vw, 132px)",
                lineHeight: 0.85,
                letterSpacing: "-0.02em",
              }}
            >
              영화 리뷰<br />
              <span className="inline-block bg-[#0a0a0a] px-3 text-[#FFE600]">
                해부 보고서
              </span>
            </h1>

            <p className="mt-6 max-w-xl font-body-kr text-[15px] leading-relaxed text-[#0a0a0a]/85">
              관객의 말, 그대로 절단. LLM이 문장을 뜯어 의견 조각으로 만들고,
              HDBSCAN이 비슷한 조각을 한 무더기에 쌓는다. 그 결과만 여기에 인쇄됨.
              <span className="ml-2 border-b-2 border-[#0a0a0a] font-display text-sm tracking-widest uppercase">
                RAW / UNFILTERED
              </span>
            </p>

            {/* meta */}
            <div className="mt-8 grid max-w-xl grid-cols-3 gap-3 font-mono text-[10px] tracking-[0.2em] uppercase">
              <div className="border-2 border-[#0a0a0a] bg-white px-3 py-2">
                <div className="text-[#0a0a0a]/60">PIPELINE</div>
                <div className="mt-1 font-display text-base tracking-wider">
                  B → C → D
                </div>
              </div>
              <div className="border-2 border-[#0a0a0a] bg-white px-3 py-2">
                <div className="text-[#0a0a0a]/60">SOURCE</div>
                <div className="mt-1 font-display text-base tracking-wider">
                  NAVER · KOFIC
                </div>
              </div>
              <div className="border-2 border-[#0a0a0a] bg-[#FFE600] px-3 py-2">
                <div className="text-[#0a0a0a]/70">LATENCY</div>
                <div className="mt-1 font-display text-base tracking-wider">
                  {summary.avg_processing_seconds.toFixed(1)}s avg
                </div>
              </div>
            </div>
          </div>

          {/* right — massive stamp + nav */}
          <div className="relative flex flex-col items-end justify-between gap-6">
            {/* huge number stamp */}
            <div className="relative">
              <div
                className="relative border-[4px] border-[#0a0a0a] bg-white px-6 py-3"
                style={{
                  boxShadow: "12px 12px 0 0 #FFE600, 12px 12px 0 4px #0a0a0a",
                  transform: "rotate(-4deg)",
                }}
              >
                <div className="font-mono text-[10px] tracking-[0.3em] uppercase">
                  ANALYSED · TOTAL
                </div>
                <div
                  className="font-display leading-none"
                  style={{ fontSize: "clamp(120px, 16vw, 220px)" }}
                >
                  {String(summary.total_movies).padStart(2, "0")}
                </div>
                <div className="font-mono text-[10px] tracking-[0.3em] uppercase">
                  / FILMS
                </div>
              </div>
            </div>

            <div className="flex flex-col items-end gap-2">
              <Link
                href="/movies"
                className="group inline-flex items-center gap-2 border-[3px] border-[#0a0a0a] bg-white px-4 py-2 font-display text-sm tracking-widest uppercase transition-transform hover:-translate-x-1 hover:-translate-y-1"
                style={{ boxShadow: "6px 6px 0 0 #0a0a0a" }}
              >
                ◀ BACK · /movies
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-2 font-mono text-[10px] tracking-[0.22em] uppercase underline-offset-4 hover:underline"
              >
                home ↗
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ KPI ROW ═══════════ */}
      <section className="border-b-[3px] border-[#0a0a0a]">
        <div className="mx-auto grid max-w-[1440px] grid-cols-2 gap-5 px-6 py-10 md:grid-cols-4">
          <BrutalStatBlock
            index="01"
            label="TOTAL FILMS"
            value={String(summary.total_movies).padStart(2, "0")}
            unit="FILMS"
            caption={
              <span>
                ACTIVE ▸{" "}
                <strong className="text-[#0a0a0a]">
                  {movies.filter((m) => m.is_active).length}
                </strong>{" "}
                / DORMANT ▸{" "}
                {summary.total_movies - movies.filter((m) => m.is_active).length}
              </span>
            }
            accent="white"
          />
          <BrutalStatBlock
            index="02"
            label="COMPLETED RUNS"
            value={String(summary.completed_movies).padStart(2, "0")}
            unit="JOBS"
            caption={<span>STATUS ▸ ALL GREEN · BATCH STABLE</span>}
            accent="yellow"
          />
          <BrutalStatBlock
            index="03"
            label="REVIEWS PROCESSED"
            value={summary.total_reviews.toLocaleString()}
            unit="ROWS"
            caption={
              <span>
                LLM PHRASES ▸ {totalKeywordsAcrossMovies.toLocaleString()}+ EXTRACTED
              </span>
            }
            accent="white"
          />
          <BrutalStatBlock
            index="04"
            label="AVG LATENCY"
            value={summary.avg_processing_seconds.toFixed(1)}
            unit="SEC/JOB"
            caption={<span>SLA ▸ DAILY · NEXT WINDOW 03:00 KST</span>}
            accent="ink"
          />
        </div>
      </section>

      {/* ═══════════ SENTIMENT WIDE BAR ═══════════ */}
      <section className="border-b-[3px] border-[#0a0a0a] brutal-paper">
        <div className="mx-auto max-w-[1440px] px-6 py-12">
          <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="font-mono text-[11px] tracking-[0.28em] uppercase">
                §02 — OVERALL VOICE
              </p>
              <h2
                className="font-display-kr mt-1 leading-[0.9]"
                style={{ fontSize: "clamp(36px, 5vw, 64px)" }}
              >
                전체 감성, 한 줄로 절단.
              </h2>
            </div>
            <div className="font-mono text-[11px] tracking-[0.22em] uppercase text-[#0a0a0a]/70">
              SOURCE ▸ ALL FILMS · ALL REVIEWS
            </div>
          </header>

          <BrutalSentimentBar
            positivePercent={summary.overall_sentiment.positive_percent}
            negativePercent={summary.overall_sentiment.negative_percent}
            totalReviews={summary.total_reviews}
            title="OVERALL · 전체 감성"
          />
        </div>
      </section>

      {/* ═══════════ MOVIE INVENTORY ═══════════ */}
      <section className="border-b-[3px] border-[#0a0a0a]">
        <div className="mx-auto max-w-[1440px] px-6 py-12">
          <header className="mb-8 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="font-mono text-[11px] tracking-[0.28em] uppercase">
                §03 — INVENTORY · {String(movies.length).padStart(2, "0")} ROWS
              </p>
              <h2
                className="font-display-kr mt-1 leading-[0.9]"
                style={{ fontSize: "clamp(36px, 5vw, 64px)" }}
              >
                필름 단위 해부 결과
              </h2>
            </div>
            <div className="flex items-center gap-2 font-mono text-[10px] tracking-[0.22em] uppercase">
              <span className="border-2 border-[#0a0a0a] bg-white px-2 py-1">
                SORT ▸ RECENT
              </span>
              <span className="border-2 border-[#0a0a0a] bg-[#FFE600] px-2 py-1">
                VIEW ▸ STACKED
              </span>
            </div>
          </header>

          <div className="flex flex-col gap-10">
            {movies.map((movie, i) => (
              <BrutalMovieBlock key={movie.movie_id} movie={movie} index={i} />
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ INTEL PANEL: keywords + activity ═══════════ */}
      <section className="border-b-[3px] border-[#0a0a0a] brutal-paper">
        <div className="mx-auto max-w-[1440px] px-6 py-12">
          <header className="mb-8 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="font-mono text-[11px] tracking-[0.28em] uppercase">
                §04 — INTEL PANEL
              </p>
              <h2
                className="font-display-kr mt-1 leading-[0.9]"
                style={{ fontSize: "clamp(36px, 5vw, 64px)" }}
              >
                관객이 가장 많이 한 말
              </h2>
            </div>
            <span className="font-mono text-[10px] tracking-[0.22em] uppercase text-[#0a0a0a]/70">
              UPDATED ▸ {stampNow(summary.updated_at)}
            </span>
          </header>

          <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1.05fr_1fr]">
            <BrutalKeywordList
              title="TOP KEYWORDS · OVERALL"
              keywords={summary.top_keywords_overall}
            />
            <BrutalActivityLog activities={summary.recent_activities} />
          </div>
        </div>
      </section>

      {/* ═══════════ COLOPHON / FOOTER ═══════════ */}
      <footer className="bg-[#0a0a0a] text-[#ece6d6]">
        <div className="mx-auto grid max-w-[1440px] grid-cols-1 gap-8 px-6 py-10 md:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <p className="font-mono text-[11px] tracking-[0.3em] uppercase text-[#FFE600]">
              COLOPHON
            </p>
            <p
              className="font-display-kr mt-3 leading-[0.95]"
              style={{ fontSize: "clamp(28px, 3.5vw, 44px)" }}
            >
              영화 리뷰<br />구조화 시스템
            </p>
            <p className="mt-4 max-w-md font-body-kr text-sm leading-relaxed text-[#ece6d6]/75">
              브루탈리스트 스타일 실험판. 같은 데이터, 다른 시선.
              메인 대시보드와 모듈 경계는 그대로 유지됨.
            </p>
          </div>

          <div>
            <p className="font-mono text-[10px] tracking-[0.3em] uppercase text-[#ece6d6]/60">
              STACK
            </p>
            <ul className="mt-3 space-y-1 font-mono text-[12px] tracking-wider">
              <li>▸ Next 16 · React 19</li>
              <li>▸ Tailwind 4</li>
              <li>▸ FastAPI · Postgres</li>
              <li>▸ HDBSCAN + miniLM</li>
            </ul>
          </div>

          <div>
            <p className="font-mono text-[10px] tracking-[0.3em] uppercase text-[#ece6d6]/60">
              SIGNATURE
            </p>
            <pre className="mt-3 font-mono text-[11px] leading-snug text-[#FFE600]">{`╔══════════════════╗
║  REVIEW.OS · 001 ║
║   BRUTAL.EDIT    ║
╚══════════════════╝`}</pre>
          </div>
        </div>

        <div className="border-t-2 border-[#FFE600]/30">
          <div className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-3 px-6 py-3 font-mono text-[10px] tracking-[0.25em] uppercase text-[#ece6d6]/60">
            <span>END OF DOCUMENT // {stampNow(summary.updated_at)}</span>
            <span>PRINTED IN BLACK + YELLOW · NO COMPROMISE</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
