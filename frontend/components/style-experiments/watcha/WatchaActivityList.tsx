import type {
  DashboardMovie,
  JobStatus,
  RecentActivity,
} from "@/lib/types";

type Props = {
  activities: RecentActivity[];
  movies: DashboardMovie[];
};

const statusTone: Record<
  JobStatus,
  { text: string; ink: string; dot: string }
> = {
  completed: { text: "분석 완료", ink: "#1a7a4a", dot: "#27ae60" },
  running: { text: "분석 진행", ink: "#a16d12", dot: "#d68910" },
  failed: { text: "분석 실패", ink: "#9c2424", dot: "#c0392b" },
};

function timeLabel(iso: string): { date: string; time: string } {
  const d = new Date(iso);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return { date: `${month}.${day}`, time: `${hh}:${mm}` };
}

export default function WatchaActivityList({ activities, movies }: Props) {
  const lookup = new Map(movies.map((m) => [m.movie_id, m]));

  return (
    <section className="border-b border-[#e8e3d6]">
      <div className="mx-auto max-w-[1240px] px-8 py-24">
        <div className="mb-12 flex items-end justify-between gap-6">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
              Logbook · 03
            </p>
            <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[52px]">
              최근 <span className="italic">분석 노트</span>
            </h2>
          </div>
          <div className="hidden text-right md:block">
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
              schedule
            </p>
            <p className="mt-1 font-mono text-[12px] tracking-tight text-[#3d3a35]">
              daily · 03:00 KST
            </p>
          </div>
        </div>

        <ol>
          {activities.map((a, i) => {
            const t = timeLabel(a.completed_at);
            const tone = statusTone[a.status];
            const movie = lookup.get(a.movie_id);
            const isLast = i === activities.length - 1;
            const topK = movie?.top_keywords[0];

            return (
              <li
                key={`${a.movie_id}-${i}`}
                className={`grid grid-cols-[88px_1fr] items-start gap-x-6 gap-y-3 sm:grid-cols-[110px_1fr_auto] ${
                  !isLast ? "border-b border-[#e8e3d6]" : ""
                } py-8`}
              >
                {/* time */}
                <div>
                  <p className="font-mono text-[11px] tracking-tight text-[#6b6760]">
                    {t.date}
                  </p>
                  <p className="font-serif text-[28px] leading-none tracking-[-0.01em] text-[#161616] tabular-nums">
                    {t.time}
                  </p>
                </div>

                {/* body */}
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span
                      className="inline-flex h-1.5 w-1.5 rounded-full"
                      style={{ background: tone.dot }}
                    />
                    <span
                      className="font-mono text-[10px] uppercase tracking-[0.18em]"
                      style={{ color: tone.ink }}
                    >
                      {tone.text}
                    </span>
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                      · {a.movie_id}
                    </span>
                  </div>
                  <h3 className="mt-2 font-serif text-[28px] font-medium leading-[1.1] tracking-[-0.01em] text-[#161616]">
                    {a.movie_title}
                  </h3>
                  {movie && (
                    <p className="mt-2.5 text-[13.5px] leading-[1.6] text-[#6b6760]">
                      리뷰{" "}
                      <span className="font-medium text-[#161616] tabular-nums">
                        {movie.review_count.toLocaleString()}
                      </span>
                      건 · 호감{" "}
                      <span className="font-medium text-[#ff2c63] tabular-nums">
                        {movie.sentiment.positive_percent}%
                      </span>
                      {topK ? (
                        <>
                          {" "}
                          · 대표 키워드{" "}
                          <em className="font-serif text-[15px] not-italic font-medium text-[#161616]">
                            {topK.label}
                          </em>
                        </>
                      ) : null}
                    </p>
                  )}
                </div>

                {/* job id */}
                <div className="col-span-2 mt-1 flex items-center justify-between sm:col-span-1 sm:mt-0 sm:flex-col sm:items-end sm:justify-start">
                  <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                    job_id
                  </p>
                  <p className="font-mono text-[12px] text-[#3d3a35]">
                    {movie?.latest_job_id ?? "—"}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
