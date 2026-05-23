import Link from "next/link";
import type { DashboardMovie } from "@/lib/types";

// Deterministic poster gradient — moody, film-still palette
const palettes: Array<[string, string, string]> = [
  ["#1a1424", "#3b1a3f", "#0d0810"], // plum/midnight
  ["#0e1f1c", "#1e3f3a", "#070f0d"], // forest/ink
  ["#2a1a14", "#5a2a1a", "#180a05"], // umber/coffee
  ["#0d172a", "#1e2a4a", "#05080f"], // deep ocean
  ["#2a1010", "#4a1a1a", "#0f0404"], // garnet
  ["#1f1d2c", "#3a2a44", "#0a0a14"], // dusk
];

function gradientFor(id: string): string {
  let s = 0;
  for (let i = 0; i < id.length; i++) {
    s = (s * 31 + id.charCodeAt(i)) >>> 0;
  }
  const [a, b, c] = palettes[s % palettes.length];
  return `radial-gradient(120% 80% at 20% 0%, ${a} 0%, ${b} 55%, ${c} 100%)`;
}

type Props = {
  movie: DashboardMovie;
  rank?: number;
};

export default function WatchaPosterCard({ movie, rank }: Props) {
  const grad = gradientFor(movie.movie_id);
  const top = movie.top_keywords.slice(0, 3);
  const pos = movie.sentiment.positive_percent;

  return (
    <Link
      href={`/movies/${movie.movie_id}/analyzing`}
      className="group block"
    >
      {/* Poster */}
      <div
        className="relative aspect-[2/3] w-full overflow-hidden rounded-[6px] shadow-[0_2px_10px_-3px_rgba(20,15,5,0.22)] transition-transform duration-500 ease-out group-hover:-translate-y-1 group-hover:shadow-[0_18px_36px_-12px_rgba(20,15,5,0.35)]"
        style={{ background: grad }}
      >
        {/* faux poster typography */}
        <div className="absolute inset-0 flex flex-col justify-between p-5">
          <div className="flex items-start justify-between">
            {rank !== undefined ? (
              <span className="font-serif text-[44px] italic leading-none text-white/75 tabular-nums">
                {String(rank).padStart(2, "0")}
              </span>
            ) : (
              <span />
            )}
            <span className="rounded-full bg-white/10 px-2 py-0.5 font-mono text-[9.5px] font-medium uppercase tracking-[0.18em] text-white/80 backdrop-blur">
              {movie.source}
            </span>
          </div>

          <div>
            <p className="font-mono text-[9.5px] uppercase tracking-[0.22em] text-white/55">
              {movie.release_year}
              {movie.genres[0] ? ` · ${movie.genres[0]}` : ""}
            </p>
            <h3 className="mt-2 font-serif text-[28px] font-medium leading-[1.04] tracking-tight text-white">
              {movie.movie_title}
            </h3>
          </div>
        </div>

        {/* score chip — Watcha-style */}
        <div className="absolute right-3 top-3 hidden md:block">
          {/* intentionally empty — primary score rendered below in editorial slot */}
        </div>

        {/* Hover overlay — reveals keywords */}
        <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-[#0a0507]/92 via-[#0a0507]/55 to-transparent p-5 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          <p className="font-mono text-[9.5px] uppercase tracking-[0.22em] text-white/55">
            관객 의견 · top 3
          </p>
          <ul className="mt-3 space-y-2">
            {top.map((k) => (
              <li
                key={k.rank}
                className="flex items-center justify-between gap-3 border-b border-white/10 pb-2 last:border-b-0 last:pb-0"
              >
                <span className="font-serif text-[18px] font-medium leading-none text-white">
                  <span className="mr-1.5 text-white/40 tabular-nums">
                    {k.rank}.
                  </span>
                  {k.label}
                </span>
                <span
                  className={`font-mono text-[10px] tabular-nums ${
                    k.sentiment === "positive"
                      ? "text-[#ff8aa9]"
                      : k.sentiment === "negative"
                      ? "text-[#88c5d8]"
                      : "text-white/55"
                  }`}
                >
                  {k.count.toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.22em] text-white/45">
            분석 페이지로 이동 →
          </p>
        </div>
      </div>

      {/* Meta — Watcha-style score block */}
      <div className="mt-4 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate font-serif text-[18px] font-medium leading-tight tracking-tight text-[#161616] transition-colors group-hover:text-[#ff2c63]">
            {movie.movie_title}
          </h3>
          <p className="mt-1 text-[12.5px] leading-tight text-[#6b6760]">
            {movie.release_year} · {movie.genres.join(" / ")}
          </p>
        </div>
        <div className="text-right">
          <div className="flex items-baseline justify-end gap-0.5">
            <span className="font-serif text-[24px] font-medium leading-none text-[#ff2c63] tabular-nums">
              {pos}
            </span>
            <span className="font-serif text-[14px] font-medium text-[#ff2c63]/75">
              %
            </span>
          </div>
          <p className="mt-0.5 font-mono text-[9.5px] uppercase tracking-[0.18em] text-[#9a958b]">
            평균 호감
          </p>
        </div>
      </div>

      {/* Sentiment bar */}
      <div className="mt-3 flex h-[3px] w-full overflow-hidden rounded-full bg-[#efe9d8]">
        <div
          className="h-full bg-[#ff2c63]"
          style={{ width: `${pos}%` }}
          aria-label={`긍정 ${pos}%`}
        />
      </div>
      <div className="mt-2 flex items-center justify-between font-mono text-[10px] tracking-tight text-[#9a958b]">
        <span>리뷰 {movie.review_count.toLocaleString()}</span>
        <span className="uppercase tracking-[0.18em]">
          ♡ {top[0]?.label ?? "—"}
        </span>
      </div>
    </Link>
  );
}
