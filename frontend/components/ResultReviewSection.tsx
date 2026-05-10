"use client";

import { useEffect, useState } from "react";
import ReviewList from "@/components/ReviewList";
import Pagination from "@/components/Pagination";

type OpinionGroup = {
  cluster_id: string;
  label: string;
  count: number;
};

type Review = {
  id: string;
  text: string;
  sentiment: "positive" | "negative" | "neutral";
};

type ResultReviewSectionProps = {
  jobId: string;
  groups: OpinionGroup[];
};

type ReviewsApiItem = {
  review_id?: string;
  id?: string;
  text?: string;
  review_text?: string;
  sentiment?: "positive" | "negative" | "neutral" | string;
};

type ReviewsApiResponse =
  | ReviewsApiItem[]
  | {
      reviews?: ReviewsApiItem[];
      items?: ReviewsApiItem[];
      total_count?: number;
      total_pages?: number;
      page?: number;
      page_size?: number;
    };

const PAGE_SIZE = 5;

function normalizeReviews(response: ReviewsApiResponse): {
  reviews: Review[];
  totalCount: number;
  totalPages: number;
} {
  const rawReviews = Array.isArray(response)
    ? response
    : response.reviews ?? response.items ?? [];

  const reviews: Review[] = rawReviews.map((review, index) => ({
    id: review.review_id ?? review.id ?? `review-${index}`,
    text: review.text ?? review.review_text ?? "",
    sentiment:
      review.sentiment === "positive" ||
      review.sentiment === "negative" ||
      review.sentiment === "neutral"
        ? review.sentiment
        : "neutral",
  }));

  const totalCount = Array.isArray(response)
    ? reviews.length
    : response.total_count ?? reviews.length;

  const totalPages = Array.isArray(response)
    ? Math.max(1, Math.ceil(reviews.length / PAGE_SIZE))
    : response.total_pages ?? Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return {
    reviews,
    totalCount,
    totalPages,
  };
}

export default function ResultReviewSection({
  jobId,
  groups,
}: ResultReviewSectionProps) {
  const [selectedClusterId, setSelectedClusterId] = useState<string | null>(
    null
  );
  const [pageByCluster, setPageByCluster] = useState<Record<string, number>>({});
  const [reviews, setReviews] = useState<Review[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const selectedGroup = groups.find(
    (group) => group.cluster_id === selectedClusterId
  );

  const currentPage = selectedClusterId
    ? pageByCluster[selectedClusterId] ?? 1
    : 1;

  const handleSelectGroup = (clusterId: string) => {
    setSelectedClusterId((current) => {
      if (current === clusterId) {
        return null;
      }

      return clusterId;
    });

    setPageByCluster((current) => ({
      ...current,
      [clusterId]: current[clusterId] ?? 1,
    }));
  };

  const setPage = (clusterId: string, nextPage: number) => {
    setPageByCluster((current) => ({
      ...current,
      [clusterId]: nextPage,
    }));
  };

  useEffect(() => {
    if (!selectedClusterId) {
      setReviews([]);
      setTotalCount(0);
      setTotalPages(1);
      setErrorMessage(null);
      return;
    }

    const clusterId = selectedClusterId;

    async function fetchReviews() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const apiUrl = `/api/reviews?jobId=${encodeURIComponent(
          jobId
        )}&clusterId=${encodeURIComponent(
          clusterId
        )}&page=${currentPage}&pageSize=${PAGE_SIZE}`;

        const res = await fetch(apiUrl, {
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error(`리뷰 API 요청 실패: ${res.status}`);
        }

        const data = (await res.json()) as ReviewsApiResponse;
        const normalized = normalizeReviews(data);

        setReviews(normalized.reviews);
        setTotalCount(normalized.totalCount);
        setTotalPages(normalized.totalPages);
      } catch (error) {
        setReviews([]);
        setTotalCount(0);
        setTotalPages(1);
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "리뷰를 불러오지 못했습니다."
        );
      } finally {
        setIsLoading(false);
      }
    }

    fetchReviews();
  }, [jobId, selectedClusterId, currentPage]);

  return (
    <section className="mt-10">
      <h2 className="text-xl font-bold text-gray-900">전체 의견 그룹</h2>
      <p className="mt-2 text-sm text-gray-500">
        의견 그룹을 선택하면 해당 그룹의 리뷰가 바로 아래에 펼쳐집니다.
      </p>

      <div className="mt-4 flex flex-col gap-3">
        {groups.map((group) => {
          const isSelected = group.cluster_id === selectedClusterId;

          return (
            <div
              key={group.cluster_id}
              className={`rounded-2xl border shadow-sm transition ${
                isSelected
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 bg-white"
              }`}
            >
              <button
                type="button"
                onClick={() => handleSelectGroup(group.cluster_id)}
                className="flex w-full items-center justify-between px-6 py-4 text-left"
              >
                <div>
                  <p className="font-semibold text-gray-900">{group.label}</p>
                  <p className="mt-1 text-xs text-gray-500">
                    클릭해서 관련 리뷰 보기
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-sm font-semibold text-gray-500">
                    {group.count}건
                  </span>
                  <span className="text-lg font-bold text-blue-600">
                    {isSelected ? "−" : "+"}
                  </span>
                </div>
              </button>

              {isSelected && selectedGroup && (
                <div className="border-t border-blue-100 bg-white px-6 py-5">
                  <div className="mb-4 flex items-end justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold text-blue-600">
                        Selected Opinion
                      </p>
                      <h3 className="mt-1 text-2xl font-bold text-gray-900">
                        {selectedGroup.label}
                      </h3>
                    </div>

                    <p className="text-sm font-semibold text-gray-500">
                      총 {totalCount}개 리뷰
                    </p>
                  </div>

                  {isLoading && (
                    <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6 text-gray-500">
                      리뷰를 불러오는 중입니다...
                    </div>
                  )}

                  {errorMessage && (
                    <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-600">
                      {errorMessage}
                    </div>
                  )}

                  {!isLoading && !errorMessage && (
                    <>
                      <ReviewList reviews={reviews} />

                      <Pagination
                        page={currentPage}
                        totalPages={totalPages}
                        onPrev={() =>
                          setPage(
                            group.cluster_id,
                            Math.max(1, currentPage - 1)
                          )
                        }
                        onNext={() =>
                          setPage(
                            group.cluster_id,
                            Math.min(totalPages, currentPage + 1)
                          )
                        }
                      />
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}