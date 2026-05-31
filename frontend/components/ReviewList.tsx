type Review = {
  id: string;
  text: string;
};

type ReviewListProps = {
  reviews: Review[];
};

export default function ReviewList({ reviews }: ReviewListProps) {
  if (reviews.length === 0) {
    return (
      <div className="rounded-[8px] border border-[#e8e3d6] bg-[#fbf9f3] p-6 text-[#6b6760]">
        표시할 리뷰가 없습니다.
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      {reviews.map((review, index) => (
        <div
          key={review.id}
          className="rounded-[8px] border border-[#e8e3d6] bg-white p-5"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
            리뷰 {index + 1}
          </p>
          <p className="mt-2 leading-7 text-[#3d3a35]">{review.text}</p>
        </div>
      ))}
    </div>
  );
}