import type { DashboardMovie } from "@/lib/types";

type Props = {
  movie: DashboardMovie;
  index: number; // 0-based, used for "FILM // 01" badge
};

function formatStamp(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  const yy = String(d.getFullYear()).slice(2);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${yy}.${mm}.${dd}/${hh}:${mi}`;
}

const sentimentTag: Record<string, string> = {
  positive: "bg-[#0a0a0a] text-[#FFE600]",
  negative: "bg-[#FF3B00] text-white",
  neutral: "bg-white text-[#0a0a0a]",
};

export default function BrutalMovieBlock({ movie, index }: Props) {
  const pos = movie.sentiment.positive_percent;
  const neg = movie.sentiment.negative_percent;

  return (
    <article
      className="group relative grid grid-cols-1 border-[3px] border-[#0a0a0a] bg-[#ece6d6] md:grid-cols-[260px_1fr]"
      style={{ boxShadow: "10px 10px 0 0 #0a0a0a" }}
    >
      {/* === poster column === */}
      <div className="relative border-b-[3px] border-[#0a0a0a] bg-[#0a0a0a] md:border-b-0 md:border-r-[3px]">
        {/* corner index */}
        <div className="absolute left-3 top-3 z-10 border-2 border-[#FFE600] bg-[#0a0a0a] px-2 py-0.5 font-mono text-[10px] tracking-widest text-[#FFE600]">
          FILM // {String(index + 1).padStart(2, "0")}
        </div>

        <div className="relative flex h-[260px] items-center justify-center overflow-hidden">
          {/* hatched background */}
          <div
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage:
                "repeating-linear-gradient(45deg, transparent 0 10px, rgba(255,230,0,0.25) 10px 12px)",
            }}
          />
          {/* concentric brutal frame */}
          <div className="absolute inset-4 border-2 border-[#FFE600]/40" />
          <div className="absolute inset-8 border border-dashed border-[#FFE600]/30" />

          <div className="relative z-10 flex flex-col items-center px-3 text-center">
            <span className="font-mono text-[10px] tracking-[0.35em] text-[#FFE600]/80">
              POSTER · NOT_FOUND
            </span>
            <span className="mt-3 font-display-kr text-[34px] leading-[0.95] text-white">
              {movie.movie_title}
            </span>
            <span className="mt-2 font-mono text-[10px] tracking-widest text-[#ece6d6]/60">
              {movie.release_year} / {movie.source.toUpperCase()}
            </span>
          </div>
        </div>

        {/* footer ribbon */}
        <div className="flex items-center justify-between border-t-2 border-[#FFE600]/50 bg-[#0a0a0a] px-3 py-1.5 font-mono text-[10px] tracking-widest text-[#FFE600]">
          <span>ID ▸ {movie.movie_id}</span>
          <span>{movie.is_active ? "● ACTIVE" : "○ DORMANT"}</span>
        </div>
      </div>

      {/* === content column === */}
      <div className="flex flex-col">
        {/* head strip */}
        <header className="flex flex-wrap items-end justify-between gap-3 border-b-[3px] border-[#0a0a0a] bg-white px-5 py-4">
          <div>
            <p className="font-mono text-[10px] tracking-[0.3em] uppercase text-[#0a0a0a]/60">
              CASE FILE · {movie.genres.join(" / ")}
            </p>
            <h2 className="font-display-kr mt-1 text-4xl leading-none text-[#0a0a0a]">
              {movie.movie_title}
            </h2>
          </div>

          <div className="flex flex-col items-end gap-1">
            <span className="border-2 border-[#0a0a0a] bg-[#FFE600] px-2 py-0.5 font-mono text-[10px] tracking-widest uppercase">
              {movie.job_status ?? "—"}
            </span>
            <span className="font-mono text-[10px] tracking-widest text-[#0a0a0a]/60">
              STAMP ▸ {formatStamp(movie.job_completed_at)}
            </span>
          </div>
        </header>

        {/* sentiment row */}
        <div className="grid grid-cols-[1fr_auto] border-b-[3px] border-[#0a0a0a]">
          <div className="flex h-[70px]">
            <div
              className="flex items-center justify-start bg-[#0a0a0a] px-4 text-[#FFE600]"
              style={{ width: `${pos}%` }}
            >
              <span className="font-display text-4xl leading-none">{pos}</span>
              <span className="ml-2 font-mono text-[10px] tracking-widest">
                % POS
              </span>
            </div>
            <div
              className="flex items-center justify-start bg-[#FF3B00] px-4 text-white"
              style={{ width: `${neg}%` }}
            >
              <span className="font-display text-3xl leading-none">{neg}</span>
              <span className="ml-2 font-mono text-[10px] tracking-widest">
                % NEG
              </span>
            </div>
          </div>
          <div className="flex items-center justify-center border-l-[3px] border-[#0a0a0a] bg-[#ece6d6] px-4 font-mono text-[10px] tracking-widest uppercase">
            N = {movie.review_count.toLocaleString()}
          </div>
        </div>

        {/* keywords table */}
        <div className="flex-1 bg-white">
          <div className="flex items-center justify-between border-b border-dashed border-[#0a0a0a] px-5 py-2 font-mono text-[10px] tracking-[0.25em] uppercase">
            <span>▣ TOP PHRASES</span>
            <span>SOURCE ▸ LLM + HDBSCAN</span>
          </div>
          <ul>
            {movie.top_keywords.map((kw) => (
              <li
                key={kw.rank}
                className="grid grid-cols-[44px_1fr_auto_60px] items-center gap-3 border-b border-dashed border-[#0a0a0a]/60 px-5 py-2 last:border-b-0"
              >
                <span className="font-mono text-[11px] tracking-widest text-[#0a0a0a]/60">
                  #{String(kw.rank).padStart(2, "0")}
                </span>
                <span className="font-display-kr text-xl leading-none text-[#0a0a0a]">
                  {kw.label}
                </span>
                <span
                  className={`border-2 border-[#0a0a0a] px-1.5 py-0.5 font-mono text-[10px] tracking-widest ${
                    sentimentTag[kw.sentiment] ?? sentimentTag.neutral
                  }`}
                >
                  {kw.sentiment.toUpperCase()}
                </span>
                <span className="text-right font-mono text-[11px] tracking-wider">
                  {kw.count.toLocaleString()}×
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* footer */}
        <footer className="grid grid-cols-1 border-t-[3px] border-[#0a0a0a] sm:grid-cols-[1fr_auto]">
          <div className="flex flex-wrap items-center gap-x-5 gap-y-1 bg-[#ece6d6] px-5 py-3 font-mono text-[10px] tracking-[0.2em] uppercase text-[#0a0a0a]/80">
            <span>RELEASE ▸ {movie.release_date ?? "—"}</span>
            <span>SOURCE ▸ {movie.source}</span>
            {movie.notes && <span>NOTE ▸ {movie.notes}</span>}
          </div>
          <button
            type="button"
            className="group/btn relative flex items-center justify-center gap-2 border-l-[3px] border-[#0a0a0a] bg-[#FFE600] px-7 py-3 font-display text-sm tracking-[0.2em] uppercase text-[#0a0a0a] transition-transform duration-150 hover:-translate-x-[2px] hover:-translate-y-[2px]"
            style={{ boxShadow: "inset 0 0 0 0 #0a0a0a" }}
          >
            <span>RUN ANALYSIS</span>
            <span aria-hidden className="text-lg leading-none">▸▸</span>
          </button>
        </footer>
      </div>
    </article>
  );
}
