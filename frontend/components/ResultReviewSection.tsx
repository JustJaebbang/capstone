"use client";

import { useEffect, useState } from "react";
import ReviewList from "@/components/ReviewList";
import Pagination from "@/components/Pagination";

type OpinionGroup = {
  cluster_id: string;
  label: string;
  count: number;
  sentiment?: "positive" | "negative";
};

type Review = {
  id: string;
  text: string;
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

function sentimentLabel(sentiment?: "positive" | "negative") {
  if (sentiment !== "positive" && sentiment !== "negative") return null;
  const isPos = sentiment === "positive";
  return (
    <span
      className={`font-mono text-[10px] uppercase tracking-[0.2em] ${
        isPos ? "text-[#ff2c63]" : "text-[#6b6760]"
      }`}
    >
      {isPos ? "긍정" : "부정"}
    </span>
  );
}

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
  const [pageByCluster, setPageByCluster] = useState<Record<string, number>>(
    {}
  );
  const [reviews, setReviews] = useState<Review[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 상위 3개 = TOP 3, 나머지 = 그 외
  const sortedGroups = [...groups].sort((a, b) => b.count - a.count);
  const topThree = sortedGroups.slice(0, 3);
  const restGroups = sortedGroups.slice(3);

  const selectedGroup = sortedGroups.find(
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

  // 펼침 영역 컴포넌트 (TOP 3와 하단에서 공통 사용)
  const renderExpandedReviews = (group: OpinionGroup) => (
    <div className="mt-4 rounded-[10px] border border-[#e8e3d6] bg-white p-7">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
            Selected Opinion
          </p>
          <div className="mt-1.5 flex items-baseline gap-3">
            <h3 className="font-serif text-[26px] font-medium text-[#161616]">
              {group.label}
            </h3>
            {sentimentLabel(group.sentiment)}
          </div>
        </div>
        <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760] tabular-nums">
          총 {totalCount}개 리뷰
        </p>
      </div>

      {isLoading && (
        <div className="rounded-[8px] border border-[#e8e3d6] bg-[#fbf9f3] p-6 text-[#6b6760]">
          리뷰를 불러오는 중입니다...
        </div>
      )}

      {errorMessage && (
        <div className="rounded-[8px] border border-[#e6c4cb] bg-[#fdf3f5] p-6 text-sm font-medium text-[#c0392b]">
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
              setPage(group.cluster_id, Math.max(1, currentPage - 1))
            }
            onNext={() =>
              setPage(group.cluster_id, Math.min(totalPages, currentPage + 1))
            }
          />
        </>
      )}
    </div>
  );

  const isTopSelected =
    selectedGroup && topThree.some((g) => g.cluster_id === selectedGroup.cluster_id);

  return (
    <>
      {/* 상단: 많이 나온 의견 TOP 3 */}
      <section className="mt-10">
        <h2 className="font-serif text-[24px] font-medium text-[#161616]">많이 나온 의견 TOP 3</h2>

        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {topThree.map((group, index) => {
            const isSelected = group.cluster_id === selectedClusterId;
            return (
              <button
                key={group.cluster_id}
                type="button"
                onClick={() => handleSelectGroup(group.cluster_id)}
                className={`rounded-[10px] border p-6 text-left transition ${
                  isSelected
                    ? "border-[#ff2c63] bg-[#fbf9f3]"
                    : "border-[#e8e3d6] bg-white hover:border-[#dcd6c5]"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                    {index + 1}위
                  </span>
                  {sentimentLabel(group.sentiment)}
                </div>
                <h3 className="mt-3 font-serif text-[20px] font-medium text-[#161616]">
                  {group.label}
                </h3>
                <p className="mt-2 font-mono text-[11px] tracking-tight text-[#6b6760] tabular-nums">
                  {group.count}건
                </p>
              </button>
            );
          })}
        </div>

        {/* TOP 3 중 하나가 선택되면 바로 아래에 리뷰 펼침 */}
        {isTopSelected && selectedGroup && renderExpandedReviews(selectedGroup)}
      </section>

      {/* 하단: 그 외 의견 그룹 */}
      {restGroups.length > 0 && (
        <section className="mt-10">
          <h2 className="font-serif text-[24px] font-medium text-[#161616]">그 외 의견 그룹</h2>
          <p className="mt-2 text-sm text-[#6b6760]">
            의견 그룹을 선택하면 해당 그룹의 리뷰가 바로 아래에 펼쳐집니다.
          </p>

          <div className="mt-4 flex flex-col gap-3">
            {restGroups.map((group) => {
              const isSelected = group.cluster_id === selectedClusterId;

              return (
                <div
                  key={group.cluster_id}
                  className={`rounded-[10px] border transition ${
                    isSelected
                      ? "border-[#ff2c63] bg-[#fbf9f3]"
                      : "border-[#e8e3d6] bg-white"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => handleSelectGroup(group.cluster_id)}
                    className="flex w-full items-center justify-between px-6 py-4 text-left"
                  >
                    <div>
                      <div className="flex items-baseline gap-3">
                        <p className="font-serif text-[17px] font-medium text-[#161616]">
                          {group.label}
                        </p>
                        {sentimentLabel(group.sentiment)}
                      </div>
                      <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                        클릭해서 관련 리뷰 보기
                      </p>
                    </div>

                    <div className="flex items-center gap-4">
                      <span className="font-mono text-[11px] tracking-tight text-[#6b6760] tabular-nums">
                        {group.count}건
                      </span>
                      <span className="text-lg font-medium text-[#ff2c63]">
                        {isSelected ? "−" : "+"}
                      </span>
                    </div>
                  </button>

                  {isSelected && renderExpandedReviews(group)}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </>
  );
}