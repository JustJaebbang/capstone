import type { DashboardSummary } from "@/lib/types";
import StatCard from "./StatCard";

type Props = {
  summary: DashboardSummary;
};

export default function StatCardGrid({ summary }: Props) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        icon="🎬"
        iconBgClass="bg-blue-100"
        label="총 영화 수"
        value={`${summary.total_movies}개`}
        description="등록된 전체 영화"
      />
      <StatCard
        icon="✅"
        iconBgClass="bg-green-100"
        label="분석 완료"
        value={`${summary.completed_movies}개`}
        description="분석이 완료된 영화"
      />
      <StatCard
        icon="📊"
        iconBgClass="bg-purple-100"
        label="총 리뷰 수"
        value={`${summary.total_reviews.toLocaleString()}개`}
        description="수집된 전체 리뷰"
      />
      <StatCard
        icon="⏱️"
        iconBgClass="bg-orange-100"
        label="평균 처리 시간"
        value={`${summary.avg_processing_seconds}초`}
        description="영화당 평균 분석 시간"
      />
    </div>
  );
}