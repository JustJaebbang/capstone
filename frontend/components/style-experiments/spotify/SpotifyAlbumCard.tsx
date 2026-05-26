import type { DashboardMovie } from "@/lib/types";

type Props = {
  movie: DashboardMovie;
};

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

export default function SpotifyAlbumCard({ movie }: Props) {
  const pos = movie.sentiment.positive_percent;

  return (
    <a
      href={`#movie-${movie.movie_id}`}
      className="group relative flex flex-col gap-3 rounded-md bg-[#181818] p-4 transition-colors duration-200 hover:bg-[#1f1f1f]"
    >
      {/* cover */}
      <div
        className="relative aspect-square overflow-hidden rounded-md"
        style={{
          background: gradientFor(movie.movie_id),
          boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
        }}
      >
        {/* glyph noise */}
        <div
          aria-hidden
          className="absolute inset-0 opacity-30 mix-blend-overlay"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0)",
            backgroundSize: "12px 12px",
          }}
        />

        {/* big title — like a generated playlist cover */}
        <div className="absolute inset-0 flex flex-col justify-end p-4">
          <p
            className="text-[10.5px] uppercase text-white/80"
            style={{ fontWeight: 600, letterSpacing: "0.06em" }}
          >
            Album · {movie.release_year}
          </p>
          <p
            className="mt-1 text-[20px] leading-[1.05] text-white"
            style={{
              fontWeight: 700,
              letterSpacing: "-0.02em",
            }}
          >
            {movie.movie_title}.
          </p>
        </div>

        {/* play button — appears on hover */}
        <button
          type="button"
          aria-label={`Play ${movie.movie_title}`}
          className="absolute bottom-3 right-3 flex h-12 w-12 translate-y-3 items-center justify-center rounded-full text-black opacity-0 transition-all duration-200 group-hover:translate-y-0 group-hover:opacity-100"
          style={{
            background: "#1ed760",
            boxShadow: "rgba(0,0,0,0.5) 0px 8px 24px",
          }}
        >
          <svg
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden
            className="h-5 w-5"
          >
            <path d="M7.05 3.606l13.49 7.788a.7.7 0 010 1.212L7.05 20.394A.7.7 0 016 19.788V4.212a.7.7 0 011.05-.606z" />
          </svg>
        </button>
      </div>

      {/* meta */}
      <div className="min-w-0">
        <p
          className="truncate text-[16px] text-white"
          style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
        >
          {movie.movie_title}
        </p>
        <p className="mt-1 line-clamp-2 text-[14px] text-[#b3b3b3]">
          <span style={{ color: "#1ed760", fontWeight: 700 }}>{pos}%</span>{" "}
          positive · {movie.review_count.toLocaleString()} reviews ·{" "}
          {movie.genres.join(", ")}
        </p>
      </div>
    </a>
  );
}
