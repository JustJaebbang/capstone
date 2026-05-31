type Props = {
  positivePercent: number;
  size?: number;
  thickness?: number;
  /** Label rendered under the percent. Defaults to "% 호감". */
  label?: string;
};

export default function WatchaSentimentRing({
  positivePercent,
  size = 160,
  thickness = 6,
  label = "% 호감",
}: Props) {
  const radius = (100 - thickness) / 2;
  const dash = `${positivePercent} ${100 - positivePercent}`;

  return (
    <div
      className="relative inline-flex shrink-0"
      style={{ width: size, height: size }}
    >
      <svg viewBox="0 0 100 100" width={size} height={size} aria-hidden>
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="#efe9d8"
          strokeWidth={thickness}
        />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="#ff2c63"
          strokeWidth={thickness}
          strokeDasharray={dash}
          strokeDashoffset="0"
          pathLength={100}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="font-serif font-medium leading-none text-[#161616] tabular-nums"
          style={{ fontSize: Math.round(size * 0.32) }}
        >
          {positivePercent}
        </span>
        <span
          className="mt-1.5 font-mono uppercase tracking-[0.22em] text-[#9a958b]"
          style={{ fontSize: Math.max(9, Math.round(size * 0.065)) }}
        >
          {label}
        </span>
      </div>
    </div>
  );
}
