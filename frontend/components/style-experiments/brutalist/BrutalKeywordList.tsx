import type { TopKeyword } from "@/lib/types";

type Props = {
  title: string;
  keywords: TopKeyword[];
};

const sentimentMarker: Record<string, { tag: string; bg: string; fg: string }> = {
  positive: { tag: "POS", bg: "bg-[#0a0a0a]", fg: "text-[#FFE600]" },
  negative: { tag: "NEG", bg: "bg-[#FF3B00]", fg: "text-white" },
  neutral: { tag: "NEU", bg: "bg-white", fg: "text-[#0a0a0a]" },
};

export default function BrutalKeywordList({ title, keywords }: Props) {
  const maxCount = keywords.reduce((m, k) => Math.max(m, k.count), 1);

  return (
    <section
      className="border-[3px] border-[#0a0a0a] bg-[#ece6d6]"
      style={{ boxShadow: "8px 8px 0 0 #0a0a0a" }}
    >
      <div className="flex items-center justify-between border-b-[3px] border-[#0a0a0a] bg-[#FFE600] px-4 py-2 font-mono text-[11px] tracking-[0.22em] uppercase text-[#0a0a0a]">
        <span>▣ {title}</span>
        <span>RANKED</span>
      </div>

      <ul className="divide-y-[3px] divide-[#0a0a0a]">
        {keywords.map((kw) => {
          const marker =
            sentimentMarker[kw.sentiment] ?? sentimentMarker.neutral;
          const widthPct = (kw.count / maxCount) * 100;

          return (
            <li
              key={`${kw.rank}-${kw.label}`}
              className="relative grid grid-cols-[56px_1fr_84px] items-center"
            >
              <span className="border-r-[3px] border-[#0a0a0a] bg-[#0a0a0a] py-3 text-center font-mono text-[12px] tracking-widest text-[#FFE600]">
                #{String(kw.rank).padStart(2, "0")}
              </span>

              <div className="relative h-full px-4 py-3">
                <div
                  className="absolute inset-y-0 left-0 -z-0 bg-white"
                  style={{ width: `${widthPct}%` }}
                />
                <div className="relative flex items-center gap-3">
                  <span className="font-display-kr text-2xl leading-none text-[#0a0a0a]">
                    {kw.label}
                  </span>
                  <span
                    className={`px-1.5 py-0.5 font-mono text-[10px] tracking-widest ${marker.bg} ${marker.fg}`}
                  >
                    {marker.tag}
                  </span>
                </div>
              </div>

              <span className="border-l-[3px] border-[#0a0a0a] py-3 pr-4 text-right font-mono text-[12px] tracking-wider text-[#0a0a0a]">
                {kw.count.toLocaleString()}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
