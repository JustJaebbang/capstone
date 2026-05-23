"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import WatchaFontStyles from "@/components/style-experiments/watcha/WatchaFontStyles";

const TOTAL_REVIEWS = 1243;
const TOTAL_DURATION_MS = 6800;

type StageState = "pending" | "active" | "complete";

type Stage = {
  code: string;
  name: string;
  sub: string;
  engine: string;
};

const STAGES: Stage[] = [
  {
    code: "01",
    name: "리뷰 수집 · 의견 추출",
    sub: "LLM이 한 문장씩 의견 조각으로 분해합니다.",
    engine: "openai · prompt v3",
  },
  {
    code: "02",
    name: "유사 의견 군집화",
    sub: "HDBSCAN이 비슷한 목소리를 한 무리로 묶습니다.",
    engine: "hdbscan · minilm-l6",
  },
  {
    code: "03",
    name: "결과 합성 · 시각화 빌드",
    sub: "감성 비율과 키워드 순위를 최종 결과 객체로 합칩니다.",
    engine: "build-final · v1",
  },
];

const TIPS = [
  "“숫자는 합의의 결과이고, 키워드는 합의되지 않은 의견의 목록이다.”",
  "“리뷰는 별점 뒤에 숨는다 — 별점은 의견을 가린다.”",
  "“군집은 합의가 아니라, 같은 방향으로 향한 다수의 목소리다.”",
];

function posterGradient(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  const palettes: Array<[string, string, string]> = [
    ["#1a1424", "#3b1a3f", "#0d0810"],
    ["#0e1f1c", "#1e3f3a", "#070f0d"],
    ["#2a1a14", "#5a2a1a", "#180a05"],
    ["#0d172a", "#1e2a4a", "#05080f"],
  ];
  const [a, b, c] = palettes[h % palettes.length];
  return `radial-gradient(120% 80% at 20% 0%, ${a} 0%, ${b} 55%, ${c} 100%)`;
}

