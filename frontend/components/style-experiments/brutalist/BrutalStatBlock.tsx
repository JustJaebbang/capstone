import type { ReactNode } from "react";

type Props = {
  index: string;       // "01"
  label: string;       // "TOTAL FILMS"
  value: string;       // "02"
  unit?: string;       // "FILMS"
  caption?: ReactNode; // 부가설명
  accent?: "ink" | "yellow" | "white";
};

const surfaceMap: Record<NonNullable<Props["accent"]>, string> = {
  ink: "bg-[#0a0a0a] text-[#ece6d6]",
  yellow: "bg-[#FFE600] text-[#0a0a0a]",
  white: "bg-white text-[#0a0a0a]",
};

export default function BrutalStatBlock({
  index,
  label,
  value,
  unit,
  caption,
  accent = "white",
}: Props) {
  const surface = surfaceMap[accent];

  return (
    <div
      className={`relative border-[3px] border-[#0a0a0a] ${surface}`}
      style={{ boxShadow: "8px 8px 0 0 #0a0a0a" }}
    >
      <div className="flex items-center justify-between border-b-[3px] border-[#0a0a0a] px-3 py-1.5 font-mono text-[10px] tracking-[0.18em] uppercase">
        <span>{`>> ${label}`}</span>
        <span>[{index}]</span>
      </div>

      <div className="flex items-end justify-between px-4 pt-5 pb-3">
        <div
          className="font-display leading-[0.85] tracking-tight"
          style={{ fontSize: "clamp(48px, 6vw, 88px)" }}
        >
          {value}
        </div>
        {unit && (
          <div className="font-mono text-[11px] tracking-[0.2em] uppercase pb-2">
            /{unit}
          </div>
        )}
      </div>

      {caption && (
        <div className="border-t-[3px] border-dashed border-[#0a0a0a] px-4 py-2 font-mono text-[10px] tracking-wider uppercase">
          {caption}
        </div>
      )}
    </div>
  );
}
