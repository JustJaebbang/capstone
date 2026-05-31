import Link from "next/link";

import ReviewTrafficChart from "@/components/ReviewTrafficChart";
import ElementScoreChart from "@/components/ElementScoreChart";
import ResultReviewSection from "@/components/ResultReviewSection";
import WatchaFontStyles from "@/components/style-experiments/watcha/WatchaFontStyles";
import WatchaSentimentRing from "@/components/style-experiments/watcha/WatchaSentimentRing";
import WatchaFooter from "@/components/style-experiments/watcha/WatchaFooter";

import { getFinalResult, getOpinionGroups } from "@/lib/api";

type ResultPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

type ApiElementScore = {
  element: string;
  score: number | null;
  positive_count: number;
  negative_count: number;
  mention_count: number;
};

type ApiFinalResult = {
  job_id?: string;
  movie_id?: string;
  movie_title?: string;
  poster_url?: string | null;
  summary: {
    sentiment_ratio: {
      positive_percent: number;
      negative_percent: number;
      positive_review_count?: number;
      negative_review_count?: number;
      tie_review_count?: number;
      total_review_count?: number;
      rule?: string;
    };
    element_scores?: ApiElementScore[];
  };
};

type ApiOpinionGroup = {
  cluster_id: string | number;
  label: string;
  count: number;
  sentiment?: "positive" | "negative";
};

type OpinionGroupsResponse =
  | ApiOpinionGroup[]
  | {
      items?: ApiOpinionGroup[];
      groups?: ApiOpinionGroup[];
      total_count?: number;
    };

type ViewOpinionGroup = {
  cluster_id: string;
  label: string;
  count: number;
  sentiment?: "positive" | "negative";
};

function normalizeOpinionGroups(
  response: OpinionGroupsResponse
): ViewOpinionGroup[] {
  const groups = Array.isArray(response)
    ? response
    : response.items ?? response.groups ?? [];

  return groups
    .map((group) => ({
      cluster_id: String(group.cluster_id),
      label: group.label,
      count: group.count,
      sentiment: group.sentiment,
    }))
    .sort((a, b) => b.count - a.count);
}

function sentimentVerdict(positivePercent: number): string {
  if (positivePercent >= 75) return "압도적 긍정";
  if (positivePercent >= 55) return "긍정적";
  if (positivePercent >= 35) return "부정적";
  return "압도적 부정";
}

// Deterministic poster gradient — moody, film-still palette
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
    ["#2a1010", "#4a1a1a", "#0f0404"],
    ["#1f1d2c", "#3a2a44", "#0a0a14"],
  ];
  const [a, b, c] = palettes[h % palettes.length];
  return `radial-gradient(120% 80% at 20% 0%, ${a} 0%, ${b} 55%, ${c} 100%)`;
}

