type Review = {
  id: string;
  text: string;
  sentiment: "positive" | "negative" | "neutral";
};

type ReviewListProps = {
  reviews: Review[];
};

function getSentimentEmoji(sentiment: Review["sentiment"]) {
  if (sentiment === "positive") return "😊";
  if (sentiment === "negative") return "🤔";
  return "😐";
}

function getSentimentLabel(sentiment: Review["sentiment"]) {
  if (sentiment === "positive") return "긍정";
  if (sentiment === "negative") return "부정";
  return "중립";
}

export default function ReviewList({ reviews }: ReviewListProps) {
  if (reviews.length === 0) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6 text-gray-500">
        표시할 리뷰가 없습니다.
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      {reviews.map((review, index) => (
        <div
          key={review.id}
          className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"
        >
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-semibold text-blue-600">
              리뷰 {index + 1}
            </p>
            <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-600">
              {getSentimentEmoji(review.sentiment)}{" "}
              {getSentimentLabel(review.sentiment)}
            </span>
          </div>

          <p className="leading-7 text-gray-700">{review.text}</p>
        </div>
      ))}
    </div>
  );
}