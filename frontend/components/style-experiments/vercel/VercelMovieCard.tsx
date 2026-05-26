import type { DashboardMovie } from "@/lib/types";

type Props = {
  movie: DashboardMovie;
  featured?: boolean;
};

const gradientFor = (id: string): string => {
  // pick a stable gradient pair based on movie id
  const pairs = [
    "linear-gradient(135deg,#007cf0 0%,#00dfd8 100%)",
    "linear-gradient(135deg,#7928ca 0%,#ff0080 100%)",
    "linear-gradient(135deg,#ff4d4d 0%,#f9cb28 100%)",
  ];
  const sum = [...id].reduce((s, c) => s + c.charCodeAt(0), 0);
  return pairs[sum % pairs.length];
};

const sentimentDot: Record<string, string> = {
  positive: "bg-[#50e3c2] shadow-[0_0_8px_#50e3c2]",
  negative: "bg-[#ff4d4d] shadow-[0_0_8px_#ff4d4d]",
  neutral: "bg-[#888]",
};

function formatStamp(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${mm}-${dd} ${hh}:${mi}`;
}

export default function VercelMovieCard({ movie, featured = false }: Props) {
  const pos = movie.sentiment.positive_percent;
  const neg = movie.sentiment.negative_percent;
  const grad = gradientFor(movie.movie_id);

  const surface = featured
    ? "border-[#2a2a2a] bg-[#171717]"
    : "border-[#1f1f1f] bg-[#0f0f0f]";

  return (
    <article
      className={`group relative flex flex-col overflow-hidden rounded-[12px] border ${surface} transition-colors hover:border-[#3a3a3a]`}
      style={{
        boxShadow:
          "0 1px 1px rgba(255,255,255,0.02) inset, 0 2px 2px rgba(0,0,0,0.5), 0 8px 16px -4px rgba(0,0,0,0.5)",
      }}
    >
      {/* poster header — 16:9 with gradient backdrop */}
      <div className="relative aspect-[16/9] overflow-hidden">
        <div className="absolute inset-0" style={{ background: grad }} />
        {/* noise / dotted grid */}
        <div
          aria-hidden
          className="absolute inset-0 opacity-30 mix-blend-overlay"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0)",
            backgroundSize: "16px 16px",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-tr from-black/40 via-transparent to-black/10" />

        {/* top-right status pill */}
        <div className="absolute right-4 top-4 flex items-center gap-1.5 rounded-full border border-white/20 bg-black/40 px-2.5 py-1 backdrop-blur">
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${
              movie.job_status === "completed"
                ? "bg-[#50e3c2] shadow-[0_0_6px_#50e3c2]"
                : movie.job_status === "running"
                ? "bg-[#f5a623]"
                : "bg-[#ff4d4d]"
            }`}
          />
          <span
            className="font-mono text-[11px] uppercase tracking-tight text-white/90"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            {movie.job_status ?? "queued"}
          </span>
        </div>

        {/* bottom-left title overlay */}
        <div className="absolute inset-x-0 bottom-0 p-5">
          <div
            className="font-mono text-[11px] uppercase tracking-tight text-white/70"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            {movie.source} · {movie.release_year}
          </div>
          <h3
            className="mt-1 text-white"
            style={{
              fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
              fontSize: "28px",
              fontWeight: 600,
              lineHeight: 1.05,
              letterSpacing: "-0.035em",
            }}
          >
            {movie.movie_title}.
          </h3>
        </div>
      </div>

      {/* meta band */}
      <div className="flex items-center justify-between border-y border-[#1f1f1f] bg-black/20 px-5 py-3">
        <div
          className="flex items-center gap-3 font-mono text-[11px] text-[#888]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          <span>{movie.movie_id}</span>
          <span className="text-[#333]">·</span>
          <span>{movie.review_count.toLocaleString()} reviews</span>
          <span className="text-[#333]">·</span>
          <span>{formatStamp(movie.job_completed_at)}</span>
        </div>
        <span
          className="font-mono text-[11px] uppercase tracking-tight text-[#666]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          v{movie.latest_job_id?.slice(-3) ?? "—"}
        </span>
      </div>

      {/* body */}
      <div className="flex flex-1 flex-col gap-5 p-5">
        {/* sentiment row */}
        <div>
          <div className="flex items-baseline justify-between">
            <span
              className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
              style={{ fontFamily: "var(--font-geist-mono), monospace" }}
            >
              sentiment
            </span>
            <div className="flex items-baseline gap-3">
              <span
                className="text-white"
                style={{
                  fontSize: "20px",
                  fontWeight: 600,
                  letterSpacing: "-0.03em",
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                {pos}%
              </span>
              <span className="text-[12px] text-[#666]">/ {neg}%</span>
            </div>
          </div>
          <div className="mt-2 flex h-1.5 overflow-hidden rounded-full bg-[#1a1a1a]">
            <div
              className="h-full"
              style={{
                width: `${pos}%`,
                background:
                  "linear-gradient(90deg,#007cf0 0%,#50e3c2 100%)",
              }}
            />
            <div
              className="h-full"
              style={{
                width: `${neg}%`,
                background:
                  "linear-gradient(90deg,#ff0080 0%,#f9cb28 100%)",
                opacity: 0.85,
              }}
            />
          </div>
        </div>

        {/* keywords */}
        <div>
          <span
            className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            top phrases
          </span>
          <ul className="mt-3 flex flex-col divide-y divide-[#1a1a1a]">
            {movie.top_keywords.map((kw) => (
              <li
                key={kw.rank}
                className="flex items-center justify-between py-2.5"
              >
                <div className="flex items-center gap-3">
                  <span
                    className="font-mono text-[11px] text-[#555] tabular-nums"
                    style={{ fontFamily: "var(--font-geist-mono), monospace" }}
                  >
                    0{kw.rank}
                  </span>
                  <span
                    className={`inline-block h-1.5 w-1.5 rounded-full ${
                      sentimentDot[kw.sentiment] ?? sentimentDot.neutral
                    }`}
                  />
                  <span className="text-[15px] font-medium tracking-[-0.01em] text-white">
                    {kw.label}
                  </span>
                </div>
                <span
                  className="font-mono text-[12px] tabular-nums text-[#888]"
                  style={{ fontFamily: "var(--font-geist-mono), monospace" }}
                >
                  {kw.count.toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* genre chips + cta */}
        <div className="mt-auto flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex flex-wrap gap-1.5">
            {movie.genres.map((g) => (
              <span
                key={g}
                className="rounded-full border border-[#262626] bg-[#0a0a0a] px-2 py-0.5 text-[12px] tracking-[-0.01em] text-[#a1a1a1]"
              >
                {g}
              </span>
            ))}
          </div>
          <button
            type="button"
            className="inline-flex h-9 items-center gap-1.5 rounded-full bg-white px-4 text-[13px] font-medium tracking-[-0.01em] text-black transition-transform duration-150 hover:scale-[1.03]"
          >
            View analysis
            <span aria-hidden>→</span>
          </button>
        </div>
      </div>
    </article>
  );
}
