type Props = {
  items: string[];
  speedSeconds?: number;
};

export default function BrutalMarquee({ items, speedSeconds = 40 }: Props) {
  // duplicate the list so the marquee loops seamlessly
  const loop = [...items, ...items];

  return (
    <div className="relative overflow-hidden border-y-[3px] border-[#0a0a0a] bg-[#FFE600]">
      <div
        className="flex w-max items-center gap-10 py-2 font-display text-[22px] tracking-[0.04em] whitespace-nowrap"
        style={{
          animation: `brutal-marquee ${speedSeconds}s linear infinite`,
        }}
      >
        {loop.map((s, i) => (
          <span key={i} className="flex items-center gap-10">
            <span>{s}</span>
            <span aria-hidden className="text-[#0a0a0a]/70">✦</span>
          </span>
        ))}
      </div>
    </div>
  );
}
