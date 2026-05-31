type Props = {
  positivePercent: number; // 0~100
  negativePercent: number; // 0~100
  size?: number;           // px
  strokeWidth?: number;
};

export default function SentimentDonut({
  positivePercent,
  negativePercent,
  size = 96,
  strokeWidth = 12,
}: Props) {
  // SVG 도넛: stroke-dasharray로 비율 표현
  // 원의 둘레 = 100으로 normalize → 퍼센트 그대로 dasharray 값으로 쓸 수 있음
  const radius = (100 - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  // 100을 기준으로 정규화된 둘레 (stroke-dasharray가 path 길이 기준이므로)
  // viewBox가 0 0 100 100이면 둘레는 2*PI*radius.
  // pathLength prop을 100으로 강제하면 dasharray를 퍼센트 그대로 쓸 수 있음.
  const positiveDash = `${positivePercent} ${100 - positivePercent}`;
  // negative는 positive 다음에 그려지므로 offset만 조정
  const negativeDashOffset = -positivePercent;
  const negativeDash = `${negativePercent} ${100 - negativePercent}`;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      style={{ display: "block" }}
    >
      {/* 배경 원 */}
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#f1f5f9"
        strokeWidth={strokeWidth}
      />
      {/* 긍정 (초록) */}
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#22c55e"
        strokeWidth={strokeWidth}
        strokeDasharray={positiveDash}
        strokeDashoffset="0"
        pathLength={100}
        transform="rotate(-90 50 50)"
        strokeLinecap="butt"
      />
      {/* 부정 (빨강) */}
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#ef4444"
        strokeWidth={strokeWidth}
        strokeDasharray={negativeDash}
        strokeDashoffset={negativeDashOffset}
        pathLength={100}
        transform="rotate(-90 50 50)"
        strokeLinecap="butt"
      />
    </svg>
  );
}