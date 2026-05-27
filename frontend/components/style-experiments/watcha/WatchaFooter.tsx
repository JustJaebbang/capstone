import Link from "next/link";

type Props = {
  updatedAt: string;
};

export default function WatchaFooter({ updatedAt }: Props) {
  const d = new Date(updatedAt);
  const year = d.getFullYear();
  const stamp = `${String(d.getMonth() + 1).padStart(2, "0")}.${String(
    d.getDate(),
  ).padStart(2, "0")}`;

  return (
    <footer className="bg-[#161616] text-[#fbf9f3]">
      <div className="mx-auto max-w-[1240px] px-8 py-16">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-[1.4fr_1fr]">
          <div>
            <div className="flex items-baseline gap-1">
              <span className="font-serif text-[28px] font-medium">
                review
              </span>
              <span className="font-serif text-[28px] italic font-medium text-[#ff2c63]">
                pedia
              </span>
            </div>
            <p className="mt-4 max-w-sm text-[13.5px] leading-[1.7] text-[#fbf9f3]/55">
              평점 대신 의견을. LLM·HDBSCAN 파이프라인이 매일 새벽 3시,
              관객 리뷰를 의견 군집으로 구조화합니다.
            </p>
            <p className="mt-6 inline-flex items-center gap-2 rounded-full bg-white/[0.06] px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-[#fbf9f3]/75">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#27ae60] shadow-[0_0_8px_#27ae60]" />
              pipeline online
            </p>
          </div>

          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#fbf9f3]/40">
              read
            </p>
            <ul className="mt-4 space-y-2.5 text-[13.5px] text-[#fbf9f3]/80">
              <li>
                <Link href="/movies" className="hover:text-[#ff2c63]">
                  분석 대상 영화 →
                </Link>
              </li>
              <li>
                <Link href="/" className="hover:text-[#ff2c63]">
                  홈으로 돌아가기
                </Link>
              </li>
              <li>
                <span className="text-[#fbf9f3]/60">파이프라인 노트</span>
              </li>
            </ul>
          </div>

        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-2 border-t border-white/10 pt-6 font-mono text-[10px] uppercase tracking-[0.22em] text-[#fbf9f3]/40 sm:flex-row sm:items-center">
          <span>
            © {year} review.pedia · vol.07 · printed {stamp}
          </span>
          <span>movie review pipeline · daily edition</span>
        </div>
      </div>
    </footer>
  );
}
