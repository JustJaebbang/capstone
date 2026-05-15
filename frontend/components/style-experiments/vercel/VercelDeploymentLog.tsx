import type { RecentActivity } from "@/lib/types";

type Props = {
  activities: RecentActivity[];
};

const statusStyle: Record<
  string,
  { dot: string; pillBg: string; pillText: string; label: string }
> = {
  completed: {
    dot: "bg-[#50e3c2] shadow-[0_0_8px_#50e3c2]",
    pillBg: "bg-[#0e2a26]",
    pillText: "text-[#50e3c2]",
    label: "Ready",
  },
  running: {
    dot: "bg-[#f5a623] shadow-[0_0_8px_#f5a623]",
    pillBg: "bg-[#2a1f0e]",
    pillText: "text-[#f5a623]",
    label: "Building",
  },
  failed: {
    dot: "bg-[#ff4d4d] shadow-[0_0_8px_#ff4d4d]",
    pillBg: "bg-[#2a0e0e]",
    pillText: "text-[#ff4d4d]",
    label: "Error",
  },
};

function timeAgo(iso: string, now: Date): string {
  const t = new Date(iso).getTime();
  const diff = Math.max(0, now.getTime() - t);
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

function formatStamp(iso: string): string {
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${mm}-${dd} ${hh}:${mi}`;
}

export default function VercelDeploymentLog({ activities }: Props) {
  // Use the most recent activity as our "now" so relative times stay deterministic in SSR.
  const reference = activities.length
    ? new Date(activities[0].completed_at)
    : new Date();

  return (
    <section
      className="overflow-hidden rounded-[12px] border border-[#1f1f1f] bg-[#0f0f0f]"
      style={{
        boxShadow:
          "0 1px 1px rgba(255,255,255,0.02) inset, 0 1px 1px rgba(0,0,0,0.5)",
      }}
      id="activity"
    >
      <div className="flex items-center justify-between border-b border-[#1f1f1f] px-6 py-4">
        <h3
          className="text-white"
          style={{
            fontSize: "16px",
            fontWeight: 600,
            letterSpacing: "-0.02em",
          }}
        >
          Recent activity.
        </h3>
        <span
          className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          tail -f
        </span>
      </div>

      <ul>
        {activities.map((a) => {
          const s = statusStyle[a.status] ?? statusStyle.completed;
          return (
            <li
              key={a.movie_id}
              className="grid grid-cols-[24px_1fr_auto] items-start gap-4 border-b border-[#1a1a1a] px-6 py-4 last:border-b-0 hover:bg-white/[0.015]"
            >
              <span
                className={`mt-2 inline-block h-2 w-2 rounded-full ${s.dot}`}
              />

              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[15px] font-medium tracking-[-0.01em] text-white">
                    {a.movie_title}
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${s.pillBg} ${s.pillText}`}
                  >
                    {s.label}
                  </span>
                </div>
                <div
                  className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 font-mono text-[12px] text-[#666]"
                  style={{ fontFamily: "var(--font-geist-mono), monospace" }}
                >
                  <span>{a.movie_id}</span>
                  <span className="text-[#333]">·</span>
                  <span>main</span>
                  <span className="text-[#333]">·</span>
                  <span>via daily-batch</span>
                </div>
              </div>

              <div className="flex flex-col items-end gap-0.5 text-right">
                <span className="text-[13px] text-[#ededed]">
                  {timeAgo(a.completed_at, reference)}
                </span>
                <span
                  className="font-mono text-[11px] text-[#666]"
                  style={{ fontFamily: "var(--font-geist-mono), monospace" }}
                >
                  {formatStamp(a.completed_at)}
                </span>
              </div>
            </li>
          );
        })}
      </ul>

      <div className="flex items-center justify-between border-t border-[#1f1f1f] bg-[#0a0a0a] px-6 py-3">
        <span
          className="font-mono text-[11px] uppercase tracking-[0.02em] text-[#666]"
          style={{ fontFamily: "var(--font-geist-mono), monospace" }}
        >
          showing {activities.length} of {activities.length}
        </span>
        <button
          type="button"
          className="text-[13px] font-medium tracking-[-0.01em] text-[#0070f3] hover:underline"
        >
          View all activity →
        </button>
      </div>
    </section>
  );
}
