type SentimentRatioProps = {
  positivePercent: number;
  negativePercent: number;
};

export default function SentimentRatio({
  positivePercent,
  negativePercent,
}: SentimentRatioProps) {
  return (
    <div className="rounded-[10px] border border-[#e8e3d6] bg-white p-7">
      <h2 className="font-serif text-[20px] font-medium text-[#161616]">
        긍정 / 부정 비율
      </h2>

      <div className="mt-6">
        <div className="mb-3 flex items-baseline justify-between">
          <span className="flex items-baseline gap-1.5">
            <span className="font-serif text-[22px] font-medium leading-none text-[#ff2c63] tabular-nums">
              {positivePercent}
            </span>
            <span className="font-serif text-[13px] text-[#ff2c63]/75">%</span>
            <span className="ml-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
              호감
            </span>
          </span>
          <span className="flex items-baseline gap-1.5">
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
              비호감
            </span>
            <span className="font-serif text-[22px] font-medium leading-none text-[#6b6760] tabular-nums">
              {negativePercent}
            </span>
            <span className="font-serif text-[13px] text-[#6b6760]/75">%</span>
          </span>
        </div>

        <div className="flex h-[6px] w-full overflow-hidden rounded-full bg-[#efe9d8]">
          <div
            className="h-full bg-[#ff2c63]"
            style={{ width: `${positivePercent}%` }}
            aria-label={`긍정 ${positivePercent}%`}
          />
          <div
            className="h-full bg-[#c4bcab]"
            style={{ width: `${negativePercent}%` }}
            aria-label={`부정 ${negativePercent}%`}
          />
        </div>
      </div>
    </div>
  );
}