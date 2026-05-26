import type { ElementScore } from "./types";

import elementScoresMock from "./mock/element-scores.json";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// 백엔드 API가 준비될 때까지 mock 사용.
// .env에 NEXT_PUBLIC_USE_MOCK_ELEMENT_SCORES=false 를 넣으면 실제 API 호출.
const USE_MOCK =
  process.env.NEXT_PUBLIC_USE_MOCK_ELEMENT_SCORES !== "false";

/**
 * 영화 요소별 점수(스토리/연기/몰입감/전개/재미/연출 등)를 조회.
 * 현재는 mock 데이터를 반환하고, 백엔드 엔드포인트가 준비되면
 * 동일한 시그니처로 실제 API 호출로 교체할 수 있다.
 */
export async function fetchElementScores(
  jobId: string,
): Promise<ElementScore[]> {
  if (USE_MOCK) {
    return elementScoresMock as ElementScore[];
  }

  const res = await fetch(
    `${BASE_URL}/batch/jobs/${encodeURIComponent(jobId)}/element-scores`,
    {
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
    },
  );
  if (!res.ok) {
    throw new Error(`요소별 점수 조회 실패: ${res.status}`);
  }
  return res.json();
}
