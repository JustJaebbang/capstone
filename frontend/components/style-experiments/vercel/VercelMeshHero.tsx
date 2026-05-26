import Link from "next/link";

type Props = {
  eyebrow: string;
  headline: string;
  body: string;
  ctaPrimary: { label: string; href: string };
  ctaSecondary: { label: string; href: string };
  lastBatchLabel: string;
};

export default function VercelMeshHero({
  eyebrow,
  headline,
  body,
  ctaPrimary,
  ctaSecondary,
  lastBatchLabel,
}: Props) {
  return (
    <section className="relative overflow-hidden border-b border-[#1f1f1f]">
      {/* mesh gradient backdrop */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background: `
            radial-gradient(at 18% 28%, rgba(0,124,240,0.55) 0%, transparent 45%),
            radial-gradient(at 82% 18%, rgba(0,223,216,0.40) 0%, transparent 50%),
            radial-gradient(at 60% 62%, rgba(121,40,202,0.55) 0%, transparent 50%),
            radial-gradient(at 28% 78%, rgba(255,0,128,0.45) 0%, transparent 45%),
            radial-gradient(at 88% 78%, rgba(249,203,40,0.30) 0%, transparent 55%)
          `,
          filter: "blur(80px) saturate(1.1)",
          opacity: 0.55,
        }}
      />
      {/* faint grid */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-[0.06]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage:
            "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        }}
      />
      {/* bottom fade into page */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 bottom-0 -z-10 h-40 bg-gradient-to-b from-transparent to-[#0a0a0a]"
      />

      <div className="mx-auto max-w-[1400px] px-6 py-24 sm:py-32">
        {/* eyebrow */}
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-[#1f1f1f] bg-[#0a0a0a]/80 px-2.5 py-1 font-mono text-[12px] leading-4 text-[#a1a1a1] backdrop-blur">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#50e3c2] shadow-[0_0_8px_#50e3c2]" />
            {eyebrow}
          </span>
        </div>

        {/* headline — display-xl, weight 600, -2.4px tracking */}
        <h1
          className="mt-6 max-w-[820px] text-white"
          style={{
            fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
            fontSize: "clamp(40px, 6vw, 72px)",
            fontWeight: 600,
            lineHeight: 1.02,
            letterSpacing: "-0.045em",
          }}
        >
          {headline}
        </h1>

        {/* body-lg */}
        <p
          className="mt-6 max-w-[600px] text-[#a1a1a1]"
          style={{
            fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
            fontSize: "18px",
            lineHeight: "28px",
          }}
        >
          {body}
        </p>

        {/* CTA row — marketing 100px pill scale */}
        <div className="mt-8 flex flex-wrap items-center gap-3">
          <Link
            href={ctaPrimary.href}
            className="inline-flex h-11 items-center gap-1.5 rounded-full bg-white px-5 text-[15px] font-medium tracking-[-0.01em] text-black transition-transform duration-150 hover:scale-[1.02]"
          >
            {ctaPrimary.label}
            <span aria-hidden>→</span>
          </Link>
          <Link
            href={ctaSecondary.href}
            className="inline-flex h-11 items-center gap-1.5 rounded-full border border-[#262626] bg-transparent px-5 text-[15px] font-medium tracking-[-0.01em] text-white transition-colors hover:bg-white/[0.04]"
          >
            {ctaSecondary.label}
          </Link>
          <span className="ml-2 font-mono text-[12px] text-[#666]">
            $ npm run pipeline · last batch {lastBatchLabel}
          </span>
        </div>
      </div>
    </section>
  );
}
