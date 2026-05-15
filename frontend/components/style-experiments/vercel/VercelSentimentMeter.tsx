type Props = {
  positivePercent: number;
  negativePercent: number;
  totalReviews: number;
};

export default function VercelSentimentMeter({
  positivePercent,
  negativePercent,
  totalReviews,
}: Props) {
  return (
    <div
      className="rounded-[12px] border border-[#1f1f1f] bg-[#0f0f0f] p-8"
      style={{
        boxShadow:
          "0 1px 1px rgba(255,255,255,0.02) inset, 0 1px 1px rgba(0,0,0,0.6), 0 8px 16px -4px rgba(0,0,0,0.6)",
      }}
    >
      {/* top row */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <span
            className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#888]"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            sentiment.overall
          </span>
          <div className="mt-2 flex items-baseline gap-4">
            <span
              className="text-white"
              style={{
                fontSize: "56px",
                lineHeight: 1,
                fontWeight: 600,
                letterSpacing: "-0.045em",
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {positivePercent}
              <span className="text-[28px] font-medium text-[#666]">%</span>
            </span>
            <span className="pb-1.5 text-[14px] tracking-[-0.01em] text-[#a1a1a1]">
              긍정 / positive
            </span>
          </div>
        </div>

        <div className="text-right">
          <span
            className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#888]"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            sample size
          </span>
          <div
            className="mt-2 text-white"
            style={{
              fontSize: "24px",
              fontWeight: 600,
              letterSpacing: "-0.04em",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {totalReviews.toLocaleString()}
            <span className="ml-1 text-[14px] font-medium text-[#666]">
              reviews
            </span>
          </div>
        </div>
      </div>

      {/* the bar */}
      <div className="relative mt-8">
        <div className="relative h-3 overflow-hidden rounded-full bg-[#1a1a1a]">
          <div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{
              width: `${positivePercent}%`,
              background:
                "linear-gradient(90deg, #007cf0 0%, #00dfd8 50%, #50e3c2 100%)",
              boxShadow: "0 0 16px rgba(0, 223, 216, 0.35)",
            }}
          />
          <div
            className="absolute inset-y-0 rounded-full"
            style={{
              left: `${positivePercent}%`,
              width: `${negativePercent}%`,
              background:
                "linear-gradient(90deg, #ff0080 0%, #ff4d4d 70%, #f9cb28 100%)",
              opacity: 0.85,
            }}
          />
          {/* divider */}
          <div
            className="absolute inset-y-0 w-px bg-[#0a0a0a]"
            style={{ left: `${positivePercent}%` }}
          />
        </div>

        {/* tick row */}
        <div className="mt-2 flex justify-between">
          {[0, 25, 50, 75, 100].map((t) => (
            <span
              key={t}
              className="font-mono text-[10px] text-[#666]"
              style={{ fontFamily: "var(--font-geist-mono), monospace" }}
            >
              {t}%
            </span>
          ))}
        </div>
      </div>

      {/* legend */}
      <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2">
        <span className="flex items-center gap-2 text-[13px] text-[#ededed]">
          <span
            className="inline-block h-2 w-3 rounded-sm"
            style={{ background: "linear-gradient(90deg,#007cf0,#00dfd8)" }}
          />
          <span className="font-medium">긍정</span>
          <span
            className="font-mono tracking-tight text-[#666]"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            {positivePercent}%
          </span>
        </span>
        <span className="flex items-center gap-2 text-[13px] text-[#ededed]">
          <span
            className="inline-block h-2 w-3 rounded-sm"
            style={{ background: "linear-gradient(90deg,#ff0080,#f9cb28)" }}
          />
          <span className="font-medium">부정</span>
          <span
            className="font-mono tracking-tight text-[#666]"
            style={{ fontFamily: "var(--font-geist-mono), monospace" }}
          >
            {negativePercent}%
          </span>
        </span>
        <span
          className="ml-auto font-mono text-[11px] text-[#666]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          method: hdbscan + rule-based extract
        </span>
      </div>
    </div>
  );
}
