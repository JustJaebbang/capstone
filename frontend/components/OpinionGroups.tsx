type OpinionGroup = {
  cluster_id: string;
  label: string;
  count: number;
};

type OpinionGroupsProps = {
  groups: OpinionGroup[];
};

export default function OpinionGroups({ groups }: OpinionGroupsProps) {
  return (
    <section className="mt-10">
      <h2 className="text-xl font-bold text-gray-900">전체 의견 그룹</h2>

      <div className="mt-4 flex flex-col gap-3">
        {groups.map((group) => (
          <button
            key={group.cluster_id}
            type="button"
            className="flex items-center justify-between rounded-2xl border border-gray-200 bg-white px-6 py-4 text-left shadow-sm transition hover:border-blue-400 hover:bg-blue-50"
          >
            <span className="font-semibold text-gray-800">{group.label}</span>
            <span className="text-sm text-gray-500">{group.count}건</span>
          </button>
        ))}
      </div>
    </section>
  );
}