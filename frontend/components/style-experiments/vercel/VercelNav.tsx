import Link from "next/link";

type Props = {
  stamp: string;
};

export default function VercelNav({ stamp }: Props) {
  return (
    <header className="sticky top-0 z-30 h-16 border-b border-[#1f1f1f] bg-[#0a0a0a]/85 backdrop-blur-md">
      <div className="mx-auto flex h-full max-w-[1400px] items-center justify-between px-6">
        {/* logo cluster */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2.5">
            <svg
              viewBox="0 0 76 65"
              fill="currentColor"
              aria-hidden
              className="h-[18px] w-[21px] text-white"
            >
              <path d="M37.5274 0L75.0548 65H0L37.5274 0Z" />
            </svg>
            <span className="font-mono text-[12px] tracking-tight text-white/90">
              review.os
            </span>
          </Link>

          <span className="h-4 w-px bg-[#262626]" />

          <span className="font-mono text-[12px] text-[#666] hover:text-white/80 transition-colors">
            kcwoo&apos;s-team
          </span>

          <span className="ml-1 inline-flex items-center gap-1 rounded-full border border-[#1f1f1f] bg-[#111] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-[#888]">
            Hobby
          </span>
        </div>

        {/* center links */}
        <nav className="hidden items-center gap-1 md:flex">
          {[
            { href: "/", label: "Overview" },
            { href: "/movies", label: "Inventory" },
            { href: "/jobs", label: "Jobs" },
            { href: "#activity", label: "Activity" },
            { href: "#docs", label: "Docs" },
          ].map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="rounded-full px-3 py-1.5 text-[13px] font-medium tracking-[-0.01em] text-[#a1a1a1] transition-colors hover:bg-white/[0.04] hover:text-white"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* right cluster */}
        <div className="flex items-center gap-2">
          <span className="hidden font-mono text-[11px] tracking-tight text-[#666] md:inline">
            updated · {stamp}
          </span>
          <button
            type="button"
            className="inline-flex h-7 items-center gap-1.5 rounded-[6px] border border-[#262626] bg-[#0a0a0a] px-2.5 text-[13px] font-medium tracking-[-0.01em] text-white transition-colors hover:border-[#404040]"
          >
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-gradient-to-tr from-[#7928ca] to-[#ff0080]" />
            Ask AI
          </button>
          <button
            type="button"
            className="inline-flex h-7 items-center rounded-[6px] bg-white px-2.5 text-[13px] font-medium tracking-[-0.01em] text-black transition-colors hover:bg-white/90"
          >
            Deploy
          </button>
        </div>
      </div>
    </header>
  );
}
