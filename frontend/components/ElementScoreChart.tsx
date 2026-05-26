import type { ElementScore } from "@/lib/types";

type Props = {
  scores: ElementScore[];
  totalReviewCount?: number | null;
};

function barColor(score: number | null): string {
  if (score === null) return "bg-gray-300";
  if (score >= 85) return "bg-blue-600";
  if (score >= 70) return "bg-blue-500";
  if (score >= 55) return "bg-sky-400";
  return "bg-sky-300";
}

function scoreInkColor(score: number | null): string {
  if (score === null) return "text-gray-400";
  if (score >= 85) return "text-blue-700";
  if (score >= 70) return "text-blue-600";
  if (score >= 55) return "text-sky-600";
  return "text-gray-500";
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
    <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-bold text-gray-900">영화 요소별 점수</h2>
        <span className="text-xs font-medium text-gray-400">0–100점</span>
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
                <span className="text-sm font-semibold text-gray-700">
                  {s.element}
                </span>
                <div
                  className="h-2.5 overflow-hidden rounded-full bg-gray-200"
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
                    className={`text-right text-sm font-bold tabular-nums ${scoreInkColor(s.score)}`}
                  >
                    {clamped}%
                  </span>
                ) : (
                  <span className="flex flex-col items-end leading-tight">
                    <span className="text-sm font-bold text-gray-400">—</span>
                    <span className="mt-0.5 text-[10px] font-medium text-gray-400">
                      언급 없음
                    </span>
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="mt-5 rounded-xl border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-400">
          요소별 점수 데이터가 아직 없습니다.
        </p>
      )}

      <p className="mt-5 border-t border-gray-200 pt-4 text-sm font-semibold text-gray-500">
        분석 리뷰 수: {reviewCountLabel}
      </p>
    </div>
  );
}
