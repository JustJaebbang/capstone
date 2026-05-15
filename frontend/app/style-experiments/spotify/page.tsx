import Link from "next/link";

import dashboardMoviesJson from "@/lib/mock/dashboard-movies.json";
import dashboardSummaryJson from "@/lib/mock/dashboard-summary.json";
import type {
  DashboardMoviesResponse,
  DashboardSummary,
} from "@/lib/types";

import SpotifySidebar from "@/components/style-experiments/spotify/SpotifySidebar";
import SpotifyTopBar from "@/components/style-experiments/spotify/SpotifyTopBar";
import SpotifyHero from "@/components/style-experiments/spotify/SpotifyHero";
import SpotifyAlbumCard from "@/components/style-experiments/spotify/SpotifyAlbumCard";
import SpotifyShelf from "@/components/style-experiments/spotify/SpotifyShelf";
import SpotifyTrackList from "@/components/style-experiments/spotify/SpotifyTrackList";
import SpotifyActivityList from "@/components/style-experiments/spotify/SpotifyActivityList";
import SpotifyNowPlayingBar from "@/components/style-experiments/spotify/SpotifyNowPlayingBar";

const summary = dashboardSummaryJson as unknown as DashboardSummary;
const movies = (dashboardMoviesJson as unknown as DashboardMoviesResponse)
  .items;

