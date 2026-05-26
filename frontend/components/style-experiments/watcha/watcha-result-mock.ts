// Static mock data for the Watcha result style-experiment page.
// This page is a showcase; real /jobs/[jobId]/result still uses the live API.

export type WatchaMockSentiment = "positive" | "negative" | "neutral";

export type WatchaMockOpinionGroup = {
  cluster_id: string;
  label: string;
  count: number;
  sentiment: WatchaMockSentiment;
};

export type WatchaMockReview = {
  id: string;
  text: string;
  sentiment: WatchaMockSentiment;
};

export type WatchaResultMock = {
  movie: {
    id: string;
    title: string;
    source: string;
    release_date: string;
    release_year: number;
    genres: string[];
    poster_seed: string;
    job_id: string;
    completed_at: string;
  };
  sentiment: {
    positive_percent: number;
    negative_percent: number;
    positive_review_count: number;
    negative_review_count: number;
    total_review_count: number;
  };
  opinion_groups: WatchaMockOpinionGroup[];
  reviews_by_cluster: Record<string, WatchaMockReview[]>;
};

export const WATCHA_RESULT_MOCK: WatchaResultMock = {
  movie: {
    id: "mv_001",
    title: "파묘",
    source: "naver",
    release_date: "2024.02.22",
    release_year: 2024,
    genres: ["미스터리", "스릴러", "오컬트"],
    poster_seed: "mv_001",
    job_id: "job_demo_001",
    completed_at: "2025-05-05T18:22:00+09:00",
  },
  sentiment: {
    positive_percent: 72,
    negative_percent: 28,
    positive_review_count: 895,
    negative_review_count: 348,
    total_review_count: 1243,
  },
  opinion_groups: [
    {
      cluster_id: "c1",
      label: "오정세의 연기가 압도적이었다",
      count: 312,
      sentiment: "positive",
    },
    {
      cluster_id: "c2",
      label: "후반부 전개가 다소 약했다",
      count: 276,
      sentiment: "negative",
    },
    {
      cluster_id: "c3",
      label: "분위기와 영상미가 인상적이었다",
      count: 198,
      sentiment: "positive",
    },
    {
      cluster_id: "c4",
      label: "한국형 오컬트의 새로운 시도",
      count: 142,
      sentiment: "positive",
    },
    {
      cluster_id: "c5",
      label: "스토리가 다소 난해하게 느껴졌다",
      count: 118,
      sentiment: "negative",
    },
    {
      cluster_id: "c6",
      label: "음악과 사운드가 몰입감을 높였다",
      count: 96,
      sentiment: "positive",
    },
    {
      cluster_id: "c7",
      label: "기대보다 무섭지 않았다",
      count: 84,
      sentiment: "negative",
    },
    {
      cluster_id: "c8",
      label: "끝맺음이 깔끔하지 않았다",
      count: 67,
      sentiment: "negative",
    },
  ],
  reviews_by_cluster: {
    c1: [
      { id: "r1-1", text: "오정세 배우의 연기가 진짜 압권. 그 장면 하나로 영화 전체가 살아나는 느낌이었습니다.", sentiment: "positive" },
      { id: "r1-2", text: "조연들도 다들 좋았지만 오정세는 완전히 다른 차원의 연기를 보여줬어요.", sentiment: "positive" },
      { id: "r1-3", text: "광기가 도는 듯한 표정에 소름이 끼쳤다. 한국 배우 중에 이런 결을 가진 사람이 또 있을까.", sentiment: "positive" },
      { id: "r1-4", text: "베테랑 배우들이 모인 작품인데도 오정세가 압도하는 장면이 많았다.", sentiment: "positive" },
      { id: "r1-5", text: "그 굿판 신은 한국 영화사에 남을 명장면.", sentiment: "positive" },
      { id: "r1-6", text: "최민식, 유해진의 호흡도 좋았지만 오정세의 등장이 영화의 결정타.", sentiment: "positive" },
    ],
    c2: [
      { id: "r2-1", text: "초반 분위기는 정말 좋은데 후반부터 힘이 빠지는 느낌이 들었어요.", sentiment: "negative" },
      { id: "r2-2", text: "마지막 30분이 좀 늘어진다. 편집이 한 번 더 손봤으면 어땠을까.", sentiment: "negative" },
      { id: "r2-3", text: "결말이 너무 빨리 정리되어서 아쉬웠습니다.", sentiment: "negative" },
      { id: "r2-4", text: "후반 전개가 어느 정도 예상 가능해져서 긴장감이 떨어졌다.", sentiment: "negative" },
      { id: "r2-5", text: "2부 시작 후부터 이야기가 산만해진다는 인상.", sentiment: "negative" },
    ],
    c3: [
      { id: "r3-1", text: "영상미가 정말 좋았다. 색감이랑 구도 모두 예술 수준.", sentiment: "positive" },
      { id: "r3-2", text: "촬영이 아름다워서 큰 화면으로 보길 잘했다는 생각.", sentiment: "positive" },
      { id: "r3-3", text: "안개와 어둠의 활용이 인상적이었음. 분위기 호러의 정석.", sentiment: "positive" },
      { id: "r3-4", text: "한 컷 한 컷이 포스터 같았다.", sentiment: "positive" },
    ],
    c4: [
      { id: "r4-1", text: "한국 오컬트의 새로운 시도라는 점에서 의미가 큰 작품.", sentiment: "positive" },
      { id: "r4-2", text: "전통과 미신을 잘 녹여낸 스토리. K-호러의 가능성을 봤다.", sentiment: "positive" },
      { id: "r4-3", text: "낯선 소재인데도 거부감 없이 잘 풀어냈다.", sentiment: "positive" },
    ],
    c5: [
      { id: "r5-1", text: "용어가 어려워서 따라가기 힘들었어요.", sentiment: "negative" },
      { id: "r5-2", text: "사전 지식이 좀 필요한 영화. 모르고 보면 헷갈리는 부분이 있다.", sentiment: "negative" },
      { id: "r5-3", text: "설명이 적어서 두 번 봐야 이해되는 장면이 있었음.", sentiment: "negative" },
    ],
    c6: [
      { id: "r6-1", text: "사운드 디자인이 굉장함. IMAX로 보길 강력 추천합니다.", sentiment: "positive" },
      { id: "r6-2", text: "음악이 분위기를 만드는 결정적인 요소였어요.", sentiment: "positive" },
      { id: "r6-3", text: "효과음 하나하나가 신경 쓰여서 더 무섭게 느껴졌다.", sentiment: "positive" },
    ],
    c7: [
      { id: "r7-1", text: "공포 영화로 기대했는데 그렇게 무섭진 않았어요.", sentiment: "negative" },
      { id: "r7-2", text: "분위기 호러에 가깝고 점프 스케어는 거의 없다.", sentiment: "negative" },
      { id: "r7-3", text: "무서운 영화를 원했다면 다른 선택이 나을 듯.", sentiment: "negative" },
    ],
    c8: [
      { id: "r8-1", text: "결말이 좀 아쉬워서 별점을 깎았어요.", sentiment: "negative" },
      { id: "r8-2", text: "끝맺음에 여운보다는 의문이 더 남았다.", sentiment: "negative" },
      { id: "r8-3", text: "마무리만 다듬었어도 더 좋은 평을 받았을 작품.", sentiment: "negative" },
    ],
  },
};
