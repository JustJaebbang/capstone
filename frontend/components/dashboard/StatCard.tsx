import type { ReactNode } from "react";

type Props = {
  icon: ReactNode;        // 이모지나 SVG
  iconBgClass: string;    // 아이콘 박스 배경색 (Tailwind)
  label: string;          // "총 영화 수"
  value: string;          // "2개"
  description: string;    // "등록된 전체 영화"
};

export default function StatCard({
  icon,
  iconBgClass,
  label,
  value,
  description,
}: Props) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-start gap-4">
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-xl text-2xl ${iconBgClass}`}
        >
          {icon}
        </div>

        <div className="flex-1">
          <p className="text-xs font-medium text-gray-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
          <p className="mt-1 text-xs text-gray-400">{description}</p>
        </div>
      </div>
    </div>
  );
}