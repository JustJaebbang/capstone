import Link from "next/link";
import type { ReactNode } from "react";
import type { DashboardMovie } from "@/lib/types";

const palettes: Array<[string, string, string]> = [
  ["#1a1424", "#3b1a3f", "#0d0810"],
  ["#0e1f1c", "#1e3f3a", "#070f0d"],
  ["#2a1a14", "#5a2a1a", "#180a05"],
  ["#0d172a", "#1e2a4a", "#05080f"],
  ["#2a1010", "#4a1a1a", "#0f0404"],
  ["#1f1d2c", "#3a2a44", "#0a0a14"],
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
  /**
   * - `string`: render as a Link.
   * - `null`: render disabled (no analysis result yet).
   */
  href: string | null;
};

function PosterBlock({ movie }: { movie: DashboardMovie }) {
  if (movie.poster_url) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={movie.poster_url}
        alt={movie.movie_title}
        className="absolute inset-0 h-full w-full object-cover"
      />
    );
  }

  return (
    <div
      className="absolute inset-0"
      style={{ background: gradientFor(movie.movie_id) }}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.18] mix-blend-overlay"
        style={{
          backgroundImage:
            "radial-gradient(rgba(255,255,255,0.6) 1px, transparent 1px)",
          backgroundSize: "3px 3px",
        }}
      />
    </div>
  );
}

export default function WatchaMovieRow({ movie, href }: Props) {
  const disabled = href === null;
  const pos = movie.sentiment.positive_percent;
  const top = movie.top_keywords.slice(0, 3);

  const Wrapper = ({ children }: { children: ReactNode }) =>
    disabled ? (
      <div
        className="group block cursor-not-allowed"
        aria-disabled="true"
        title="아직 분석 결과가 없습니다"
      >
        {children}
      </div>
    ) : (
      <Link href={href as string} className="group block">
        {children}
      </Link>
    );

  return (
    <Wrapper>
      <article
        className={`relative grid grid-cols-[1fr_auto] gap-6 rounded-[8px] border border-[#e8e3d6] bg-white p-5 transition-all duration-300 ${
          disabled
            ? "opacity-70"
            : "hover:-translate-y-0.5 hover:border-[#dcd6c5] hover:shadow-[0_18px_36px_-22px_rgba(20,15,5,0.22)]"
        }`}
      >
        {/* Left — meta (title / sentiment / review count / keywords) */}
        <div className="flex min-w-0 flex-col">
          <h3
            className={`truncate font-serif text-[26px] font-medium leading-tight tracking-[-0.01em] text-[#161616] transition-colors sm:text-[28px] ${
              disabled ? "" : "group-hover:text-[#ff2c63]"
            }`}
          >
            {movie.movie_title}
          </h3>

          <div className="mt-5">
            <div className="flex items-baseline justify-between gap-3">
              <div className="flex items-baseline gap-1">
                <span className="font-serif text-[28px] font-medium leading-none text-[#ff2c63] tabular-nums">
                  {pos}
                </span>
                <span className="font-serif text-[15px] font-medium text-[#ff2c63]/75">
                  %
                </span>
                <span className="ml-2 font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                  호감
                </span>
              </div>
              <span className="font-mono text-[11px] tracking-tight text-[#6b6760] tabular-nums">
                리뷰 {movie.review_count.toLocaleString()}
              </span>
            </div>
            <div className="mt-2 flex h-[3px] w-full overflow-hidden rounded-full bg-[#efe9d8]">
              <div
                className="h-full bg-[#ff2c63]"
                style={{ width: `${pos}%` }}
                aria-label={`긍정 ${pos}%`}
              />
            </div>
          </div>

          {top.length > 0 && (
            <ul className="mt-auto flex flex-wrap gap-1.5 pt-5">
              {top.map((k) => (
                <li
                  key={k.rank}
                  className="inline-flex items-baseline gap-1.5 rounded-full border border-[#e8e3d6] bg-[#fbf9f3] px-2.5 py-1"
                >
                  <span className="font-mono text-[9.5px] uppercase tracking-[0.18em] text-[#9a958b] tabular-nums">
                    {String(k.rank).padStart(2, "0")}
                  </span>
                  <span className="font-serif text-[13.5px] font-medium leading-none text-[#161616]">
                    {k.label}
                  </span>
                  <span
                    className={`font-mono text-[10px] tabular-nums ${
                      k.sentiment === "positive"
                        ? "text-[#ff2c63]"
                        : k.sentiment === "negative"
                        ? "text-[#0f4c5c]"
                        : "text-[#9a958b]"
                    }`}
                  >
                    {k.count.toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Right — poster (2:3) */}
        <div className="relative aspect-[2/3] w-[120px] shrink-0 self-start overflow-hidden rounded-[6px] shadow-[0_2px_10px_-3px_rgba(20,15,5,0.22)] sm:w-[140px]">
          <PosterBlock movie={movie} />

          {disabled && (
            <div className="pointer-events-none absolute inset-x-0 top-1/2 z-10 -translate-y-1/2 px-2 text-center">
              <span className="inline-block rounded-full bg-black/55 px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.18em] text-white/85 backdrop-blur">
                결과 없음
              </span>
            </div>
          )}
        </div>
      </article>
    </Wrapper>
  );
}
