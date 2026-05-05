type PaginationProps = {
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
};

export default function Pagination({
  page,
  totalPages,
  onPrev,
  onNext,
}: PaginationProps) {
  return (
    <div className="mt-5 flex items-center justify-between">
      <button
        type="button"
        onClick={onPrev}
        disabled={page <= 1}
        className="rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 disabled:cursor-not-allowed disabled:opacity-40 hover:bg-gray-100"
      >
        ← 이전
      </button>

      <p className="text-sm font-semibold text-gray-600">
        Page {page} / {totalPages}
      </p>

      <button
        type="button"
        onClick={onNext}
        disabled={page >= totalPages}
        className="rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 disabled:cursor-not-allowed disabled:opacity-40 hover:bg-gray-100"
      >
        다음 →
      </button>
    </div>
  );
}