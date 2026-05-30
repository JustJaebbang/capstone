import Link from "next/link";

type Props = {
  movieTitle: string;
  href?: string | null;
};

const REPEAT = 4; // 짧은 제목·넓은 화면에서도 폭을 채우도록 한 그룹당 여러 벌 반복

export default function WatchaTicker({ movieTitle, href }: Props) {
  const renderGroup = (groupKey: string, ariaHidden: boolean) => (
    <div className="flex shrink-0" aria-hidden={ariaHidden || undefined}>
      {Array.from({ length: REPEAT }).map((_, i) => (
        <span
          key={`${groupKey}-${i}`}
          className="px-12 font-mono text-[14px] uppercase tracking-[0.18em] text-[#6b6760]"
        >
          최근 분석된 영화는{" "}
          <em className="not-italic font-medium text-[#ff2c63]">{movieTitle}</em>{" "}
          입니다!
        </span>
      ))}
    </div>
  );

  const strip = (
    <div className="watcha-ticker overflow-hidden border-y border-[#e8e3d6] bg-[#fbf9f3] py-3">
      <div className="watcha-ticker-track flex w-max whitespace-nowrap">
        {renderGroup("a", false)}
        {renderGroup("b", true)}
      </div>
      <style>{`
        @keyframes watcha-ticker {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
        .watcha-ticker-track {
          animation: watcha-ticker 28s linear infinite;
          will-change: transform;
        }
        .watcha-ticker:hover .watcha-ticker-track {
          animation-play-state: paused;
        }
        @media (prefers-reduced-motion: reduce) {
          .watcha-ticker-track { animation: none; }
        }
      `}</style>
    </div>
  );

  if (href) {
    return (
      <Link
        href={href}
        aria-label={`최근 분석된 영화 ${movieTitle} 결과 보기`}
        className="block transition-colors hover:bg-[#f5f1e6]"
      >
        {strip}
      </Link>
    );
  }
  return strip;
}
