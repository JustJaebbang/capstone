import Link from "next/link";

import {
  fetchDashboardMovies,
  fetchDashboardSummary,
} from "@/lib/dashboard";

import WatchaNav from "@/components/style-experiments/watcha/WatchaNav";
import WatchaHero from "@/components/style-experiments/watcha/WatchaHero";
import WatchaPosterCard from "@/components/style-experiments/watcha/WatchaPosterCard";
import WatchaKeywordEditorial from "@/components/style-experiments/watcha/WatchaKeywordEditorial";
import WatchaActivityList from "@/components/style-experiments/watcha/WatchaActivityList";
import WatchaFooter from "@/components/style-experiments/watcha/WatchaFooter";

export default async function WatchaPediaPage() {
  const [summary, moviesResponse] = await Promise.all([
    fetchDashboardSummary(),
    fetchDashboardMovies(),
  ]);
  const movies = moviesResponse.items;

  const sorted = [...movies].sort(
    (a, b) => b.sentiment.positive_percent - a.sentiment.positive_percent,
  );
  const feature = sorted[0];
  const placeholderCount = Math.max(0, 4 - sorted.length);

  return (
    <main className="min-h-screen bg-[#fbf9f3] text-[#161616] antialiased selection:bg-[#ff2c63]/85 selection:text-white">
      {/* Scoped page typography + helper classes */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        .watcha-page {
          font-family: 'Manrope', var(--font-geist-sans), 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif;
          font-feature-settings: 'ss01';
          -webkit-font-smoothing: antialiased;
          color: #161616;
        }
        .watcha-page .font-serif {
          font-family: 'Fraunces', 'Noto Serif KR', 'Apple SD Gothic Neo', Georgia, serif;
          font-feature-settings: 'lnum';
        }
        .watcha-page .font-mono {
          font-family: 'JetBrains Mono', var(--font-geist-mono), ui-monospace, monospace;
        }
        .watcha-page .tabular-nums {
          font-variant-numeric: tabular-nums lining-nums;
        }
      `}</style>

      <div className="watcha-page">
        <WatchaNav updatedAt={summary.updated_at} />
        {feature ? (
          <WatchaHero feature={feature} summary={summary} />
        ) : (
          <section className="border-b border-[#e8e3d6]">
            <div className="mx-auto max-w-[1240px] px-8 py-28 text-center">
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                pipeline empty
              </p>
              <h1 className="mt-6 font-serif text-[56px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[72px]">
                아직 분석된 <span className="italic text-[#ff2c63]">작품</span>이 없습니다.
              </h1>
              <p className="mt-5 text-[15px] leading-[1.7] text-[#3d3a35]">
                백엔드 파이프라인이 다음 배치를 끝내면 이 자리에 첫 번째 영화가 도착합니다.
              </p>
            </div>
          </section>
        )}

        {/* ── Collection 01 ─────────────────────────── */}
        <section className="border-b border-[#e8e3d6]">
          <div className="mx-auto max-w-[1240px] px-8 py-24">
            <div className="mb-14 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  Collection · 01
                </p>
                <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[56px]">
                  이번 회차의{" "}
                  <span className="italic text-[#ff2c63]">영화들</span>
                </h2>
                <p className="mt-4 max-w-[480px] text-[15px] leading-[1.7] text-[#3d3a35]">
                  포스터 아래의 숫자는 평점이 아닌{" "}
                  <em className="not-italic font-medium text-[#161616]">
                    호감 비율
                  </em>
                  입니다. 카드를 누르면 미리 분석된 결과 페이지로 바로 이동합니다.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="rounded-full bg-[#161616] px-4 py-2 font-mono text-[11px] uppercase tracking-[0.16em] text-[#fbf9f3]"
                >
                  호감순
                </button>
                <button
                  type="button"
                  className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760] hover:bg-[#f0ece0]"
                >
                  최신순
                </button>
                <button
                  type="button"
                  className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760] hover:bg-[#f0ece0]"
                >
                  리뷰 많은 순
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-x-8 gap-y-14 md:grid-cols-3 lg:grid-cols-4">
              {sorted.map((m, i) => (
                <WatchaPosterCard
                  key={m.movie_id}
                  movie={m}
                  rank={i + 1}
                />
              ))}

              {/* "다음 배치 대기" placeholders to fill the editorial grid */}
              {Array.from({ length: placeholderCount }).map((_, i) => (
                <div key={`coming-${i}`} aria-hidden>
                  <div className="relative aspect-[2/3] w-full overflow-hidden rounded-[6px] border border-dashed border-[#dcd6c5] bg-[#f0ece0]">
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                      <span className="font-serif text-[40px] italic leading-none text-[#9a958b]">
                        soon
                      </span>
                      <p className="mt-3 px-6 font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
                        다음 배치에서 공개
                      </p>
                    </div>
                  </div>
                  <p className="mt-4 font-serif text-[18px] tracking-tight text-[#9a958b]">
                    Untitled
                  </p>
                  <p className="mt-1 text-[12.5px] text-[#9a958b]">
                    소스 큐 대기 중
                  </p>
                  <div className="mt-3 h-[3px] w-full rounded-full bg-[#efe9d8]" />
                </div>
              ))}
            </div>

            {/* trailing editorial line */}
            <div className="mt-14 flex items-center justify-between border-t border-[#e8e3d6] pt-6">
              <p className="font-serif text-[15px] italic text-[#6b6760]">
                &ldquo;숫자는 합의의 결과이고, 키워드는 합의되지 않은 의견의
                목록이다.&rdquo;
              </p>
              <Link
                href="/movies"
                className="font-mono text-[11px] uppercase tracking-[0.18em] text-[#161616] hover:text-[#ff2c63]"
              >
                전체 대시보드 →
              </Link>
            </div>
          </div>
        </section>

        <WatchaKeywordEditorial keywords={summary.top_keywords_overall} />
        <WatchaActivityList
          activities={summary.recent_activities}
          movies={movies}
        />
        <WatchaFooter updatedAt={summary.updated_at} />
      </div>
    </main>
  );
}
