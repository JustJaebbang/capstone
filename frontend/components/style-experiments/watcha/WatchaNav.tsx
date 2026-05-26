import Link from "next/link";

type Props = {
  updatedAt: string;
};

export default function WatchaNav({ updatedAt }: Props) {
  const d = new Date(updatedAt);
  const stamp = `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(
    2,
    "0",
  )}.${String(d.getDate()).padStart(2, "0")}`;

  return (
    <header className="sticky top-0 z-30 border-b border-[#e8e3d6] bg-[#fbf9f3]/85 backdrop-blur">
      <div className="mx-auto flex max-w-[1240px] items-center justify-between px-8 py-5">
        <Link href="/" className="flex items-baseline gap-1">
          <span className="font-serif text-[26px] font-medium tracking-[-0.02em] text-[#161616]">
            review
          </span>
          <span className="font-serif text-[26px] italic font-medium text-[#ff2c63]">
            pedia
          </span>
          <span className="ml-2 hidden font-mono text-[10px] uppercase tracking-[0.24em] text-[#9a958b] sm:inline">
            vol.07
          </span>
        </Link>

        <nav className="hidden items-center gap-9 md:flex">
          <span className="text-[13.5px] font-medium tracking-tight text-[#161616]">
            영화
          </span>
          <span className="text-[13.5px] tracking-tight text-[#6b6760] hover:text-[#161616]">
            키워드
          </span>
          <span className="text-[13.5px] tracking-tight text-[#6b6760] hover:text-[#161616]">
            분석 노트
          </span>
          <span className="text-[13.5px] tracking-tight text-[#6b6760] hover:text-[#161616]">
            아카이브
          </span>
        </nav>

        <div className="flex items-center gap-3">
          <span className="hidden font-mono text-[11px] uppercase tracking-[0.16em] text-[#9a958b] md:inline">
            batch · {stamp}
          </span>
          <Link
            href="/movies"
            className="rounded-full bg-[#161616] px-4 py-2 text-[12.5px] font-medium tracking-tight text-[#fbf9f3] transition-colors hover:bg-[#ff2c63]"
          >
            대시보드 열기
          </Link>
        </div>
      </div>
    </header>
  );
}
