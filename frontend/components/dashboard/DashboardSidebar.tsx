import type { DashboardSummary } from "@/lib/types";
import SentimentDonut from "./SentimentDonut";
import KeywordRow from "./KeywordRow";

type Props = {
  summary: DashboardSummary;
};

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${month}월 ${day}일 ${hh}:${mm}`;
}

export default function DashboardSidebar({ summary }: Props) {
  return (
    <aside className="flex flex-col gap-4">
      {/* 1. 감성 비율 요약 */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-gray-900">감성 비율 요약</h3>

        <div className="mt-4 flex items-center gap-4">
          <SentimentDonut
            positivePercent={summary.overall_sentiment.positive_percent}
            negativePercent={summary.overall_sentiment.negative_percent}
            size={88}
            strokeWidth={14}
          />

          <div className="flex flex-col gap-1.5 text-sm">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              <span className="text-gray-600">긍정</span>
              <span className="font-bold text-green-600">
                {summary.overall_sentiment.positive_percent}%
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              <span className="text-gray-600">부정</span>
              <span className="font-bold text-red-600">
                {summary.overall_sentiment.negative_percent}%
              </span>
            </div>
          </div>
        </div>

        <p className="mt-3 text-xs text-gray-400">
          전체 리뷰 {summary.total_reviews.toLocaleString()}개
        </p>
      </div>

      {/* 2. TOP 키워드 (전체) */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-gray-900">TOP 키워드 (전체)</h3>

        <div className="mt-4 flex flex-col gap-1.5">
          {summary.top_keywords_overall.map((kw) => (
            <KeywordRow key={kw.rank} keyword={kw} />
          ))}
        </div>

        <button
          type="button"
          className="mt-3 w-full text-right text-xs font-semibold text-blue-600 hover:underline"
        >
          더보기 →
        </button>
      </div>

      {/* 3. 최근 분석 활동 */}
      <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-bold text-gray-900">최근 분석 활동</h3>

        <ul className="mt-4 flex flex-col gap-3">
          {summary.recent_activities.map((activity) => (
            <li
              key={activity.movie_id}
              className="flex items-start justify-between"
            >
              <div className="flex items-start gap-2">
                <span className="mt-0.5 text-green-500">✓</span>
                <div>
                  <p className="text-sm font-semibold text-gray-900">
                    {activity.movie_title}
                  </p>
                  <p className="text-xs text-gray-400">
                    {activity.status === "completed"
                      ? "분석 완료"
                      : activity.status === "running"
                      ? "분석 진행 중"
                      : "분석 실패"}
                  </p>
                </div>
              </div>
              <span className="text-xs text-gray-400">
                {formatDateTime(activity.completed_at)}
              </span>
            </li>
          ))}
        </ul>

        <button
          type="button"
          className="mt-3 w-full text-right text-xs font-semibold text-blue-600 hover:underline"
        >
          전체 활동 보기 →
        </button>
      </div>
    </aside>
  );
}