export default async function ResultPage({ params }: ResultPageProps) {
  const { jobId } = await params;

  const [finalResultRaw, opinionGroupsRaw] = await Promise.all([
    getFinalResult(jobId),
    getOpinionGroups(jobId),
  ]);
  const finalResult = finalResultRaw as ApiFinalResult;
  const opinionGroupsResponse = opinionGroupsRaw as OpinionGroupsResponse;

  const opinionGroups = normalizeOpinionGroups(opinionGroupsResponse);
  const sentimentRatio = finalResult.summary.sentiment_ratio;

  const effectiveJobId = finalResult.job_id ?? jobId;
  const movieTitle = finalResult.movie_title ?? "Untitled";
  const posterSeed = finalResult.movie_id ?? effectiveJobId;
  const totalReviewCount = sentimentRatio.total_review_count ?? null;
  const positiveReviewCount = sentimentRatio.positive_review_count ?? null;
  const negativeReviewCount = sentimentRatio.negative_review_count ?? null;
  const topGroup = opinionGroups[0];

  return (
    <main className="min-h-screen bg-[#fbf9f3] text-[#161616] antialiased selection:bg-[#ff2c63]/85 selection:text-white">
      <WatchaFontStyles />

      <div className="watcha-page">
        {/* ── Nav ─────────────────────────────────────── */}
        <header className="sticky top-0 z-30 border-b border-[#e8e3d6] bg-[#fbf9f3]/85 backdrop-blur">
          <div className="mx-auto flex max-w-[1240px] items-center justify-between px-8 py-5">
            <Link href="/" className="flex items-baseline gap-1">
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
                job · {effectiveJobId}
              </span>
              <Link
                href="/movies"
                className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760] hover:bg-[#f0ece0]"
              >
                ← 영화 목록으로
              </Link>
            </div>
          </div>
        </header>

        {/* ── Hero ────────────────────────────────────── */}
        <section className="border-b border-[#e8e3d6]">
          <div className="mx-auto max-w-[1240px] px-8 py-16 lg:py-24">
            <Link
              href="/movies"
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
                  style={
                    finalResult.poster_url
                      ? undefined
                      : { background: posterGradient(posterSeed) }
                  }
                >
                  {finalResult.poster_url ? (
                    <>
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={finalResult.poster_url}
                        alt={movieTitle}
                        className="absolute inset-0 h-full w-full object-cover"
                      />
                    </>
                  ) : (
                    <div
                      aria-hidden
                      className="pointer-events-none absolute inset-0 opacity-[0.18] mix-blend-overlay"
                      style={{
                        backgroundImage:
                          "radial-gradient(rgba(255,255,255,0.6) 1px, transparent 1px)",
                        backgroundSize: "3px 3px",
                      }}
                    />
                  )}
                  <div className="absolute inset-0 flex flex-col justify-between p-10">
                    <div className="flex items-start justify-end">
                      <span className="rounded-full bg-white/10 px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-[#27ae60] backdrop-blur">
                        completed
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Meta */}
              <div className="flex flex-col">
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  Analysis · 분석 완료
                </p>
                <h1 className="mt-5 font-serif text-[58px] font-normal italic leading-[1.02] tracking-[-0.028em] text-[#ff2c63] sm:text-[72px] lg:text-[84px]">
                  {sentimentVerdict(sentimentRatio.positive_percent)}
                </h1>

                <div className="mt-10 flex items-center gap-10">
                  <WatchaSentimentRing
                    positivePercent={sentimentRatio.positive_percent}
                    size={180}
                    thickness={6}
                  />
                  <div className="flex flex-col gap-3">
                    <div>
                      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                        positive
                      </p>
                      <p className="mt-1 flex items-baseline gap-1 font-serif text-[26px] leading-none text-[#ff2c63] tabular-nums">
                        {sentimentRatio.positive_percent}%
                        {positiveReviewCount !== null && (
                          <span className="text-[12px] font-normal text-[#9a958b]">
                            · {positiveReviewCount.toLocaleString()}건
                          </span>
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                        negative
                      </p>
                      <p className="mt-1 flex items-baseline gap-1 font-serif text-[26px] leading-none text-[#0f4c5c] tabular-nums">
                        {sentimentRatio.negative_percent}%
                        {negativeReviewCount !== null && (
                          <span className="text-[12px] font-normal text-[#9a958b]">
                            · {negativeReviewCount.toLocaleString()}건
                          </span>
                        )}
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
                      {totalReviewCount !== null
                        ? totalReviewCount.toLocaleString()
                        : "—"}
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
                      {opinionGroups.length}
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
                      {topGroup?.label ?? "—"}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </section>

        {/* ── 긍정/부정 비율 + 요소별 점수 (2단 유지) ── */}
        <section className="border-b border-[#e8e3d6] bg-[#f5f1e6]">
          <div className="mx-auto max-w-[1240px] px-8 py-20">
            <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  Editor&apos;s note · 01
                </p>
                <h2 className="mt-4 font-serif text-[36px] leading-[1.1] tracking-[-0.02em] text-[#161616] sm:text-[44px]">
                  리뷰 트래픽과 <span className="italic">요소별 점수</span>
                </h2>
              </div>
              <p className="max-w-[420px] text-[14px] leading-[1.7] text-[#3d3a35] md:text-right">
                관객 반응의 전체 톤과, 영화의 각 요소(스토리·연기·연출 등)가
                각각 어떻게 평가받았는지를 한 번에 봅니다.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <ReviewTrafficChart movieId={finalResult.movie_id ?? ""} />
              <ElementScoreChart
                scores={finalResult.summary.element_scores ?? []}
                totalReviewCount={totalReviewCount}
              />
            </div>
          </div>
        </section>

        {/* ── 의견 군집 (TOP 3 + 그 외) ─────────────── */}
        <section className="border-b border-[#e8e3d6]">
          <div className="mx-auto max-w-[1240px] px-8 py-20">
            <div className="mb-2 flex flex-col gap-2">
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                Notebook · 02
              </p>
              <h2 className="font-serif text-[36px] leading-[1.05] tracking-[-0.02em] text-[#161616] sm:text-[44px]">
                관객 <span className="italic text-[#ff2c63]">의견 그룹</span>
              </h2>
              <p className="mt-2 max-w-[560px] text-[15px] leading-[1.7] text-[#3d3a35]">
                가장 많이 나온 의견 TOP 3와, 그 뒤를 잇는 그룹들입니다.
                카드를 누르면 해당 그룹의 실제 리뷰가 펼쳐집니다.
              </p>
            </div>

            <ResultReviewSection
              jobId={effectiveJobId}
              groups={opinionGroups}
            />
          </div>
        </section>

        <WatchaFooter updatedAt={new Date().toISOString()} />
      </div>
    </main>
  );
}
