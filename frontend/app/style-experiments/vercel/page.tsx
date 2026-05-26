import Link from "next/link";

import dashboardMoviesJson from "@/lib/mock/dashboard-movies.json";
import dashboardSummaryJson from "@/lib/mock/dashboard-summary.json";
import type {
  DashboardMoviesResponse,
  DashboardSummary,
} from "@/lib/types";

import VercelNav from "@/components/style-experiments/vercel/VercelNav";
import VercelMeshHero from "@/components/style-experiments/vercel/VercelMeshHero";
import VercelStatCard from "@/components/style-experiments/vercel/VercelStatCard";
import VercelSentimentMeter from "@/components/style-experiments/vercel/VercelSentimentMeter";
import VercelMovieCard from "@/components/style-experiments/vercel/VercelMovieCard";
import VercelKeywordTable from "@/components/style-experiments/vercel/VercelKeywordTable";
import VercelDeploymentLog from "@/components/style-experiments/vercel/VercelDeploymentLog";

const summary = dashboardSummaryJson as unknown as DashboardSummary;
const movies = (dashboardMoviesJson as unknown as DashboardMoviesResponse)
  .items;

function formatStamp(iso: string): string {
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${mm}-${dd} ${hh}:${mi}`;
}

function shortStamp(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate(),
  ).padStart(2, "0")}`;
}

