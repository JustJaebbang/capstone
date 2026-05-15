import type { ReactNode } from "react";

type Props = {
  label: string;
  value: string;
  unit?: string;
  delta?: { tone: "up" | "down" | "neutral"; text: string };
  spark?: ReactNode;
};

const toneColor: Record<NonNullable<Props["delta"]>["tone"], string> = {
  up: "text-[#50e3c2]",
  down: "text-[#ff4d4d]",
  neutral: "text-[#888]",
};

export default function VercelStatCard({
  label,
  value,
  unit,
  delta,
  spark,
}: Props) {
  return (
    <div
      className="group relative overflow-hidden rounded-[12px] border border-[#1f1f1f] bg-[#0f0f0f] p-6 transition-colors hover:border-[#2a2a2a]"
      style={{
        boxShadow:
          "0 1px 1px rgba(255,255,255,0.02) inset, 0 1px 1px rgba(0,0,0,0.6), 0 8px 16px -8px rgba(0,0,0,0.5)",
      }}
    >
      {/* mono label */}
      <div className="flex items-center justify-between">
        <span
          className="font-mono text-[12px] uppercase tracking-[0.02em] text-[#888]"
          style={{ fontFamily: "var(--font-geist-mono), ui-monospace, monospace" }}
        >
          {label}
        </span>
        {delta && (
          <span className={`font-mono text-[11px] ${toneColor[delta.tone]}`}>
            {delta.tone === "up" ? "▲" : delta.tone === "down" ? "▼" : "■"}{" "}
            {delta.text}
          </span>
        )}
      </div>

      {/* big number */}
      <div className="mt-3 flex items-baseline gap-1.5">
        <span
          className="text-white"
          style={{
            fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
            fontSize: "40px",
            lineHeight: "44px",
            fontWeight: 600,
            letterSpacing: "-0.04em",
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {value}
        </span>
        {unit && (
          <span className="text-[14px] font-medium tracking-[-0.01em] text-[#666]">
            {unit}
          </span>
        )}
      </div>

      {/* sparkline / decorative */}
      {spark && <div className="mt-4 h-10">{spark}</div>}
    </div>
  );
}
