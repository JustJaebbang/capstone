import type { RecentActivity } from "@/lib/types";

type Props = {
  activities: RecentActivity[];
};

const statusBadge: Record<
  string,
  { dot: string; label: string; tone: string }
> = {
  completed: {
    dot: "bg-[#1ed760] shadow-[0_0_6px_#1ed760]",
    label: "Played",
    tone: "text-[#1ed760]",
  },
  running: {
    dot: "bg-[#ffa42b] shadow-[0_0_6px_#ffa42b]",
    label: "Streaming",
    tone: "text-[#ffa42b]",
  },
  failed: {
    dot: "bg-[#f3727f] shadow-[0_0_6px_#f3727f]",
    label: "Error",
    tone: "text-[#f3727f]",
  },
};

function timeAgo(iso: string, ref: Date): string {
  const t = new Date(iso).getTime();
  const diff = Math.max(0, ref.getTime() - t);
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m} min ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} hr ago`;
  const d = Math.floor(h / 24);
  return `${d} day${d === 1 ? "" : "s"} ago`;
}

function formatStamp(iso: string): string {
  const d = new Date(iso);
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${mm}-${dd} ${hh}:${mi}`;
}

const coverFor = (id: string): string => {
  const palettes = [
    "linear-gradient(135deg, #1db954 0%, #064e2c 100%)",
    "linear-gradient(135deg, #f59e0b 0%, #7c2d12 100%)",
    "linear-gradient(135deg, #ef4444 0%, #4c0519 100%)",
    "linear-gradient(135deg, #6366f1 0%, #1e1b4b 100%)",
    "linear-gradient(135deg, #ec4899 0%, #4a044e 100%)",
    "linear-gradient(135deg, #06b6d4 0%, #083344 100%)",
  ];
  const sum = [...id].reduce((s, c) => s + c.charCodeAt(0), 0);
  return palettes[sum % palettes.length];
};

export default function SpotifyActivityList({ activities }: Props) {
  const reference = activities.length
    ? new Date(activities[0].completed_at)
    : new Date();

  return (
    <div className="px-8">
      <div
        className="grid grid-cols-[40px_1.4fr_1fr_120px_120px] items-center gap-4 border-b border-[#282828] px-4 py-2 text-[12px] uppercase text-[#b3b3b3]"
        style={{ letterSpacing: "0.08em" }}
      >
        <span className="text-right">#</span>
        <span>Title</span>
        <span>Channel</span>
        <span>Status</span>
        <span className="text-right">When</span>
      </div>

      <ul>
        {activities.map((a, i) => {
          const s = statusBadge[a.status] ?? statusBadge.completed;
          return (
            <li
              key={a.movie_id}
              className="group grid grid-cols-[40px_1.4fr_1fr_120px_120px] items-center gap-4 rounded-md px-4 py-2 hover:bg-white/[0.06]"
            >
              <span className="text-right text-[14px] text-[#b3b3b3]">
                {i + 1}
              </span>
              <div className="flex min-w-0 items-center gap-3">
                <span
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-sm text-[10.5px] uppercase text-white"
                  style={{
                    background: coverFor(a.movie_id),
                    fontWeight: 700,
                    letterSpacing: "0.04em",
                  }}
                >
                  {a.movie_title.slice(0, 2)}
                </span>
                <div className="min-w-0">
                  <p
                    className="truncate text-[15px] text-white"
                    style={{ fontWeight: 700, letterSpacing: "-0.01em" }}
                  >
                    {a.movie_title}
                  </p>
                  <p className="truncate text-[12px] text-[#b3b3b3]">
                    review.os · daily batch
                  </p>
                </div>
              </div>

              <span className="text-[14px] text-[#b3b3b3]">
                Daily Batch · main
              </span>

              <span className={`flex items-center gap-2 text-[14px] ${s.tone}`}>
                <span className={`inline-block h-1.5 w-1.5 rounded-full ${s.dot}`} />
                {s.label}
              </span>

              <span
                className="text-right text-[14px] text-[#b3b3b3]"
                title={formatStamp(a.completed_at)}
              >
                {timeAgo(a.completed_at, reference)}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
