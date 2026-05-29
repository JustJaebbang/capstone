import type { ElementScore } from "@/lib/types";

type Props = {
  scores: ElementScore[];
  totalReviewCount?: number | null;
};

function barColor(score: number | null): string {
  if (score === null) return "bg-[#e8e3d6]";
  if (score >= 85) return "bg-[#ff2c63]";
  if (score >= 70) return "bg-[#ff2c63]/75";
  if (score >= 55) return "bg-[#ff2c63]/55";
  return "bg-[#ff2c63]/35";
}

function scoreInkColor(score: number | null): string {
  if (score === null) return "text-[#9a958b]";
  if (score >= 70) return "text-[#ff2c63]";
  return "text-[#161616]";
}

export default function ElementScoreChart({
  scores,
  totalReviewCount,
}: Props) {
  const hasScores = scores.length > 0;
  const reviewCountLabel =
    totalReviewCount === undefined || totalReviewCount === null
      ? "-"
      : `${totalReviewCount.toLocaleString()}개`;

  return (
    <div className="rounded-[10px] border border-[#e8e3d6] bg-white p-7">
      <div className="flex items-baseline justify-between">
        <h2 className="font-serif text-[20px] font-medium text-[#161616]">영화 요소별 점수</h2>
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">0–100점</span>
      </div>

      {hasScores ? (
        <ul className="mt-5 space-y-3.5">
          {scores.map((s) => {
            const hasScore = s.score !== null;
            const clamped = hasScore
              ? Math.max(0, Math.min(100, s.score as number))
              : 0;
            return (
              <li
                key={s.element}
                className="grid grid-cols-[64px_1fr_72px] items-center gap-3"
              >
                <span className="font-serif text-[15px] font-medium text-[#161616]">
                  {s.element}
                </span>
                <div
                  className="h-2.5 overflow-hidden rounded-full bg-[#efe9d8]"
                  role="progressbar"
                  aria-label={`${s.element} 점수`}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  {...(hasScore ? { "aria-valuenow": clamped } : {})}
                >
                  {hasScore && (
                    <div
                      className={`h-full rounded-full ${barColor(s.score)} transition-[width] duration-500 ease-out`}
                      style={{ width: `${clamped}%` }}
                    />
                  )}
                </div>
                {hasScore ? (
                  <span
                    className={`text-right font-serif text-[16px] font-medium tabular-nums ${scoreInkColor(s.score)}`}
                  >
                    {clamped}%
                  </span>
                ) : (
                  <span className="flex flex-col items-end leading-tight">
                    <span className="font-serif text-[16px] font-medium text-[#9a958b]">—</span>
                    <span className="mt-0.5 font-mono text-[9.5px] uppercase tracking-[0.18em] text-[#9a958b]">
                      언급 없음
                    </span>
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="mt-5 rounded-[8px] border border-dashed border-[#dcd6c5] bg-[#fbf9f3] p-4 text-sm text-[#9a958b]">
          요소별 점수 데이터가 아직 없습니다.
        </p>
      )}

      <p className="mt-5 border-t border-[#e8e3d6] pt-4 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760]">
        분석 리뷰 수: {reviewCountLabel}
      </p>
    </div>
  );
}
