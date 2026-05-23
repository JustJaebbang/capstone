import Link from "next/link";
import SentimentRatio from "@/components/SentimentRatio";
import ElementScoreChart from "@/components/ElementScoreChart";
import ResultReviewSection from "@/components/ResultReviewSection";
import { getFinalResult, getOpinionGroups } from "@/lib/api";
import { fetchElementScores } from "@/lib/element-scores";

type ResultPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

type ApiFinalResult = {
  job_id?: string;
  movie_id?: string;
  movie_title?: string;
  summary: {
    sentiment_ratio: {
      positive_percent: number;
      negative_percent: number;
      positive_review_count?: number;
      negative_review_count?: number;
      tie_review_count?: number;
      total_review_count?: number;
      rule?: string;
    };
  };
};

type ApiOpinionGroup = {
  cluster_id: string | number;
  label: string;
  count: number;
};

type OpinionGroupsResponse =
  | ApiOpinionGroup[]
  | {
      items?: ApiOpinionGroup[];
      groups?: ApiOpinionGroup[];
      total_count?: number;
    };

type ViewOpinionGroup = {
  cluster_id: string;
  label: string;
  count: number;
};

function normalizeOpinionGroups(
  response: OpinionGroupsResponse
): ViewOpinionGroup[] {
  const groups = Array.isArray(response)
    ? response
    : response.items ?? response.groups ?? [];

  return groups
    .map((group) => ({
      cluster_id: String(group.cluster_id),
      label: group.label,
      count: group.count,
    }))
    .sort((a, b) => b.count - a.count);
}

export default async function ResultPage({ params }: ResultPageProps) {
  const { jobId } = await params;

  const [finalResultRaw, opinionGroupsRaw, elementScores] = await Promise.all([
    getFinalResult(jobId),
    getOpinionGroups(jobId),
    fetchElementScores(jobId),
  ]);
  const finalResult = finalResultRaw as ApiFinalResult;
  const opinionGroupsResponse = opinionGroupsRaw as OpinionGroupsResponse;

  const opinionGroups = normalizeOpinionGroups(opinionGroupsResponse);
  const sentimentRatio = finalResult.summary.sentiment_ratio;

  const effectiveJobId = finalResult.job_id ?? jobId;

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto w-full max-w-5xl">
        <Link
          href="/movies"
          className="text-sm font-semibold text-blue-600 hover:underline"
        >
          ← 영화 목록으로
        </Link>

        <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <p className="text-sm font-semibold text-blue-600">
            Analysis Result
          </p>

          <h1 className="mt-2 text-3xl font-bold text-gray-900">
            분석 결과 보기
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Job ID: {effectiveJobId}
          </p>

          {finalResult.movie_title && (
            <p className="mt-1 text-sm text-gray-500">
              영화: {finalResult.movie_title}
            </p>
          )}

          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <SentimentRatio
              positivePercent={sentimentRatio.positive_percent}
              negativePercent={sentimentRatio.negative_percent}
            />

            <ElementScoreChart
              scores={elementScores}
              totalReviewCount={sentimentRatio.total_review_count ?? null}
            />
          </div>

          <ResultReviewSection jobId={effectiveJobId} groups={opinionGroups} />
        </section>
      </div>
    </main>
  );
}