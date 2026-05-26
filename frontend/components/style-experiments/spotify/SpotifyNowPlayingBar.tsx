import type { DashboardMovie } from "@/lib/types";

type Props = {
  movie: DashboardMovie;
};

const coverFor = (id: string): string => {
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

export default function SpotifyNowPlayingBar({ movie }: Props) {
  // synthesised progress / total — purely visual
  const totalSeconds = 240;
  const progressSeconds = Math.round(
    totalSeconds * (movie.sentiment.positive_percent / 100),
  );
  const fmt = (s: number) =>
    `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className="h-[88px] w-full bg-black px-4 py-2 text-white">
      <div className="grid h-full grid-cols-[1fr_2fr_1fr] items-center gap-4">
        {/* left — track info */}
        <div className="flex items-center gap-3 min-w-0">
          <span
            className="flex h-14 w-14 shrink-0 items-center justify-center rounded-sm text-[11px] uppercase text-white"
            style={{
              background: coverFor(movie.movie_id),
              fontWeight: 700,
              letterSpacing: "0.04em",
            }}
          >
            {movie.movie_title.slice(0, 2)}
          </span>
          <div className="min-w-0">
            <p
              className="truncate text-[14px] text-white"
              style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
            >
              {movie.movie_title}
            </p>
            <p className="truncate text-[12px] text-[#b3b3b3]">
              review.os · {movie.review_count.toLocaleString()} reviews
            </p>
          </div>
          <button
            type="button"
            aria-label="Save to your library"
            className="ml-3 flex h-8 w-8 items-center justify-center text-[#b3b3b3] hover:scale-105 hover:text-[#1ed760]"
          >
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M15.724 4.22A4.313 4.313 0 0012.192.814a4.269 4.269 0 00-3.622 1.13.837.837 0 01-1.14 0 4.272 4.272 0 00-6.21 5.855l5.916 7.05a1.128 1.128 0 001.728 0l5.916-7.05a4.228 4.228 0 00.944-3.577z" />
            </svg>
          </button>
        </div>

        {/* center — controls + progress */}
        <div className="flex flex-col items-center gap-1">
          <div className="flex items-center gap-4 text-[#b3b3b3]">
            <button
              type="button"
              aria-label="Shuffle"
              className="hover:text-white"
            >
              <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
                <path d="M13.151.922a.75.75 0 10-1.06 1.06L13.109 3H11.16a3.75 3.75 0 00-2.873 1.34l-6.173 7.356A2.25 2.25 0 01.39 12.5H0v1.5h.391a3.75 3.75 0 002.873-1.34l6.173-7.356a2.25 2.25 0 011.724-.804h1.947l-1.017 1.018a.75.75 0 001.06 1.06L15.98 3.75 13.15.922zM.391 3.5H0V2h.391a3.75 3.75 0 012.873 1.34l.7.834.04.046L4.4 4.59l-.86 1.07-.05-.058-.738-.88A2.25 2.25 0 00.391 3.5zm7.81 6.751l.054.064.738.879a2.25 2.25 0 001.724.806h1.947l-1.017-1.018a.75.75 0 011.06-1.06L15.98 12.25l-2.829 2.828a.75.75 0 11-1.06-1.06L13.109 13H11.16a3.75 3.75 0 01-2.873-1.34l-.747-.891-.039-.046.7-.86z" />
              </svg>
            </button>
            <button
              type="button"
              aria-label="Previous"
              className="hover:text-white"
            >
              <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
                <path d="M3.3 1a.7.7 0 01.7.7v5.15l9.95-5.744a.7.7 0 011.05.606v12.575a.7.7 0 01-1.05.607L4 9.149V14.3a.7.7 0 01-1.4 0V1.7a.7.7 0 01.7-.7z" />
              </svg>
            </button>
            <button
              type="button"
              aria-label="Play"
              className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-black hover:scale-105"
            >
              <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
                <path d="M3 1.713a.7.7 0 011.05-.607l10.89 6.288a.7.7 0 010 1.212L4.05 14.894A.7.7 0 013 14.287V1.713z" />
              </svg>
            </button>
            <button
              type="button"
              aria-label="Next"
              className="hover:text-white"
            >
              <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
                <path d="M12.7 1a.7.7 0 00-.7.7v5.15L2.05 1.107A.7.7 0 001 1.712v12.575a.7.7 0 001.05.607L12 9.149V14.3a.7.7 0 101.4 0V1.7a.7.7 0 00-.7-.7z" />
              </svg>
            </button>
            <button
              type="button"
              aria-label="Repeat"
              className="hover:text-white"
            >
              <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
                <path d="M0 4.75A3.75 3.75 0 013.75 1h8.5A3.75 3.75 0 0116 4.75v5a3.75 3.75 0 01-3.75 3.75H9.81l1.018 1.018a.75.75 0 11-1.06 1.06L6.939 12.75l2.829-2.828a.75.75 0 011.06 1.06L9.811 12h2.439a2.25 2.25 0 002.25-2.25v-5a2.25 2.25 0 00-2.25-2.25h-8.5A2.25 2.25 0 001.5 4.75v5A2.25 2.25 0 003.75 12H5v1.5H3.75A3.75 3.75 0 010 9.75v-5z" />
              </svg>
            </button>
          </div>

          <div className="flex w-full items-center gap-3 text-[11px] text-[#b3b3b3]">
            <span style={{ fontVariantNumeric: "tabular-nums" }}>
              {fmt(progressSeconds)}
            </span>
            <div className="relative h-1 flex-1 overflow-hidden rounded-full bg-[#4d4d4d]">
              <div
                className="absolute inset-y-0 left-0 rounded-full bg-white group-hover:bg-[#1ed760]"
                style={{
                  width: `${(progressSeconds / totalSeconds) * 100}%`,
                }}
              />
            </div>
            <span style={{ fontVariantNumeric: "tabular-nums" }}>
              {fmt(totalSeconds)}
            </span>
          </div>
        </div>

        {/* right — extras */}
        <div className="flex items-center justify-end gap-3 text-[#b3b3b3]">
          <button
            type="button"
            aria-label="Now playing view"
            className="hover:text-white"
          >
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M11.196 8L6 5v6l5.196-3z" />
              <path d="M15.002 1.75A1.75 1.75 0 0013.252 0h-10.5a1.75 1.75 0 00-1.75 1.75v12.5c0 .966.783 1.75 1.75 1.75h10.5a1.75 1.75 0 001.75-1.75V1.75zm-1.75-.25a.25.25 0 01.25.25v12.5a.25.25 0 01-.25.25h-10.5a.25.25 0 01-.25-.25V1.75a.25.25 0 01.25-.25h10.5z" />
            </svg>
          </button>
          <button type="button" aria-label="Queue" className="hover:text-white">
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M15 15H1v-1.5h14V15zm0-4.5H1V9h14v1.5zM14.5 6L9 2.5 9 9.5 14.5 6zM1 4.5h6V3H1v1.5z" />
            </svg>
          </button>
          <button type="button" aria-label="Devices" className="hover:text-white">
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M6 2.75C6 1.784 6.784 1 7.75 1h6.5c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0114.25 15h-6.5A1.75 1.75 0 016 13.25V2.75zm1.75-.25a.25.25 0 00-.25.25v10.5c0 .138.112.25.25.25h6.5a.25.25 0 00.25-.25V2.75a.25.25 0 00-.25-.25h-6.5z" />
              <path d="M3 9.5a.75.75 0 100 1.5h1a.75.75 0 100-1.5H3zm-3 0A.75.75 0 01.75 9h.75a.75.75 0 010 1.5H.75A.75.75 0 010 9.5z" />
            </svg>
          </button>

          {/* volume */}
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M9.741.85a.75.75 0 01.375.65v13a.75.75 0 01-1.125.65l-6.925-4a3.642 3.642 0 01-1.33-4.967 3.639 3.639 0 011.33-1.332l6.925-4a.75.75 0 01.75 0zm-6.924 5.3a2.139 2.139 0 000 3.7l5.8 3.35V2.8l-5.8 3.35zm8.683 4.29V5.56a2.75 2.75 0 010 4.88z" />
            </svg>
            <div className="relative h-1 w-24 overflow-hidden rounded-full bg-[#4d4d4d]">
              <div
                className="absolute inset-y-0 left-0 rounded-full bg-white"
                style={{ width: "72%" }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
