import type { ReactNode } from "react";

type Props = {
  title: string;
  subtitle?: string;
  showAllHref?: string;
  children: ReactNode;
};

export default function SpotifyShelf({
  title,
  subtitle,
  showAllHref = "#",
  children,
}: Props) {
  return (
    <section className="px-8 pt-6">
      <div className="mb-4 flex items-end justify-between">
        <div>
          <a
            href={showAllHref}
            className="block text-white transition-colors hover:underline"
            style={{
              fontFamily:
                "var(--font-geist-sans), 'Apple SD Gothic Neo', system-ui, sans-serif",
              fontSize: "24px",
              fontWeight: 700,
              letterSpacing: "-0.02em",
              lineHeight: 1.1,
            }}
          >
            {title}
          </a>
          {subtitle && (
            <p
              className="mt-1 text-[14px] text-[#b3b3b3]"
              style={{ fontWeight: 400 }}
            >
              {subtitle}
            </p>
          )}
        </div>
        <a
          href={showAllHref}
          className="text-[12px] text-[#b3b3b3] hover:underline"
          style={{
            fontWeight: 700,
            letterSpacing: "0.04em",
            textTransform: "uppercase",
          }}
        >
          Show all
        </a>
      </div>

      {children}
    </section>
  );
}