// Tiny inline sparkline — purely decorative, deterministic per seed
function Sparkline({
  seed,
  color = "#50e3c2",
}: {
  seed: number;
  color?: string;
}) {
  const pts: [number, number][] = Array.from({ length: 16 }).map((_, i) => {
    const x = (i / 15) * 100;
    // pseudo-random but deterministic
    const v =
      0.5 +
      0.4 *
        Math.sin(seed * 0.7 + i * 0.9) *
        Math.cos(seed * 0.3 + i * 0.4);
    const y = 30 - v * 24;
    return [x, y];
  });
  const path =
    "M " +
    pts.map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(" L ");
  return (
    <svg
      viewBox="0 0 100 36"
      preserveAspectRatio="none"
      className="h-10 w-full"
      aria-hidden
    >
      <defs>
        <linearGradient id={`spark-${seed}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.35} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      <path
        d={`${path} L 100 36 L 0 36 Z`}
        fill={`url(#spark-${seed})`}
      />
      <path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth={1.25}
        strokeLinecap="round"
      />
    </svg>
  );
}

export default function VercelDashboardPage() {
  const totalReviewsAcross = movies.reduce(
    (s, m) => s + m.review_count,
    0,
  );
  const avgPositive = Math.round(
    movies.reduce((s, m) => s + m.sentiment.positive_percent, 0) /
      Math.max(1, movies.length),
  );

  return (
    <main className="min-h-screen bg-[#0a0a0a] text-[#ededed] antialiased selection:bg-white selection:text-black">
      {/* token primitives, scoped to this page */}
      <style>{`
        .vercel-page {
          font-family: var(--font-geist-sans), 'SF Pro Text', 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif;
          font-feature-settings: "ss01", "ss02", "cv11";
        }
        .vercel-page p, .vercel-page li, .vercel-page span, .vercel-page h1,
        .vercel-page h2, .vercel-page h3, .vercel-page button, .vercel-page a {
          font-family: inherit;
        }
      `}</style>

      <div className="vercel-page">
        <VercelNav stamp={formatStamp(summary.updated_at)} />

        {/* ── Hero ─────────────────────────────────────── */}
        <VercelMeshHero
          eyebrow="DAILY BATCH · v0.1.0 · STABLE"
          headline="관객의 의견, 매일 자동으로."
          body="LLM이 리뷰 문장에서 의견 조각을 추출하고, HDBSCAN이 비슷한 조각을 한 무더기로 묶습니다. 결과는 매일 한 번 갱신됩니다."
          ctaPrimary={{ label: "View dashboard", href: "/movies" }}
          ctaSecondary={{ label: "Documentation", href: "#docs" }}
          lastBatchLabel={formatStamp(summary.updated_at)}
        />

        {/* ── Stat ribbon ──────────────────────────────── */}
        <section className="mx-auto max-w-[1400px] px-6 py-12">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <span
                className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#666]"
                style={{
                  fontFamily: "var(--font-geist-mono), monospace",
                }}
              >
                overview
              </span>
              <h2
                className="mt-2 text-white"
                style={{
                  fontSize: "32px",
                  fontWeight: 600,
                  lineHeight: "40px",
                  letterSpacing: "-0.04em",
                }}
              >
                Pipeline at a glance.
              </h2>
            </div>
            <Link
              href="/movies"
              className="text-[13px] font-medium tracking-[-0.01em] text-[#0070f3] hover:underline"
            >
              Open full dashboard →
            </Link>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <VercelStatCard
              label="total films"
              value={String(summary.total_movies).padStart(2, "0")}
              unit="films"
              delta={{ tone: "neutral", text: "stable" }}
              spark={<Sparkline seed={1} color="#0070f3" />}
            />
            <VercelStatCard
              label="completed runs"
              value={String(summary.completed_movies).padStart(2, "0")}
              unit={`/ ${summary.total_movies}`}
              delta={{ tone: "up", text: "100% pass" }}
              spark={<Sparkline seed={2} color="#50e3c2" />}
            />
            <VercelStatCard
              label="reviews processed"
              value={summary.total_reviews.toLocaleString()}
              unit="rows"
              delta={{ tone: "up", text: "+12.4%" }}
              spark={<Sparkline seed={3} color="#7928ca" />}
            />
            <VercelStatCard
              label="avg latency"
              value={summary.avg_processing_seconds.toFixed(1)}
              unit="s / job"
              delta={{ tone: "down", text: "-0.4s" }}
              spark={<Sparkline seed={4} color="#f9cb28" />}
            />
          </div>
        </section>

        {/* ── Sentiment ────────────────────────────────── */}
        <section className="mx-auto max-w-[1400px] px-6 py-12">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <span
                className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#666]"
                style={{
                  fontFamily: "var(--font-geist-mono), monospace",
                }}
              >
                sentiment
              </span>
              <h2
                className="mt-2 text-white"
                style={{
                  fontSize: "32px",
                  fontWeight: 600,
                  lineHeight: "40px",
                  letterSpacing: "-0.04em",
                }}
              >
                Overall voice, one line.
              </h2>
            </div>
            <span
              className="font-mono text-[12px] text-[#666]"
              style={{
                fontFamily: "var(--font-geist-mono), monospace",
              }}
            >
              last sync · {formatStamp(summary.updated_at)}
            </span>
          </div>

          <VercelSentimentMeter
            positivePercent={summary.overall_sentiment.positive_percent}
            negativePercent={summary.overall_sentiment.negative_percent}
            totalReviews={summary.total_reviews}
          />
        </section>

        {/* ── Movie inventory ──────────────────────────── */}
        <section className="mx-auto max-w-[1400px] px-6 py-12">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <span
                className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#666]"
                style={{
                  fontFamily: "var(--font-geist-mono), monospace",
                }}
              >
                inventory · {String(movies.length).padStart(2, "0")} films
              </span>
              <h2
                className="mt-2 text-white"
                style={{
                  fontSize: "32px",
                  fontWeight: 600,
                  lineHeight: "40px",
                  letterSpacing: "-0.04em",
                }}
              >
                Today&apos;s film analysis.
              </h2>
              <p className="mt-2 max-w-xl text-[15px] tracking-[-0.01em] text-[#a1a1a1]">
                각 카드는 하나의 영화 단위 batch 실행 결과입니다.
                긍/부정 비율, 상위 의견 군집, 마지막 빌드 시각이 함께 표시됩니다.
              </p>
            </div>
            <div className="hidden items-center gap-2 md:flex">
              <button
                type="button"
                className="rounded-full border border-[#262626] bg-transparent px-3 py-1.5 text-[13px] font-medium tracking-[-0.01em] text-[#a1a1a1] hover:bg-white/[0.04] hover:text-white"
              >
                Filter
              </button>
              <button
                type="button"
                className="rounded-full bg-white/[0.06] px-3 py-1.5 text-[13px] font-medium tracking-[-0.01em] text-white"
              >
                Recent
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {movies.map((m, i) => (
              <VercelMovieCard
                key={m.movie_id}
                movie={m}
                featured={i === 0}
              />
            ))}
          </div>
        </section>

        {/* ── Polarity-flipped showcase band ───────────── */}
        <section className="border-y border-[#1f1f1f] bg-[#0f0f0f]">
          <div className="mx-auto max-w-[1400px] px-6 py-20">
            <div className="grid grid-cols-1 gap-12 lg:grid-cols-[1.05fr_1fr]">
              <div>
                <span
                  className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#666]"
                  style={{
                    fontFamily: "var(--font-geist-mono), monospace",
                  }}
                >
                  architecture · b → c → d
                </span>
                <h2
                  className="mt-3 max-w-[640px] text-white"
                  style={{
                    fontSize: "44px",
                    fontWeight: 600,
                    lineHeight: 1.05,
                    letterSpacing: "-0.045em",
                  }}
                >
                  Three modules, one daily job.
                </h2>
                <p className="mt-5 max-w-[560px] text-[16px] leading-7 text-[#a1a1a1]">
                  Orchestrator는 작업의 상태만 책임집니다.
                  추출은 LLM 모듈이, 군집화는 클러스터 모듈이 맡습니다.
                  세 단계는 같은 <code className="rounded bg-[#1a1a1a] px-1.5 py-0.5 font-mono text-[13px] text-[#ededed]">job_id</code> 하나로 묶여 흐릅니다.
                </p>

                <ul className="mt-8 space-y-3">
                  {[
                    {
                      tag: "B",
                      label: "Orchestrator",
                      sub: "FastAPI · Postgres",
                      tone: "#0070f3",
                    },
                    {
                      tag: "C",
                      label: "LLM extractor",
                      sub: "dummy · rule-based · openai",
                      tone: "#7928ca",
                    },
                    {
                      tag: "D",
                      label: "Cluster engine",
                      sub: "hdbscan · miniLM · kmeans",
                      tone: "#50e3c2",
                    },
                  ].map((row) => (
                    <li
                      key={row.tag}
                      className="flex items-center gap-4 rounded-[8px] border border-[#1f1f1f] bg-[#0a0a0a] px-4 py-3"
                    >
                      <span
                        className="inline-flex h-8 w-8 items-center justify-center rounded-md font-mono text-[14px] font-medium text-white"
                        style={{
                          background: `linear-gradient(135deg, ${row.tone}, ${row.tone}55)`,
                          fontFamily: "var(--font-geist-mono), monospace",
                        }}
                      >
                        {row.tag}
                      </span>
                      <div className="flex-1">
                        <div className="text-[15px] font-medium tracking-[-0.01em] text-white">
                          {row.label}
                        </div>
                        <div
                          className="mt-0.5 font-mono text-[12px] text-[#666]"
                          style={{
                            fontFamily: "var(--font-geist-mono), monospace",
                          }}
                        >
                          {row.sub}
                        </div>
                      </div>
                      <span className="font-mono text-[11px] text-[#50e3c2]">
                        ● online
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* code-editor-mockup */}
              <div
                className="overflow-hidden rounded-[12px] border border-[#1f1f1f] bg-black"
                style={{
                  boxShadow:
                    "0 1px 1px rgba(255,255,255,0.04) inset, 0 24px 48px -16px rgba(0,0,0,0.7)",
                }}
              >
                <div className="flex items-center justify-between border-b border-[#1f1f1f] bg-[#0a0a0a] px-4 py-2.5">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
                    <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
                    <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
                  </div>
                  <span
                    className="font-mono text-[12px] text-[#666]"
                    style={{
                      fontFamily: "var(--font-geist-mono), monospace",
                    }}
                  >
                    pipeline.sh
                  </span>
                  <span
                    className="font-mono text-[11px] text-[#666]"
                    style={{
                      fontFamily: "var(--font-geist-mono), monospace",
                    }}
                  >
                    ↳ daily-batch
                  </span>
                </div>
                <pre
                  className="overflow-x-auto px-5 py-5 text-[13px] leading-[20px]"
                  style={{
                    fontFamily: "var(--font-geist-mono), monospace",
                    color: "#ededed",
                  }}
                >
                  <span className="text-[#666]">$</span>{" "}
                  <span className="text-[#50e3c2]">curl</span> -X POST{" "}
                  <span className="text-[#f9cb28]">/batch/jobs</span>
                  {"\n"}
                  <span className="text-[#666]">  → job_id</span>{" "}
                  <span className="text-[#ededed]">job_demo_001</span>
                  {"\n\n"}
                  <span className="text-[#666]">$</span>{" "}
                  <span className="text-[#50e3c2]">curl</span> -X POST{" "}
                  <span className="text-[#f9cb28]">/batch/jobs/$id/run-llm</span>
                  {"\n"}
                  <span className="text-[#666]">  → status</span>{" "}
                  <span className="text-[#0070f3]">llm_processing</span>
                  {"\n\n"}
                  <span className="text-[#666]">$</span>{" "}
                  <span className="text-[#50e3c2]">curl</span> -X POST{" "}
                  <span className="text-[#f9cb28]">/batch/jobs/$id/run-cluster</span>
                  {"\n"}
                  <span className="text-[#666]">  → status</span>{" "}
                  <span className="text-[#ff0080]">clustering</span>
                  {"\n\n"}
                  <span className="text-[#666]">$</span>{" "}
                  <span className="text-[#50e3c2]">curl</span> -X POST{" "}
                  <span className="text-[#f9cb28]">/batch/jobs/$id/build-final</span>
                  {"\n"}
                  <span className="text-[#666]">  → status</span>{" "}
                  <span className="text-[#50e3c2]">completed</span>
                  {"\n"}
                  <span className="text-[#666]">  ✓ {totalReviewsAcross.toLocaleString()} reviews · {avgPositive}% positive</span>
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* ── Keywords + Activity (2-column) ───────────── */}
        <section className="mx-auto max-w-[1400px] px-6 py-16">
          <div className="mb-6 flex items-end justify-between">
            <div>
              <span
                className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#666]"
                style={{
                  fontFamily: "var(--font-geist-mono), monospace",
                }}
              >
                signals
              </span>
              <h2
                className="mt-2 text-white"
                style={{
                  fontSize: "32px",
                  fontWeight: 600,
                  lineHeight: "40px",
                  letterSpacing: "-0.04em",
                }}
              >
                What the audience says most.
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.1fr_1fr]">
            <VercelKeywordTable
              title="Top keywords · overall"
              keywords={summary.top_keywords_overall}
            />
            <VercelDeploymentLog activities={summary.recent_activities} />
          </div>
        </section>

        {/* ── Footer ───────────────────────────────────── */}
        <footer className="border-t border-[#1f1f1f] bg-[#0a0a0a]">
          <div className="mx-auto grid max-w-[1400px] grid-cols-2 gap-12 px-6 py-16 md:grid-cols-4">
            <div className="col-span-2">
              <div className="flex items-center gap-2">
                <svg
                  viewBox="0 0 76 65"
                  fill="currentColor"
                  aria-hidden
                  className="h-4 text-white"
                >
                  <path d="M37.5274 0L75.0548 65H0L37.5274 0Z" />
                </svg>
                <span className="text-[15px] font-medium tracking-[-0.01em] text-white">
                  review.os
                </span>
              </div>
              <p className="mt-3 max-w-sm text-[14px] leading-5 tracking-[-0.01em] text-[#888]">
                LLM 기반 영화 리뷰 의견 구조화 시스템 — 데일리 배치로
                추출 · 군집화 · 요약을 한 흐름에 묶어 처리합니다.
              </p>
              <div className="mt-5 flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-[#0e2a26] px-2.5 py-1 text-[12px] font-medium text-[#50e3c2]">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#50e3c2] shadow-[0_0_6px_#50e3c2]" />
                  All systems normal
                </span>
                <span
                  className="font-mono text-[11px] text-[#666]"
                  style={{
                    fontFamily: "var(--font-geist-mono), monospace",
                  }}
                >
                  v0.1.0
                </span>
              </div>
            </div>

            {[
              {
                heading: "Pipeline",
                items: ["Orchestrator", "LLM extract", "Cluster engine", "Final build"],
              },
              {
                heading: "Resources",
                items: ["Docs", "Changelog", "Status", "GitHub"],
              },
            ].map((col) => (
              <div key={col.heading}>
                <h4
                  className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
                  style={{
                    fontFamily: "var(--font-geist-mono), monospace",
                  }}
                >
                  {col.heading}
                </h4>
                <ul className="mt-4 space-y-2.5">
                  {col.items.map((it) => (
                    <li key={it}>
                      <a
                        href="#"
                        className="text-[14px] tracking-[-0.01em] text-[#a1a1a1] hover:text-white"
                      >
                        {it}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-[#1f1f1f]">
            <div className="mx-auto flex max-w-[1400px] items-center justify-between px-6 py-5">
              <span
                className="font-mono text-[11px] text-[#666]"
                style={{
                  fontFamily: "var(--font-geist-mono), monospace",
                }}
              >
                © {new Date(summary.updated_at).getFullYear()} review.os · build {shortStamp(summary.updated_at)}
              </span>
              <Link
                href="/style-experiments/brutalist"
                className="text-[12px] tracking-[-0.01em] text-[#666] hover:text-white"
              >
                see also · brutalist edition →
              </Link>
            </div>
          </div>
        </footer>
      </div>
    </main>
  );
}
