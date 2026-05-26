import Link from "next/link";

import {
  fetchDashboardMovies,
  fetchDashboardSummary,
} from "@/lib/dashboard";

import WatchaFontStyles from "@/components/style-experiments/watcha/WatchaFontStyles";
import WatchaNav from "@/components/style-experiments/watcha/WatchaNav";
import WatchaFooter from "@/components/style-experiments/watcha/WatchaFooter";
import WatchaMovieRow from "@/components/style-experiments/watcha/WatchaMovieRow";

function cardHrefFor(movie: { latest_job_id: string | null }): string | null {
  return movie.latest_job_id ? `/jobs/${movie.latest_job_id}/result` : null;
}

export default async function MoviesPage() {
  const [moviesResponse, summary] = await Promise.all([
    fetchDashboardMovies(),
    fetchDashboardSummary(),
  ]);
  const movies = moviesResponse.items;

  return (
    <main className="flex min-h-screen flex-col bg-[#fbf9f3] text-[#161616] antialiased selection:bg-[#ff2c63]/85 selection:text-white">
      <WatchaFontStyles />

      <div className="watcha-page flex flex-1 flex-col">
        <WatchaNav updatedAt={summary.updated_at} />

        <section className="flex-1 border-b border-[#e8e3d6]">
          <div className="mx-auto max-w-[1240px] px-8 py-16 lg:py-20">
            <div className="mb-12">
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                Collection · 01
              </p>
              <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[56px]">
                이번 회차의{" "}
                <span className="italic text-[#ff2c63]">영화들</span>
              </h2>
              <p className="mt-4 max-w-[560px] text-[15px] leading-[1.7] text-[#3d3a35]">
                카드를 누르면 미리 분석된 결과 페이지로 바로 이동합니다.
                숫자는 평점이 아닌{" "}
                <em className="not-italic font-medium text-[#161616]">
                  호감 비율
                </em>
                입니다.
              </p>
            </div>

            {movies.length === 0 ? (
              <div className="rounded-[8px] border border-dashed border-[#dcd6c5] bg-white p-16 text-center">
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  pipeline empty
                </p>
                <p className="mt-4 font-serif text-[24px] text-[#6b6760]">
                  아직 분석된 영화가 없습니다.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-5 md:grid-cols-2 md:gap-6">
                {movies.map((m) => (
                  <WatchaMovieRow
                    key={m.movie_id}
                    movie={m}
                    href={cardHrefFor(m)}
                  />
                ))}
              </div>
            )}
          </div>
        </section>

        <WatchaFooter updatedAt={summary.updated_at} />
      </div>
    </main>
  );
}