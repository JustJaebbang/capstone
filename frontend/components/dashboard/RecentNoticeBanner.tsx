import type { RecentActivity } from "@/lib/types";

type Props = {
  activities: RecentActivity[];
};

function formatStamp(iso: string): string {
  const d = new Date(iso);
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${month}월 ${day}일 ${hh}:${mm}`;
}

export default function RecentNoticeBanner({ activities }: Props) {
  if (activities.length === 0) {
    return null;
  }

  // completed_at 이 가장 최근인 항목 선택
  const latest = [...activities].sort(
    (a, b) =>
      new Date(b.completed_at).getTime() -
      new Date(a.completed_at).getTime(),
  )[0];

  return (
    <div
      role="status"
      className="mb-6 flex flex-wrap items-center gap-x-3 gap-y-1 rounded-2xl border border-blue-100 bg-blue-50 px-5 py-3 text-sm text-blue-900"
    >
      <span aria-hidden className="text-base leading-none">
        📢
      </span>
      <span className="font-medium">최근 분석된 영화:</span>
      <span className="font-bold text-blue-700">{latest.movie_title}</span>
      <span className="ml-auto text-xs text-blue-700/70">
        {formatStamp(latest.completed_at)}
      </span>
    </div>
  );
}
