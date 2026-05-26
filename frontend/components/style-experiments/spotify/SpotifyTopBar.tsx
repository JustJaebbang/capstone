type Props = {
  scrolled?: boolean;
};

export default function SpotifyTopBar({ scrolled = false }: Props) {
  return (
    <div
      className={`sticky top-0 z-20 flex items-center justify-between px-6 py-3 transition-colors ${
        scrolled ? "bg-[#101010]/85 backdrop-blur" : "bg-transparent"
      }`}
    >
      {/* left — back / forward */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          aria-label="Go back"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-white hover:scale-105"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M11.03.47a.75.75 0 010 1.06L4.56 8l6.47 6.47a.75.75 0 11-1.06 1.06L2.44 8 9.97.47a.75.75 0 011.06 0z" />
          </svg>
        </button>
        <button
          type="button"
          aria-label="Go forward"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-[#b3b3b3] hover:text-white"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M4.97.47a.75.75 0 011.06 0L13.56 8l-7.53 7.53a.75.75 0 11-1.06-1.06L11.44 8 4.97 1.53a.75.75 0 010-1.06z" />
          </svg>
        </button>

        {/* search input */}
        <div
          className="ml-2 flex h-10 w-[360px] items-center gap-3 rounded-full bg-[#1f1f1f] px-3 text-[#b3b3b3]"
          style={{
            boxShadow:
              "rgb(18,18,18) 0px 1px 0px, rgb(124,124,124) 0px 0px 0px 1px inset",
          }}
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M7 1.75a5.25 5.25 0 100 10.5 5.25 5.25 0 000-10.5zM.25 7a6.75 6.75 0 1112.096 4.09l3.282 3.281a.75.75 0 11-1.06 1.06l-3.281-3.28A6.75 6.75 0 01.25 7z" />
          </svg>
          <input
            type="text"
            placeholder="영화, 의견, 키워드 검색"
            className="flex-1 bg-transparent text-[14px] text-white placeholder:text-[#888] focus:outline-none"
          />
          <span className="ml-auto h-5 w-px bg-[#4d4d4d]" />
          <button
            type="button"
            aria-label="Browse"
            className="text-[#b3b3b3] hover:text-white"
          >
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
              <path d="M1.513 1.513A.75.75 0 012.25 1h11.5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0V2.5h-10v11h2.75a.75.75 0 010 1.5h-3.5a.75.75 0 01-.75-.75V1.75zM7.5 6.25a.75.75 0 01.75-.75h6.5a.75.75 0 010 1.5h-6.5a.75.75 0 01-.75-.75zM6.25 7.5a.75.75 0 01.75.75v6.5a.75.75 0 01-1.5 0v-6.5a.75.75 0 01.75-.75z" />
            </svg>
          </button>
        </div>
      </div>

      {/* right — explore + upgrade + avatar */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="rounded-full px-3 py-2 text-[14px] text-[#b3b3b3] hover:text-white"
          style={{ fontWeight: 700 }}
        >
          Explore Premium
        </button>
        <button
          type="button"
          className="flex items-center gap-2 rounded-full bg-black/60 px-3 py-2 text-[13px] text-white hover:scale-[1.03]"
          style={{ fontWeight: 700 }}
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M2.5 4.25A.75.75 0 013.25 3.5h9.5a.75.75 0 010 1.5h-9.5a.75.75 0 01-.75-.75zM2.5 8a.75.75 0 01.75-.75h9.5a.75.75 0 010 1.5h-9.5A.75.75 0 012.5 8zM3.25 11a.75.75 0 000 1.5h9.5a.75.75 0 000-1.5h-9.5z" />
          </svg>
          Install App
        </button>
        <button
          type="button"
          aria-label="Notifications"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-black/60 text-[#b3b3b3] hover:text-white"
        >
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden className="h-4 w-4">
            <path d="M8 1.5a4.5 4.5 0 00-4.5 4.5v3.75L2 11.25h12L12.5 9.75V6A4.5 4.5 0 008 1.5zM6 13a2 2 0 104 0H6z" />
          </svg>
        </button>

        <span
          className="ml-1 flex h-8 w-8 items-center justify-center rounded-full text-[13px] text-black"
          style={{
            background: "linear-gradient(135deg,#1ed760 0%, #14833b 100%)",
            fontWeight: 700,
          }}
          title="kcwoo"
        >
          K
        </span>
      </div>
    </div>
  );
}
