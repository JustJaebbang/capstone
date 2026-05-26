import type { TopKeyword } from "@/lib/types";

type Props = {
  title: string;
  keywords: TopKeyword[];
};

const sentimentTone: Record<
  string,
  { dot: string; label: string; text: string }
> = {
  positive: {
    dot: "bg-[#50e3c2] shadow-[0_0_6px_#50e3c2]",
    label: "긍정",
    text: "text-[#50e3c2]",
  },
  negative: {
    dot: "bg-[#ff4d4d] shadow-[0_0_6px_#ff4d4d]",
    label: "부정",
    text: "text-[#ff4d4d]",
  },
  neutral: { dot: "bg-[#888]", label: "중립", text: "text-[#888]" },
};

export default function VercelKeywordTable({ title, keywords }: Props) {
  const max = keywords.reduce((m, k) => Math.max(m, k.count), 1);

  return (
    <section
      className="overflow-hidden rounded-[12px] border border-[#1f1f1f] bg-[#0f0f0f]"
      style={{
        boxShadow:
          "0 1px 1px rgba(255,255,255,0.02) inset, 0 1px 1px rgba(0,0,0,0.5)",
      }}
    >
      {/* header */}
      <div className="flex items-center justify-between border-b border-[#1f1f1f] px-6 py-4">
        <h3
          className="text-white"
          style={{
            fontSize: "16px",
            fontWeight: 600,
            letterSpacing: "-0.02em",
          }}
        >
          {title}
        </h3>
        <span
          className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          {keywords.length} rows
        </span>
      </div>

      {/* table header — caption-mono uppercase */}
      <div
        className="grid grid-cols-[40px_1fr_120px_84px] gap-3 border-b border-[#1f1f1f] bg-[#0a0a0a] px-6 py-2.5 font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
        style={{ fontFamily: "var(--font-geist-mono), monospace" }}
      >
        <span>#</span>
        <span>phrase</span>
        <span>sentiment</span>
        <span className="text-right">count</span>
      </div>

      {/* rows */}
      <ul>
        {keywords.map((kw) => {
          const tone = sentimentTone[kw.sentiment] ?? sentimentTone.neutral;
          const width = (kw.count / max) * 100;
          return (
            <li
              key={`${kw.rank}-${kw.label}`}
              className="relative border-b border-[#1a1a1a] last:border-b-0"
            >
              {/* bar fill behind */}
              <div
                aria-hidden
                className="absolute inset-y-0 left-0 -z-0 bg-gradient-to-r from-white/[0.025] to-transparent"
                style={{ width: `${width}%` }}
              />
              <div className="relative grid grid-cols-[40px_1fr_120px_84px] items-center gap-3 px-6 py-3">
                <span
                  className="font-mono text-[12px] tabular-nums text-[#666]"
                  style={{ fontFamily: "var(--font-geist-mono), monospace" }}
                >
                  0{kw.rank}
                </span>
                <span className="text-[15px] font-medium tracking-[-0.01em] text-white">
                  {kw.label}
                </span>
                <span className="flex items-center gap-1.5">
                  <span
                    className={`inline-block h-1.5 w-1.5 rounded-full ${tone.dot}`}
                  />
                  <span className={`text-[13px] font-medium ${tone.text}`}>
                    {tone.label}
                  </span>
                </span>
                <span
                  className="text-right font-mono text-[13px] tabular-nums text-[#ededed]"
                  style={{ fontFamily: "var(--font-geist-mono), monospace" }}
                >
                  {kw.count.toLocaleString()}
                </span>
              </div>
            </li>
          );
        })}
      </ul>

      {/* footer */}
      <div className="flex items-center justify-between border-t border-[#1f1f1f] bg-[#0a0a0a] px-6 py-3">
        <span
          className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          source · llm + hdbscan
        </span>
        <button
          type="button"
          className="text-[13px] font-medium tracking-[-0.01em] text-[#0070f3] hover:underline"
        >
          View all keywords →
        </button>
      </div>
    </section>
  );
}
