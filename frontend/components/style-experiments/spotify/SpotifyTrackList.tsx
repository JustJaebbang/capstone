import type { TopKeyword } from "@/lib/types";

type Props = {
  keywords: TopKeyword[];
};

const sentimentBadge: Record<
  string,
  { dot: string; label: string; tone: string }
> = {
  positive: {
    dot: "bg-[#1ed760] shadow-[0_0_6px_#1ed760]",
    label: "긍정",
    tone: "text-[#1ed760]",
  },
  negative: {
    dot: "bg-[#f3727f] shadow-[0_0_6px_#f3727f]",
    label: "부정",
    tone: "text-[#f3727f]",
  },
  neutral: {
    dot: "bg-[#b3b3b3]",
    label: "중립",
    tone: "text-[#b3b3b3]",
  },
};

// "play count" — a Spotify-style number with thousands grouping
function plays(count: number): string {
  return count.toLocaleString();
}

// fake a "duration" from the count to keep the track-list pattern intact
function durationFromCount(count: number): string {
  const seconds = Math.max(60, Math.min(420, Math.round(count / 5)));
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export default function SpotifyTrackList({ keywords }: Props) {
  return (
    <div className="px-8">
      {/* header */}
      <div
        className="sticky top-[64px] z-10 mb-1 grid grid-cols-[40px_1fr_180px_140px_80px] items-center gap-4 border-b border-[#282828] px-4 py-2 text-[12px] uppercase text-[#b3b3b3]"
        style={{
          fontWeight: 400,
          letterSpacing: "0.08em",
        }}
      >
        <span className="text-right">#</span>
        <span>Title</span>
        <span>Sentiment</span>
        <span className="text-right">Plays</span>
        <span className="flex justify-end">
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z" />
            <path d="M8 3.25a.75.75 0 01.75.75v3.69l2.28 2.28a.75.75 0 11-1.06 1.06L7.25 8.31V4a.75.75 0 01.75-.75z" />
          </svg>
        </span>
      </div>

      <ol>
        {keywords.map((kw) => {
          const badge =
            sentimentBadge[kw.sentiment] ?? sentimentBadge.neutral;
          return (
            <li
              key={`${kw.rank}-${kw.label}`}
              className="group grid grid-cols-[40px_1fr_180px_140px_80px] items-center gap-4 rounded-md px-4 py-2 hover:bg-white/[0.06]"
            >
              {/* rank / play */}
              <span className="relative text-right text-[16px] text-[#b3b3b3]">
                <span className="group-hover:hidden">{kw.rank}</span>
                <span className="absolute inset-0 hidden items-center justify-end pr-0.5 text-white group-hover:flex">
                  <svg
                    viewBox="0 0 16 16"
                    fill="currentColor"
                    aria-hidden
                    className="h-3.5 w-3.5"
                  >
                    <path d="M3 1.713a.7.7 0 011.05-.607l10.89 6.288a.7.7 0 010 1.212L4.05 14.894A.7.7 0 013 14.287V1.713z" />
                  </svg>
                </span>
              </span>

              {/* title (phrase) */}
              <div className="flex min-w-0 items-center gap-3">
                <span
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-sm text-[11px] uppercase text-white"
                  style={{
                    background:
                      kw.sentiment === "positive"
                        ? "linear-gradient(135deg, #1db954 0%, #053e1e 100%)"
                        : kw.sentiment === "negative"
                        ? "linear-gradient(135deg, #f3727f 0%, #4c0519 100%)"
                        : "linear-gradient(135deg, #4d4d4d 0%, #1f1f1f 100%)",
                    fontWeight: 700,
                    letterSpacing: "0.04em",
                  }}
                >
                  {String(kw.rank).padStart(2, "0")}
                </span>
                <div className="min-w-0">
                  <p
                    className="truncate text-[16px] text-white"
                    style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
                  >
                    {kw.label}
                  </p>
                  <p className="truncate text-[12px] text-[#b3b3b3]">
                    review.os · top opinions
                  </p>
                </div>
              </div>

              {/* sentiment as "album" */}
              <span className={`flex items-center gap-2 text-[14px] ${badge.tone}`}>
                <span className={`inline-block h-1.5 w-1.5 rounded-full ${badge.dot}`} />
                {badge.label} cluster
              </span>

              {/* plays */}
              <span
                className="text-right text-[14px] text-[#b3b3b3]"
                style={{ fontVariantNumeric: "tabular-nums" }}
              >
                {plays(kw.count)}
              </span>

              {/* duration */}
              <span
                className="text-right text-[14px] text-[#b3b3b3]"
                style={{ fontVariantNumeric: "tabular-nums" }}
              >
                {durationFromCount(kw.count)}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
