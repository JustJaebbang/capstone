import type { TopKeyword } from "@/lib/types";

type Props = {
  keyword: TopKeyword;
};

export default function KeywordRow({ keyword }: Props) {
  const { rank, label, sentiment, count } = keyword;

  // 감성에 따라 배경색과 이모지 결정
  const isPositive = sentiment === "positive";
  const isNegative = sentiment === "negative";

  const bgClass = isPositive
    ? "bg-green-50"
    : isNegative
    ? "bg-red-50"
    : "bg-gray-50";

  const icon = isPositive ? "👍" : isNegative ? "👎" : "·";

  return (
    <div
      className={`flex items-center justify-between rounded-lg px-3 py-2 ${bgClass}`}
    >
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-gray-400 w-4">{rank}</span>
        <span className="text-sm font-medium text-gray-800">{label}</span>
        <span className="text-sm">{icon}</span>
      </div>
      <span className="text-sm font-semibold text-gray-700 tabular-nums">
        {count.toLocaleString()}
      </span>
    </div>
  );
}