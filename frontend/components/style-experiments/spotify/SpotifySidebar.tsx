import Link from "next/link";
import type { DashboardMovie } from "@/lib/types";

type Props = {
  movies: DashboardMovie[];
};

// deterministic gradient picker (same family as the album cards)
const gradientFor = (id: string): string => {
  const palettes = [
    "linear-gradient(135deg, #1db954 0%, #064e2c 100%)",
    "linear-gradient(135deg, #f59e0b 0%, #7c2d12 100%)",
    "linear-gradient(135deg, #ef4444 0%, #4c0519 100%)",
    "linear-gradient(135deg, #6366f1 0%, #1e1b4b 100%)",
    "linear-gradient(135deg, #ec4899 0%, #4a044e 100%)",
    "linear-gradient(135deg, #06b6d4 0%, #083344 100%)",
  ];
  const sum = [...id].reduce((s, c) => s + c.charCodeAt(0), 0);
  return palettes[sum % palettes.length];
};

export default function SpotifySidebar({ movies }: Props) {
  return (
    <aside className="hidden h-full w-[280px] shrink-0 flex-col gap-2 lg:flex">
      {/* top panel — Home / Search */}
      <div className="rounded-lg bg-[#121212] p-2">
        <Link
          href="/"
          className="flex items-center gap-4 rounded-md px-4 py-3 text-white hover:bg-white/[0.06]"
        >
          <svg
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden
            className="h-6 w-6"
          >
            <path d="M12.5 3.247a1 1 0 00-1 0L4 7.577V20h4.5v-6a1 1 0 011-1h5a1 1 0 011 1v6H20V7.577l-7.5-4.33zm-2-1.732a3 3 0 013 0l7.5 4.33a2 2 0 011 1.732V21a1 1 0 01-1 1h-6.5a1 1 0 01-1-1v-6h-3v6a1 1 0 01-1 1H3a1 1 0 01-1-1V7.577a2 2 0 011-1.732l7.5-4.33z" />
          </svg>
          <span
            className="text-[15px] text-white"
            style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
          >
            Home
          </span>
        </Link>

        <Link
          href="/movies"
          className="flex items-center gap-4 rounded-md px-4 py-3 text-[#b3b3b3] hover:text-white hover:bg-white/[0.06]"
        >
          <svg
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden
            className="h-6 w-6"
          >
            <path d="M10.533 1.279c-5.18 0-9.407 4.14-9.407 9.279s4.226 9.279 9.407 9.279c2.234 0 4.29-.77 5.907-2.058l4.353 4.353a1 1 0 101.414-1.414l-4.344-4.344a9.157 9.157 0 002.077-5.816c0-5.14-4.226-9.28-9.407-9.28zm-7.407 9.279c0-4.006 3.302-7.28 7.407-7.28s7.407 3.274 7.407 7.28-3.302 7.279-7.407 7.279-7.407-3.273-7.407-7.28z" />
          </svg>
          <span className="text-[15px]" style={{ fontWeight: 400 }}>
            Search
          </span>
        </Link>
      </div>

      {/* library panel */}
      <div className="flex flex-1 flex-col gap-4 overflow-hidden rounded-lg bg-[#121212] p-2">
        <div className="flex items-center justify-between px-2 pt-2">
          <button
            type="button"
            className="flex items-center gap-3 text-[#b3b3b3] transition-colors hover:text-white"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className="h-6 w-6">
              <path d="M14.5 2.134a1 1 0 011 0l6 3.464a1 1 0 01.5.866V21a1 1 0 01-1 1h-6a1 1 0 01-1-1V3a1 1 0 01.5-.866zM16 4.732V20h4V7.041l-4-2.309zM3 22a1 1 0 01-1-1V3a1 1 0 012 0v18a1 1 0 01-1 1zM8 22a1 1 0 01-1-1V3a1 1 0 012 0v18a1 1 0 01-1 1z" />
            </svg>
            <span
              className="text-[15px]"
              style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
            >
              Your library
            </span>
          </button>
          <div className="flex items-center gap-1">
            <button
              type="button"
              aria-label="Create playlist"
              className="flex h-8 w-8 items-center justify-center rounded-full text-[#b3b3b3] hover:bg-white/[0.06] hover:text-white"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className="h-4 w-4">
                <path d="M11.99 0C5.37 0 0 5.37 0 12s5.37 12 11.99 12C18.62 24 24 18.63 24 12S18.62 0 11.99 0zM13 13v5h-2v-5H6v-2h5V6h2v5h5v2h-5z" />
              </svg>
            </button>
          </div>
        </div>

        {/* filter pills */}
        <div className="flex gap-2 px-2">
          <span className="rounded-full bg-[#1f1f1f] px-3 py-1 text-[13px] font-medium text-white">
            Films
          </span>
          <span className="rounded-full bg-transparent px-3 py-1 text-[13px] font-medium text-[#b3b3b3] hover:bg-[#1a1a1a] hover:text-white">
            Batches
          </span>
        </div>

        {/* search-within bar */}
        <div className="flex items-center justify-between px-2 text-[#b3b3b3]">
          <button
            type="button"
            aria-label="Search in library"
            className="flex h-8 w-8 items-center justify-center rounded-full hover:text-white"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M10.533 1.279c-5.18 0-9.407 4.14-9.407 9.279s4.226 9.279 9.407 9.279c2.234 0 4.29-.77 5.907-2.058l4.353 4.353a1 1 0 101.414-1.414l-4.344-4.344a9.157 9.157 0 002.077-5.816c0-5.14-4.226-9.28-9.407-9.28z" />
            </svg>
          </button>
          <button
            type="button"
            className="flex items-center gap-1 text-[12px] font-medium hover:text-white"
            style={{ fontWeight: 600 }}
          >
            Recents
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-3 w-3">
              <path d="M14.78 6.97l-5.78 5.78a1 1 0 01-1.41 0L1.81 6.97a1 1 0 011.41-1.41L8.3 10.64l5.07-5.07a1 1 0 011.41 1.4z" />
            </svg>
          </button>
        </div>

        {/* library list — movies as playlists */}
        <ul className="flex flex-col gap-1 overflow-y-auto px-1 pb-2">
          {/* Liked songs analog */}
          <li>
            <a
              href="#liked"
              className="flex items-center gap-3 rounded-md p-2 hover:bg-white/[0.06]"
            >
              <span
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md"
                style={{
                  background:
                    "linear-gradient(135deg, #1db954 0%, #053e1e 100%)",
                }}
              >
                <svg viewBox="0 0 16 16" fill="white" aria-hidden className="h-5 w-5">
                  <path d="M15.724 4.22A4.313 4.313 0 0012.192.814a4.269 4.269 0 00-3.622 1.13.837.837 0 01-1.14 0 4.272 4.272 0 00-6.21 5.855l5.916 7.05a1.128 1.128 0 001.728 0l5.916-7.05a4.228 4.228 0 00.944-3.577z" />
                </svg>
              </span>
              <div className="min-w-0">
                <p className="truncate text-[15px] text-white" style={{ fontWeight: 600 }}>
                  Liked opinions
                </p>
                <p className="truncate text-[13px] text-[#b3b3b3]" style={{ fontWeight: 400 }}>
                  <span style={{ color: "#1ed760" }}>♡</span> Playlist · 24 phrases
                </p>
              </div>
            </a>
          </li>

          {movies.map((m) => (
            <li key={m.movie_id}>
              <a
                href={`#movie-${m.movie_id}`}
                className="flex items-center gap-3 rounded-md p-2 hover:bg-white/[0.06]"
              >
                <span
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md text-[10px] font-bold uppercase text-white/90"
                  style={{
                    background: gradientFor(m.movie_id),
                    letterSpacing: "0.02em",
                  }}
                >
                  {m.movie_title.slice(0, 2)}
                </span>
                <div className="min-w-0">
                  <p
                    className="truncate text-[15px] text-white"
                    style={{ fontWeight: 600, letterSpacing: "-0.01em" }}
                  >
                    {m.movie_title}
                  </p>
                  <p className="flex items-center gap-1.5 truncate text-[13px] text-[#b3b3b3]">
                    {m.job_status === "running" && (
                      <span
                        className="inline-block h-2 w-2 rounded-full"
                        style={{
                          background: "#1ed760",
                          boxShadow: "0 0 6px #1ed760",
                        }}
                      />
                    )}
                    Album · {m.source}
                  </p>
                </div>
              </a>
            </li>
          ))}

          {/* a couple of static rows so the library feels populated */}
          {[
            { name: "Daily batch", sub: "Playlist · review.os" },
            { name: "Top opinions today", sub: "Playlist · auto-generated" },
          ].map((row) => (
            <li key={row.name}>
              <a
                href="#"
                className="flex items-center gap-3 rounded-md p-2 hover:bg-white/[0.06]"
              >
                <span
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md text-white/70"
                  style={{
                    background:
                      "linear-gradient(135deg, #282828 0%, #181818 100%)",
                  }}
                >
                  <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-5 w-5">
                    <path d="M15 15H1V1h14v14zM2 14h12V2H2v12z" />
                  </svg>
                </span>
                <div className="min-w-0">
                  <p
                    className="truncate text-[15px] text-white"
                    style={{ fontWeight: 600, letterSpacing: "-0.01em" }}
                  >
                    {row.name}
                  </p>
                  <p className="truncate text-[13px] text-[#b3b3b3]">{row.sub}</p>
                </div>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
