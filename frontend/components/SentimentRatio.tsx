type SentimentRatioProps = {
  positivePercent: number;
  negativePercent: number;
};

export default function SentimentRatio({
  positivePercent,
  negativePercent,
}: SentimentRatioProps) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
      <h2 className="text-lg font-bold text-gray-900">긍정 / 부정 비율</h2>

      <div className="mt-5">
        <div className="mb-2 flex justify-between text-sm font-semibold text-gray-700">
          <span>😊 긍정 {positivePercent}%</span>
          <span>🤔 부정 {negativePercent}%</span>
        </div>

        <div className="h-3 overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-blue-600"
            style={{
              width: `${positivePercent}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
}