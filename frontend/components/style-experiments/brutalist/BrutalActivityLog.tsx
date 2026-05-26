import type { RecentActivity } from "@/lib/types";

type Props = {
  activities: RecentActivity[];
};

function formatStamp(iso: string): string {
  const d = new Date(iso);
  const yy = String(d.getFullYear()).slice(2);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${yy}.${mm}.${dd} / ${hh}:${mi}`;
}

const statusGlyph: Record<string, { glyph: string; bg: string; fg: string; label: string }> = {
  completed: { glyph: "✔", bg: "bg-[#0a0a0a]", fg: "text-[#FFE600]", label: "DONE" },
  running:   { glyph: "▶", bg: "bg-[#FFE600]", fg: "text-[#0a0a0a]", label: "LIVE" },
  failed:    { glyph: "✖", bg: "bg-[#FF3B00]", fg: "text-white",    label: "FAIL" },
};

export default function BrutalActivityLog({ activities }: Props) {
  return (
    <section
      className="border-[3px] border-[#0a0a0a] bg-white"
      style={{ boxShadow: "8px 8px 0 0 #0a0a0a" }}
    >
      <div className="flex items-center justify-between border-b-[3px] border-[#0a0a0a] bg-[#0a0a0a] px-4 py-2 font-mono text-[11px] tracking-[0.22em] uppercase text-[#ece6d6]">
        <span>▤ RECENT.LOG</span>
        <span className="text-[#FFE600]">TAIL -F</span>
      </div>

      {/* receipt header */}
      <div className="flex items-center gap-3 border-b border-dashed border-[#0a0a0a] px-4 py-2 font-mono text-[10px] tracking-[0.22em] uppercase text-[#0a0a0a]/70">
        <span className="flex-1">▌ STAMP</span>
        <span className="flex-[2]">▌ EVENT</span>
        <span>▌ STATE</span>
      </div>

      <ul>
        {activities.map((a, i) => {
          const s = statusGlyph[a.status] ?? statusGlyph.completed;
          return (
            <li
              key={a.movie_id}
              className="relative grid grid-cols-[110px_1fr_auto] items-center gap-3 border-b border-dashed border-[#0a0a0a] px-4 py-3 last:border-b-0"
            >
              <span className="font-mono text-[11px] tracking-wider text-[#0a0a0a]/75">
                {formatStamp(a.completed_at)}
              </span>

              <div className="flex items-baseline gap-2">
                <span className="font-mono text-[10px] tracking-widest text-[#0a0a0a]/40">
                  [{String(i + 1).padStart(2, "0")}]
                </span>
                <span className="font-display-kr text-lg leading-none text-[#0a0a0a]">
                  {a.movie_title}
                </span>
              </div>

              <span
                className={`inline-flex items-center gap-1.5 border-2 border-[#0a0a0a] px-2 py-0.5 font-mono text-[10px] tracking-widest ${s.bg} ${s.fg}`}
              >
                <span>{s.glyph}</span>
                <span>{s.label}</span>
              </span>
            </li>
          );
        })}
      </ul>

      <div className="border-t-[3px] border-[#0a0a0a] bg-[#ece6d6] px-4 py-2 font-mono text-[10px] tracking-[0.22em] uppercase text-[#0a0a0a]/80">
        ━━ EOF ━━ {activities.length} ENTRIES
      </div>
    </section>
  );
}