export default function SpotifyDashboardPage() {
  const featured = movies[0];

  return (
    <main
      className="h-screen bg-black text-white antialiased"
      style={{
        fontFamily:
          "var(--font-geist-sans), 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif",
      }}
    >
      <div className="flex h-[calc(100vh-88px)] gap-2 p-2">
        <SpotifySidebar movies={movies} />

        {/* main panel */}
        <div className="relative flex-1 overflow-y-auto rounded-lg bg-[#121212]">
          <SpotifyTopBar />

          <SpotifyHero featured={featured} summary={summary} />

          {/* "Made for you" shelf — movie albums */}
          <SpotifyShelf
            title="Recently analyzed"
            subtitle="오늘의 batch에서 막 도착한 앨범"
          >
            <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 xl:grid-cols-4">
              {movies.map((m) => (
                <SpotifyAlbumCard key={m.movie_id} movie={m} />
              ))}

              {/* filler "playlists" so the shelf reads like Spotify */}
              {[
                {
                  title: "Daily mix · 긍정",
                  sub: `Top ${summary.overall_sentiment.positive_percent}% of phrases`,
                  grad:
                    "linear-gradient(135deg, #1db954 0%, #053e1e 100%)",
                },
                {
                  title: "Daily mix · 부정",
                  sub: `${summary.overall_sentiment.negative_percent}% of phrases`,
                  grad:
                    "linear-gradient(135deg, #f3727f 0%, #4c0519 100%)",
                },
              ].map((p) => (
                <a
                  key={p.title}
                  href="#"
                  className="group flex flex-col gap-3 rounded-md bg-[#181818] p-4 transition-colors hover:bg-[#1f1f1f]"
                >
                  <div
                    className="relative aspect-square overflow-hidden rounded-md"
                    style={{
                      background: p.grad,
                      boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
                    }}
                  >
                    <div
                      aria-hidden
                      className="absolute inset-0 opacity-25 mix-blend-overlay"
                      style={{
                        backgroundImage:
                          "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0)",
                        backgroundSize: "12px 12px",
                      }}
                    />
                    <div className="absolute inset-0 flex flex-col justify-end p-4">
                      <p
                        className="text-[10.5px] uppercase text-white/85"
                        style={{
                          fontWeight: 600,
                          letterSpacing: "0.06em",
                        }}
                      >
                        Mix
                      </p>
                      <p
                        className="mt-1 text-[18px] leading-[1.1] text-white"
                        style={{
                          fontWeight: 700,
                          letterSpacing: "-0.02em",
                        }}
                      >
                        {p.title}
                      </p>
                    </div>
                    <button
                      type="button"
                      aria-label={`Play ${p.title}`}
                      className="absolute bottom-3 right-3 flex h-12 w-12 translate-y-3 items-center justify-center rounded-full text-black opacity-0 transition-all duration-200 group-hover:translate-y-0 group-hover:opacity-100"
                      style={{
                        background: "#1ed760",
                        boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
                      }}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className="h-5 w-5">
                        <path d="M7.05 3.606l13.49 7.788a.7.7 0 010 1.212L7.05 20.394A.7.7 0 016 19.788V4.212a.7.7 0 011.05-.606z" />
                      </svg>
                    </button>
                  </div>
                  <p
                    className="truncate text-[16px] text-white"
                    style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
                  >
                    {p.title}
                  </p>
                  <p className="line-clamp-2 text-[14px] text-[#b3b3b3]">
                    {p.sub}
                  </p>
                </a>
              ))}
            </div>
          </SpotifyShelf>

          {/* top opinions = track list */}
          <SpotifyShelf
            title="Top opinions today"
            subtitle="전체 영화 누적 · LLM + HDBSCAN 기준"
          >
            <SpotifyTrackList keywords={summary.top_keywords_overall} />
          </SpotifyShelf>

          {/* per-movie keyword chips — like artist's "Discography" row */}
          <SpotifyShelf
            title="By film"
            subtitle="영화별 톱 의견 — 카드를 눌러 앨범 페이지로"
          >
            <div className="grid grid-cols-1 gap-4 px-0 md:grid-cols-2">
              {movies.map((m) => (
                <div
                  key={`detail-${m.movie_id}`}
                  className="rounded-lg bg-[#181818] p-5"
                  id={`movie-${m.movie_id}`}
                >
                  <div className="flex items-center gap-4">
                    <span
                      className="flex h-16 w-16 shrink-0 items-center justify-center rounded-md text-[12px] uppercase text-white"
                      style={{
                        background:
                          m.movie_id.charCodeAt(2) % 2 === 0
                            ? "linear-gradient(135deg,#1db954,#064e2c)"
                            : "linear-gradient(135deg,#6366f1,#1e1b4b)",
                        fontWeight: 700,
                        letterSpacing: "0.05em",
                        boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
                      }}
                    >
                      {m.movie_title.slice(0, 2)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p
                        className="text-[10.5px] uppercase text-[#b3b3b3]"
                        style={{ fontWeight: 600, letterSpacing: "0.06em" }}
                      >
                        Album · {m.release_year}
                      </p>
                      <p
                        className="mt-1 truncate text-[22px] text-white"
                        style={{ fontWeight: 700, letterSpacing: "-0.02em" }}
                      >
                        {m.movie_title}
                      </p>
                      <p className="text-[13px] text-[#b3b3b3]">
                        <span style={{ color: "#1ed760", fontWeight: 700 }}>
                          {m.sentiment.positive_percent}%
                        </span>{" "}
                        positive ·{" "}
                        <span className="text-[#f3727f]">
                          {m.sentiment.negative_percent}%
                        </span>{" "}
                        negative · {m.review_count.toLocaleString()} reviews
                      </p>
                    </div>
                    <button
                      type="button"
                      aria-label={`Play ${m.movie_title}`}
                      className="flex h-12 w-12 items-center justify-center rounded-full text-black hover:scale-105"
                      style={{
                        background: "#1ed760",
                        boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
                      }}
                    >
                      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className="h-5 w-5">
                        <path d="M7.05 3.606l13.49 7.788a.7.7 0 010 1.212L7.05 20.394A.7.7 0 016 19.788V4.212a.7.7 0 011.05-.606z" />
                      </svg>
                    </button>
                  </div>

                  {/* sentiment bar */}
                  <div className="mt-5 flex h-1.5 overflow-hidden rounded-full bg-[#282828]">
                    <div
                      className="h-full"
                      style={{
                        width: `${m.sentiment.positive_percent}%`,
                        background:
                          "linear-gradient(90deg,#1db954,#1ed760)",
                      }}
                    />
                    <div
                      className="h-full"
                      style={{
                        width: `${m.sentiment.negative_percent}%`,
                        background:
                          "linear-gradient(90deg,#f3727f,#ef4444)",
                      }}
                    />
                  </div>

                  {/* mini track list */}
                  <ol className="mt-4 flex flex-col">
                    {m.top_keywords.map((kw) => (
                      <li
                        key={`${m.movie_id}-${kw.rank}`}
                        className="group flex items-center gap-3 rounded-sm px-2 py-2 hover:bg-white/[0.04]"
                      >
                        <span className="w-6 text-right text-[14px] text-[#b3b3b3]">
                          {kw.rank}
                        </span>
                        <span
                          className={`inline-block h-1.5 w-1.5 rounded-full ${
                            kw.sentiment === "positive"
                              ? "bg-[#1ed760] shadow-[0_0_6px_#1ed760]"
                              : kw.sentiment === "negative"
                              ? "bg-[#f3727f] shadow-[0_0_6px_#f3727f]"
                              : "bg-[#b3b3b3]"
                          }`}
                        />
                        <span
                          className="flex-1 text-[15px] text-white"
                          style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
                        >
                          {kw.label}
                        </span>
                        <span
                          className="text-[12px] text-[#b3b3b3]"
                          style={{ fontVariantNumeric: "tabular-nums" }}
                        >
                          {kw.count.toLocaleString()} plays
                        </span>
                      </li>
                    ))}
                  </ol>

                  <div className="mt-4 flex flex-wrap items-center gap-2">
                    {m.genres.map((g) => (
                      <span
                        key={g}
                        className="rounded-full bg-[#1f1f1f] px-3 py-1 text-[12px] text-[#cbcbcb]"
                      >
                        {g}
                      </span>
                    ))}
                    <span className="ml-auto text-[12px] text-[#b3b3b3]">
                      {m.notes ?? "—"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </SpotifyShelf>

          {/* listening history → recent activity */}
          <SpotifyShelf
            title="Recently played"
            subtitle="배치 실행 이력 — 최신 분석부터"
          >
            <SpotifyActivityList activities={summary.recent_activities} />
          </SpotifyShelf>

          {/* footer */}
          <footer className="mx-8 mt-12 mb-6 border-t border-[#282828] pt-6 pb-2 text-[12px] text-[#b3b3b3]">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p style={{ fontWeight: 700, color: "#fff" }}>review.os</p>
                <p>
                  LLM 기반 영화 리뷰 의견 구조화 시스템 · daily batch
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href="/style-experiments/brutalist"
                  className="hover:text-white"
                >
                  Brutalist edition →
                </Link>
                <Link
                  href="/style-experiments/vercel"
                  className="hover:text-white"
                >
                  Vercel edition →
                </Link>
              </div>
            </div>
          </footer>
        </div>
      </div>

      <SpotifyNowPlayingBar movie={featured} />
    </main>
  );
}