export default function WatchaAnalyzingPage() {
  const [progress, setProgress] = useState(0);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const id = window.setInterval(() => {
      const e = Date.now() - start;
      setElapsedMs(e);
      const pct = Math.min(100, (e / TOTAL_DURATION_MS) * 100);
      setProgress(pct);
      if (pct >= 100) {
        window.clearInterval(id);
      }
    }, 100);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    const id = window.setInterval(
      () => setTipIndex((i) => (i + 1) % TIPS.length),
      4200,
    );
    return () => window.clearInterval(id);
  }, []);

  const stageThreshold = 100 / STAGES.length;
  const stageStates: StageState[] = STAGES.map((_, idx) => {
    const start = idx * stageThreshold;
    const end = (idx + 1) * stageThreshold;
    if (progress >= end) return "complete";
    if (progress >= start) return "active";
    return "pending";
  });

  const overallSeconds = (elapsedMs / 1000).toFixed(1);
  const reviewsDone = Math.min(
    TOTAL_REVIEWS,
    Math.floor((progress / 100) * TOTAL_REVIEWS),
  );
  const isComplete = progress >= 100;

  return (
    <main className="min-h-screen bg-[#fbf9f3] text-[#161616] antialiased selection:bg-[#ff2c63]/85 selection:text-white">
      <WatchaFontStyles />

      <div className="watcha-page flex min-h-screen flex-col">
        {/* Top nav */}
        <header className="border-b border-[#e8e3d6]">
          <div className="mx-auto flex max-w-[1240px] items-center justify-between px-8 py-5">
            <Link
              href="/style-experiments/watcha"
              className="flex items-baseline gap-1"
            >
              <span className="font-serif text-[24px] font-medium tracking-[-0.02em] text-[#161616]">
                review
              </span>
              <span className="font-serif text-[24px] italic font-medium text-[#ff2c63]">
                pedia
              </span>
              <span className="ml-2 hidden font-mono text-[10px] uppercase tracking-[0.24em] text-[#9a958b] sm:inline">
                / live
              </span>
            </Link>
            <div className="flex items-center gap-3">
              <span className="hidden font-mono text-[11px] uppercase tracking-[0.18em] text-[#9a958b] md:inline">
                {isComplete ? "ready · 결과 도착" : "live · daily batch"}
              </span>
              <Link
                href="/style-experiments/watcha"
                className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6760] hover:bg-[#f0ece0]"
              >
                ← 대시보드
              </Link>
            </div>
          </div>
        </header>

        {/* Body */}
        <section className="flex-1 border-b border-[#e8e3d6]">
          <div className="mx-auto grid max-w-[1240px] grid-cols-1 gap-14 px-8 py-20 lg:grid-cols-[0.95fr_1.05fr] lg:gap-20 lg:py-24">
            {/* Left — poster + meta */}
            <div className="flex flex-col">
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                Now Processing · job_demo_001
              </p>
              <h1 className="mt-5 font-serif text-[52px] font-normal leading-[1.04] tracking-[-0.025em] text-[#161616] sm:text-[64px]">
                관객의 목소리를
                <br />
                <span className="italic text-[#ff2c63]">읽는 중</span>입니다.
              </h1>
              <p className="mt-5 max-w-[440px] text-[15px] leading-[1.7] text-[#3d3a35]">
                약 30초 안에 결과가 도착합니다. 같은 문장 속에 섞인 의견을
                나누고, 비슷한 의견은 하나의 군집으로 묶습니다.
              </p>

              {/* Poster */}
              <div
                className="relative mt-10 aspect-[3/4] w-full max-w-[340px] overflow-hidden rounded-[10px] shadow-[0_24px_50px_-18px_rgba(20,15,5,0.4)]"
                style={{ background: posterGradient("mv_001") }}
              >
                <div
                  aria-hidden
                  className="pointer-events-none absolute inset-0 opacity-[0.16] mix-blend-overlay"
                  style={{
                    backgroundImage:
                      "radial-gradient(rgba(255,255,255,0.55) 1px, transparent 1px)",
                    backgroundSize: "3px 3px",
                  }}
                />
                <div className="absolute inset-0 flex flex-col justify-between p-8">
                  <div className="flex items-start justify-between">
                    <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-white/55">
                      이 작품
                    </p>
                    <span className="rounded-full bg-white/10 px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-white/80 backdrop-blur">
                      naver
                    </span>
                  </div>
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-white/55">
                      2024.02.22 · 미스터리 · 스릴러
                    </p>
                    <h2 className="mt-3 font-serif text-[52px] font-medium leading-[1.02] tracking-[-0.025em] text-white">
                      파묘
                    </h2>
                  </div>
                </div>

                {/* Bottom live-shimmer band — stops when complete */}
                <div className="pointer-events-none absolute inset-x-0 bottom-0 h-[3px] bg-white/10">
                  {!isComplete && (
                    <div className="h-full watcha-shimmer" />
                  )}
                </div>
              </div>

              <div className="mt-6 grid max-w-[340px] grid-cols-3 gap-5 border-t border-[#e8e3d6] pt-5">
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                    총 리뷰
                  </p>
                  <p className="mt-1.5 font-serif text-[22px] leading-none text-[#161616] tabular-nums">
                    {TOTAL_REVIEWS.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                    처리됨
                  </p>
                  <p className="mt-1.5 font-serif text-[22px] leading-none text-[#ff2c63] tabular-nums">
                    {reviewsDone.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#9a958b]">
                    경과
                  </p>
                  <p className="mt-1.5 font-serif text-[22px] leading-none text-[#161616] tabular-nums">
                    {overallSeconds}s
                  </p>
                </div>
              </div>
            </div>

            {/* Right — stage timeline */}
            <div>
              <ol className="space-y-4">
                {STAGES.map((stage, idx) => {
                  const state = stageStates[idx];
                  const stageStart = idx * stageThreshold;
                  const stageEnd = (idx + 1) * stageThreshold;
                  const localProgress =
                    state === "complete"
                      ? 100
                      : state === "active"
                      ? Math.max(
                          0,
                          Math.min(
                            100,
                            ((progress - stageStart) /
                              (stageEnd - stageStart)) *
                              100,
                          ),
                        )
                      : 0;

                  return (
                    <li
                      key={stage.code}
                      className={`relative rounded-[10px] border p-7 transition-all duration-500 ${
                        state === "active"
                          ? "border-[#ff2c63]/35 bg-white shadow-[0_14px_28px_-18px_rgba(20,15,5,0.25)]"
                          : state === "complete"
                          ? "border-[#e8e3d6] bg-[#f5f1e6]/60"
                          : "border-dashed border-[#dcd6c5] bg-transparent opacity-60"
                      }`}
                    >
                      <div className="flex items-start gap-5">
                        {/* dot indicator */}
                        <div
                          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
                          style={{
                            background:
                              state === "active"
                                ? "#ffe8ef"
                                : state === "complete"
                                ? "#dff1e6"
                                : "#f0ece0",
                          }}
                        >
                          {state === "complete" ? (
                            <span className="font-mono text-[14px] font-medium text-[#1a7a4a]">
                              ✓
                            </span>
                          ) : (
                            <span
                              className={`block h-2 w-2 rounded-full ${
                                state === "active" ? "watcha-pulse-dot" : ""
                              }`}
                              style={{
                                background:
                                  state === "active" ? "#ff2c63" : "#9a958b",
                              }}
                            />
                          )}
                        </div>

                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                            <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
                              stage · {stage.code}
                            </span>
                            <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                              · {stage.engine}
                            </span>
                          </div>
                          <h3 className="mt-1.5 font-serif text-[26px] font-medium leading-tight tracking-[-0.015em] text-[#161616]">
                            {stage.name}
                          </h3>
                          <p className="mt-2 text-[14px] leading-[1.6] text-[#3d3a35]">
                            {stage.sub}
                          </p>

                          {/* progress bar */}
                          <div className="mt-4 flex h-[3px] w-full overflow-hidden rounded-full bg-[#efe9d8]">
                            <div
                              className="h-full transition-[width] duration-500 ease-out"
                              style={{
                                width: `${localProgress}%`,
                                background:
                                  state === "complete" ? "#27ae60" : "#ff2c63",
                              }}
                            />
                          </div>

                          <p className="mt-3 font-mono text-[11px] tabular-nums text-[#6b6760]">
                            {state === "complete"
                              ? `완료 · ${TOTAL_REVIEWS.toLocaleString()}건 처리됨`
                              : state === "active"
                              ? `처리 중 · ${Math.floor(
                                  (localProgress / 100) * TOTAL_REVIEWS,
                                ).toLocaleString()} / ${TOTAL_REVIEWS.toLocaleString()}건`
                              : "대기 중"}
                          </p>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ol>

              {/* Tip + CTA */}
              <div className="mt-10 flex flex-col items-start justify-between gap-6 border-t border-[#e8e3d6] pt-8 md:flex-row md:items-end">
                <p
                  key={tipIndex}
                  className="watcha-fade-up max-w-[480px] font-serif text-[16px] italic leading-[1.6] text-[#6b6760]"
                >
                  {TIPS[tipIndex]}
                </p>
                {isComplete ? (
                  <Link
                    href="/style-experiments/watcha/result"
                    className="watcha-fade-up inline-flex items-center gap-2 rounded-full bg-[#ff2c63] px-6 py-3 text-[14px] font-medium tracking-tight text-white transition-colors hover:bg-[#161616]"
                  >
                    결과 보기 <span className="font-mono">→</span>
                  </Link>
                ) : (
                  <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[#9a958b] tabular-nums">
                    elapsed · {overallSeconds}s · {Math.round(progress)}%
                  </p>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Slim footer */}
        <footer className="bg-[#161616] py-6 text-[#fbf9f3]">
          <div className="mx-auto flex max-w-[1240px] flex-col items-start justify-between gap-2 px-8 font-mono text-[10px] uppercase tracking-[0.22em] text-[#fbf9f3]/40 sm:flex-row sm:items-center">
            <span>review.pedia · live analysis</span>
            <span>movie review pipeline · daily edition</span>
          </div>
        </footer>
      </div>
    </main>
  );
}
