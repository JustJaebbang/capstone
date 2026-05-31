type TopOpinion = {
  label: string;
  count: number;
};

type TopOpinionsProps = {
  opinions: TopOpinion[];
};

export default function TopOpinions({ opinions }: TopOpinionsProps) {
  return (
    <section className="mt-10">
      <h2 className="text-xl font-bold text-gray-900">많이 나온 의견 TOP 3</h2>

      <div className="mt-4 grid gap-4 md:grid-cols-3">
        {opinions.map((opinion, index) => (
          <div
            key={opinion.label}
            className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
          >
            <p className="text-sm font-semibold text-blue-600">
              {index + 1}위
            </p>
            <h3 className="mt-3 text-lg font-bold text-gray-900">
              {opinion.label}
            </h3>
            <p className="mt-2 text-gray-500">{opinion.count}건</p>
          </div>
        ))}
      </div>
    </section>
  );
}