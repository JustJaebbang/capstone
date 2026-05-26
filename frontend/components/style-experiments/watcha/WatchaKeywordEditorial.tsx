import type { KeywordSentiment, TopKeyword } from "@/lib/types";

type Props = {
  keywords: TopKeyword[];
};

const toneStyles: Record<
  KeywordSentiment,
  { ink: string; bg: string; label: string }
> = {
  positive: { ink: "#a8174b", bg: "#fdeaf0", label: "긍정 우세" },
  negative: { ink: "#0f4c5c", bg: "#e0ecf0", label: "부정 우세" },
  neutral: { ink: "#5a564f", bg: "#ece8db", label: "의견 분기" },
};

export default function WatchaKeywordEditorial({ keywords }: Props) {
  const total = keywords.reduce((s, k) => s + k.count, 0) || 1;
  const max = Math.max(...keywords.map((k) => k.count), 1);

  return (
    <section className="border-b border-[#e8e3d6] bg-[#f5f1e6]">
      <div className="mx-auto max-w-[1240px] px-8 py-24">
        <div className="grid grid-cols-1 gap-14 lg:grid-cols-[0.85fr_1.15fr] lg:gap-20">
          <div className="lg:sticky lg:top-28 lg:self-start">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
              Notebook · 02
            </p>
            <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[52px]">
              관객이 가장 자주
              <br />
              꺼낸 <span className="italic">단어들</span>
            </h2>
            <p className="mt-6 max-w-[400px] text-[15px] leading-[1.75] text-[#3d3a35]">
              모든 작품을 통틀어 등장 횟수가 많았던 키워드입니다.
              평점 한 줄로는 닿지 않는 결을 보여줍니다.
            </p>

            <p className="mt-10 font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
              method
            </p>
            <p className="mt-2 max-w-[400px] text-[13px] leading-[1.7] text-[#6b6760]">
              LLM이 의견 조각을 추출하고 HDBSCAN이 묶은 군집의
              <em className="not-italic font-medium text-[#161616]">
                {" "}
                대표 라벨
              </em>
              만 집계했습니다.
            </p>
          </div>

          <div>
            {keywords.map((k, i) => {
              const t = toneStyles[k.sentiment as KeywordSentiment] ?? toneStyles.neutral;
              const ratio = Math.round((k.count / total) * 100);
              const bar = Math.round((k.count / max) * 100);
              const isLast = i === keywords.length - 1;

              return (
                <article
                  key={k.rank}
                  className={`group grid grid-cols-[64px_1fr_auto] items-center gap-x-6 gap-y-3 ${
                    !isLast ? "border-b border-[#dcd6c5]" : ""
                  } py-8 transition-colors hover:bg-[#fbf9f3]/50`}
                >
                  <span className="font-serif text-[56px] font-normal leading-none text-[#161616] tabular-nums">
                    {String(k.rank).padStart(2, "0")}
                  </span>

                  <div>
                    <h3 className="font-serif text-[34px] font-medium leading-none tracking-tight text-[#161616]">
                      {k.label}
                    </h3>
                    <div className="mt-2.5 flex items-center gap-3">
                      <span
                        className="rounded-full px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.18em]"
                        style={{ background: t.bg, color: t.ink }}
                      >
                        {t.label}
                      </span>
                      <span className="font-mono text-[11px] tabular-nums text-[#6b6760]">
                        전체의 {ratio}%
                      </span>
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="font-serif text-[28px] font-medium leading-none text-[#161616] tabular-nums">
                      {k.count.toLocaleString()}
                    </p>
                    <p className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                      mentions
                    </p>
                  </div>

                  {/* tonal bar spanning across the row */}
                  <div className="col-span-3 mt-1 flex h-[3px] w-full overflow-hidden rounded-full bg-[#e6dfca]">
                    <div
                      className="h-full transition-[width] duration-500"
                      style={{ width: `${bar}%`, background: t.ink }}
                    />
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
