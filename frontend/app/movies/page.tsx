import { fetchDashboardData } from "@/lib/dashboard";

import WatchaFontStyles from "@/components/style-experiments/watcha/WatchaFontStyles";
import WatchaNav from "@/components/style-experiments/watcha/WatchaNav";
import WatchaFooter from "@/components/style-experiments/watcha/WatchaFooter";
import WatchaMovieRow from "@/components/style-experiments/watcha/WatchaMovieRow";

function cardHrefFor(movie: { latest_job_id: string | null }): string | null {
  return movie.latest_job_id ? `/jobs/${movie.latest_job_id}/result` : null;
}

function ErrorState({ message }: { message: string }) {
  const stamp = new Date().toISOString();
  return (
    <main className="flex min-h-screen flex-col bg-[#fbf9f3] text-[#161616] antialiased">
      <WatchaFontStyles />
      <div className="watcha-page flex flex-1 flex-col">
        <WatchaNav updatedAt={stamp} />
        <section className="flex-1 border-b border-[#e8e3d6]">
          <div className="mx-auto max-w-[1240px] px-8 py-24">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
              pipeline offline
            </p>
            <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[56px]">
              대시보드 데이터를{" "}
              <span className="italic text-[#ff2c63]">불러올 수 없습니다</span>
            </h2>
            <p className="mt-4 max-w-[560px] text-[15px] leading-[1.7] text-[#3d3a35]">
              백엔드 API({process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"})에
              연결하지 못했습니다. 잠시 후 다시 시도하거나, 백엔드 서버가
              실행 중인지 확인해주세요.
            </p>
            <pre className="mt-8 max-w-full overflow-x-auto rounded-[6px] border border-[#e8e3d6] bg-white p-4 font-mono text-[12px] text-[#6b6760]">
              {message}
            </pre>
          </div>
        </section>
        <WatchaFooter updatedAt={stamp} />
      </div>
    </main>
  );
}

export default async function MoviesPage() {
  let data;
  try {
    data = await fetchDashboardData();
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return <ErrorState message={message} />;
  }

  const { movies, summary } = data;

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