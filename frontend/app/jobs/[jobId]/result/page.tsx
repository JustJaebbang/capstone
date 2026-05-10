import Link from "next/link";
import SentimentRatio from "@/components/SentimentRatio";
import TopOpinions from "@/components/TopOpinions";
import ResultReviewSection from "@/components/ResultReviewSection";
import { getFinalResult, getOpinionGroups } from "@/lib/api";

type ResultPageProps = {
  params: Promise<{
    jobId: string;
  }>;
};

type ApiTopOpinion = {
  rank?: number;
  topic?: string;
  sentiment?: string;
  label: string;
  count: number;
};

type ApiFinalResult = {
  job_id?: string;
  movie_id?: string;
  movie_title?: string;
  summary: {
    top_opinions: ApiTopOpinion[];
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

  return groups.map((group) => ({
    cluster_id: String(group.cluster_id),
    label: group.label,
    count: group.count,
  }));
}

export default async function ResultPage({ params }: ResultPageProps) {
  const { jobId } = await params;

  const finalResult = (await getFinalResult(jobId)) as ApiFinalResult;
  const opinionGroupsResponse =
    (await getOpinionGroups(jobId)) as OpinionGroupsResponse;

  const opinionGroups = normalizeOpinionGroups(opinionGroupsResponse);
  const sentimentRatio = finalResult.summary.sentiment_ratio;

  // 핵심: ResultReviewSection에 undefined가 아니라 실제 job_id를 넘기기
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

            <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
              <h2 className="text-lg font-bold text-gray-900">요약</h2>

              <p className="mt-3 leading-7 text-gray-600">
                백엔드 API에서 불러온 최종 분석 결과입니다. 의견 그룹을
                선택하면 해당 그룹의 리뷰를 확인할 수 있습니다.
              </p>

              <p className="mt-4 text-sm font-semibold text-gray-500">
                분석 리뷰 수: {sentimentRatio.total_review_count ?? "-"}개
              </p>
            </div>
          </div>

          <TopOpinions opinions={finalResult.summary.top_opinions} />

          <ResultReviewSection jobId={effectiveJobId} groups={opinionGroups} />
        </section>
      </div>
    </main>
  );
}