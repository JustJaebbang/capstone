type Props = {
  positivePercent: number;
  negativePercent: number;
  totalReviews?: number;
  title?: string;
};

export default function BrutalSentimentBar({
  positivePercent,
  negativePercent,
  totalReviews,
  title = "SENTIMENT SPLIT — RAW",
}: Props) {
  return (
    <section
      className="border-[3px] border-[#0a0a0a] bg-white"
      style={{ boxShadow: "10px 10px 0 0 #0a0a0a" }}
    >
      {/* heading strip */}
      <div className="flex items-center justify-between border-b-[3px] border-[#0a0a0a] bg-[#0a0a0a] px-4 py-2 font-mono text-[11px] tracking-[0.25em] uppercase text-[#ece6d6]">
        <span>◼ {title}</span>
        <span className="text-[#FFE600]">FEED: GLOBAL</span>
      </div>

      {/* the bar */}
      <div className="relative">
        <div className="flex h-[120px]">
          {/* positive */}
          <div
            className="relative flex items-end border-r-[3px] border-[#0a0a0a] bg-[#0a0a0a] text-[#ece6d6]"
            style={{ width: `${positivePercent}%` }}
          >
            <div className="absolute inset-0 opacity-20"
              style={{
                backgroundImage:
                  "repeating-linear-gradient(135deg, transparent 0 8px, rgba(255,230,0,0.5) 8px 10px)",
              }}
            />
            <div className="relative flex items-end gap-3 px-5 pb-3">
              <span
                className="font-display leading-none"
                style={{ fontSize: "clamp(48px, 7vw, 96px)" }}
              >
                {positivePercent}
              </span>
              <span className="pb-2 font-mono text-xs tracking-widest uppercase">
                % POS / 긍정
              </span>
            </div>
          </div>

          {/* negative */}
          <div
            className="relative flex items-end bg-[#FFE600] text-[#0a0a0a]"
            style={{ width: `${negativePercent}%` }}
          >
            <div className="absolute inset-0"
              style={{
                backgroundImage:
                  "repeating-linear-gradient(135deg, transparent 0 8px, rgba(10,10,10,0.18) 8px 10px)",
              }}
            />
            <div className="relative flex items-end gap-3 px-5 pb-3">
              <span
                className="font-display leading-none"
                style={{ fontSize: "clamp(40px, 6vw, 80px)" }}
              >
                {negativePercent}
              </span>
              <span className="pb-2 font-mono text-xs tracking-widest uppercase">
                % NEG / 부정
              </span>
            </div>
          </div>
        </div>

        {/* tick ruler */}
        <div className="flex border-t-[3px] border-[#0a0a0a] bg-[#ece6d6] font-mono text-[10px] tracking-[0.2em] uppercase text-[#0a0a0a]">
          {Array.from({ length: 11 }).map((_, i) => (
            <div
              key={i}
              className="flex flex-1 items-center justify-start border-r border-dashed border-[#0a0a0a]/40 px-1.5 py-1 last:border-r-0"
            >
              {i * 10}
            </div>
          ))}
        </div>
      </div>

      {/* footer */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t-[3px] border-[#0a0a0a] px-4 py-2 font-mono text-[10px] tracking-[0.22em] uppercase">
        <span>N={totalReviews?.toLocaleString() ?? "—"} REVIEWS</span>
        <span>METHOD ▸ HDBSCAN + RULE-BASED EXTRACT</span>
        <span>STATE ▸ STABLE</span>
      </div>
    </section>
  );
}
