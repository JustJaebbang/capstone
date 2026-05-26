"use client";

import { useMemo, useState } from "react";

import type {
  WatchaMockOpinionGroup,
  WatchaMockReview,
  WatchaMockSentiment,
} from "./watcha-result-mock";

type Props = {
  groups: WatchaMockOpinionGroup[];
  reviewsByCluster: Record<string, WatchaMockReview[]>;
};

const PAGE_SIZE = 4;

const sentimentTone: Record<
  WatchaMockSentiment,
  { ink: string; bg: string; label: string; bar: string }
> = {
  positive: {
    ink: "#a8174b",
    bg: "#fdeaf0",
    label: "긍정 우세",
    bar: "#ff2c63",
  },
  negative: {
    ink: "#0f4c5c",
    bg: "#e0ecf0",
    label: "부정 우세",
    bar: "#0f4c5c",
  },
  neutral: {
    ink: "#5a564f",
    bg: "#ece8db",
    label: "의견 분기",
    bar: "#9a958b",
  },
};

const reviewChipTone: Record<
  WatchaMockSentiment,
  { ink: string; bg: string; label: string }
> = {
  positive: { ink: "#a8174b", bg: "#fdeaf0", label: "긍정" },
  negative: { ink: "#0f4c5c", bg: "#e0ecf0", label: "부정" },
  neutral: { ink: "#5a564f", bg: "#ece8db", label: "중립" },
};

export default function WatchaResultBody({ groups, reviewsByCluster }: Props) {
  const sorted = useMemo(
    () => [...groups].sort((a, b) => b.count - a.count),
    [groups],
  );
  const total = useMemo(
    () => sorted.reduce((s, g) => s + g.count, 0) || 1,
    [sorted],
  );

  const topThree = sorted.slice(0, 3);
  const rest = sorted.slice(3);

  const [selectedClusterId, setSelectedClusterId] = useState<string | null>(
    topThree[0]?.cluster_id ?? null,
  );
  const [pageByCluster, setPageByCluster] = useState<Record<string, number>>(
    {},
  );

  const selectedGroup = sorted.find(
    (g) => g.cluster_id === selectedClusterId,
  );

  const currentPage = selectedClusterId
    ? pageByCluster[selectedClusterId] ?? 1
    : 1;

  const handleSelect = (clusterId: string) => {
    setSelectedClusterId((current) =>
      current === clusterId ? null : clusterId,
    );
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

  const isTopSelected =
    selectedGroup &&
    topThree.some((g) => g.cluster_id === selectedGroup.cluster_id);

  const renderExpandedReviews = (group: WatchaMockOpinionGroup) => {
    const reviews = reviewsByCluster[group.cluster_id] ?? [];
    const totalCount = reviews.length;
    const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
    const page = Math.min(totalPages, Math.max(1, currentPage));
    const start = (page - 1) * PAGE_SIZE;
    const visible = reviews.slice(start, start + PAGE_SIZE);
    const tone = sentimentTone[group.sentiment];

    return (
      <div className="watcha-fade-up mt-6 rounded-[10px] border border-[#e8e3d6] bg-white p-8 shadow-[0_18px_38px_-22px_rgba(20,15,5,0.25)]">
        <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3 border-b border-[#e8e3d6] pb-5">
          <div className="min-w-0">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
              Selected Opinion · {group.cluster_id}
            </p>
            <h4 className="mt-2 font-serif text-[28px] font-medium leading-tight tracking-[-0.015em] text-[#161616]">
              {group.label}
            </h4>
            <div className="mt-3 flex items-center gap-3">
              <span
                className="rounded-full px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.18em]"
                style={{ background: tone.bg, color: tone.ink }}
              >
                {tone.label}
              </span>
              <span className="font-mono text-[11px] tabular-nums text-[#6b6760]">
                전체의 {Math.round((group.count / total) * 100)}%
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="font-serif text-[34px] leading-none text-[#161616] tabular-nums">
              {group.count.toLocaleString()}
            </p>
            <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
              mentions · {totalCount}건 리뷰
            </p>
          </div>
        </div>

        {/* Review list */}
        {visible.length === 0 ? (
          <p className="mt-6 text-[14px] text-[#6b6760]">
            이 군집에 표시할 리뷰가 없습니다.
          </p>
        ) : (
          <ul className="mt-6 space-y-4">
            {visible.map((r, i) => {
              const chip = reviewChipTone[r.sentiment];
              const globalIndex = start + i + 1;
              return (
                <li
                  key={r.id}
                  className="rounded-[8px] border border-[#efe9d8] bg-[#fbf9f3]/60 p-5 transition-colors hover:bg-white"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-[#9a958b]">
                      review · {String(globalIndex).padStart(2, "0")}
                    </p>
                    <span
                      className="rounded-full px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.18em]"
                      style={{ background: chip.bg, color: chip.ink }}
                    >
                      {chip.label}
                    </span>
                  </div>
                  <p className="font-serif text-[17px] leading-[1.7] tracking-[-0.005em] text-[#161616]">
                    <span className="mr-1.5 font-serif text-[20px] italic text-[#ff2c63]/70">
                      &ldquo;
                    </span>
                    {r.text}
                    <span className="ml-1 font-serif text-[20px] italic text-[#ff2c63]/70">
                      &rdquo;
                    </span>
                  </p>
                </li>
              );
            })}
          </ul>
        )}

        {/* Pagination */}
        {totalCount > PAGE_SIZE && (
          <div className="mt-6 flex items-center justify-between border-t border-[#e8e3d6] pt-5">
            <button
              type="button"
              onClick={() =>
                setPage(group.cluster_id, Math.max(1, page - 1))
              }
              disabled={page <= 1}
              className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.18em] text-[#3d3a35] transition-colors hover:bg-[#f0ece0] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
            >
              ← 이전
            </button>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#6b6760] tabular-nums">
              page {page} / {totalPages}
            </p>
            <button
              type="button"
              onClick={() =>
                setPage(group.cluster_id, Math.min(totalPages, page + 1))
              }
              disabled={page >= totalPages}
              className="rounded-full border border-[#dcd6c5] bg-transparent px-4 py-2 font-mono text-[11px] uppercase tracking-[0.18em] text-[#3d3a35] transition-colors hover:bg-[#f0ece0] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
            >
              다음 →
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* ── TOP 3 ─────────────────────────────────────── */}
      <section className="border-b border-[#e8e3d6]">
        <div className="mx-auto max-w-[1240px] px-8 py-24">
          <div className="mb-12 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                Notebook · 02
              </p>
              <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[52px]">
                관객 의견 <span className="italic text-[#ff2c63]">TOP 3</span>
              </h2>
              <p className="mt-4 max-w-[480px] text-[15px] leading-[1.7] text-[#3d3a35]">
                가장 많이 언급된 세 가지 의견 군집입니다. 카드를 누르면 해당
                군집에 묶인 실제 리뷰가 바로 아래에 펼쳐집니다.
              </p>
            </div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
              clusters · {sorted.length} groups
            </p>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
            {topThree.map((group, idx) => {
              const tone = sentimentTone[group.sentiment];
              const isSelected = group.cluster_id === selectedClusterId;
              const ratio = Math.round((group.count / total) * 100);
              return (
                <button
                  type="button"
                  key={group.cluster_id}
                  onClick={() => handleSelect(group.cluster_id)}
                  className={`group relative flex h-full flex-col items-start rounded-[10px] border bg-white p-6 text-left transition-all duration-300 ${
                    isSelected
                      ? "border-[#ff2c63] shadow-[0_20px_36px_-22px_rgba(255,44,99,0.4)]"
                      : "border-[#e8e3d6] hover:-translate-y-1 hover:border-[#dcd6c5] hover:shadow-[0_18px_36px_-22px_rgba(20,15,5,0.2)]"
                  }`}
                >
                  <div className="flex w-full items-start justify-between">
                    <span className="font-serif text-[48px] italic leading-none text-[#161616]/80 tabular-nums">
                      {String(idx + 1).padStart(2, "0")}
                    </span>
                    <span
                      className="rounded-full px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.18em]"
                      style={{ background: tone.bg, color: tone.ink }}
                    >
                      {tone.label}
                    </span>
                  </div>

                  <h3 className="mt-5 font-serif text-[22px] font-medium leading-[1.25] tracking-[-0.01em] text-[#161616]">
                    {group.label}
                  </h3>

                  <div className="mt-6 flex w-full items-end justify-between">
                    <div>
                      <p className="font-serif text-[28px] leading-none text-[#161616] tabular-nums">
                        {group.count.toLocaleString()}
                      </p>
                      <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                        mentions · {ratio}%
                      </p>
                    </div>
                    <span
                      className="font-mono text-[11px] uppercase tracking-[0.18em] transition-colors"
                      style={{
                        color: isSelected ? "#ff2c63" : "#9a958b",
                      }}
                    >
                      {isSelected ? "− 닫기" : "+ 펼치기"}
                    </span>
                  </div>

                  <div className="mt-4 flex h-[3px] w-full overflow-hidden rounded-full bg-[#efe9d8]">
                    <div
                      className="h-full transition-[width] duration-500"
                      style={{
                        width: `${Math.round((group.count / topThree[0].count) * 100)}%`,
                        background: tone.bar,
                      }}
                    />
                  </div>
                </button>
              );
            })}
          </div>

          {isTopSelected && selectedGroup && renderExpandedReviews(selectedGroup)}
        </div>
      </section>

      {/* ── 그 외 의견 그룹 ───────────────────────────── */}
      {rest.length > 0 && (
        <section className="border-b border-[#e8e3d6] bg-[#f5f1e6]">
          <div className="mx-auto max-w-[1240px] px-8 py-24">
            <div className="mb-12 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                  Logbook · 03
                </p>
                <h2 className="mt-5 font-serif text-[44px] leading-[1.05] tracking-[-0.025em] text-[#161616] sm:text-[52px]">
                  그 외 <span className="italic">의견 그룹</span>
                </h2>
                <p className="mt-4 max-w-[460px] text-[15px] leading-[1.7] text-[#3d3a35]">
                  TOP 3 다음으로 자주 언급된 군집입니다. 행을 펼치면 해당
                  의견의 실제 리뷰가 표시됩니다.
                </p>
              </div>
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[#9a958b]">
                rest · {rest.length} groups
              </p>
            </div>

            <ol className="rounded-[10px] border border-[#dcd6c5] bg-[#fbf9f3]/70">
              {rest.map((group, idx) => {
                const tone = sentimentTone[group.sentiment];
                const isSelected = group.cluster_id === selectedClusterId;
                const isLast = idx === rest.length - 1;
                const ratio = Math.round((group.count / total) * 100);

                return (
                  <li
                    key={group.cluster_id}
                    className={!isLast ? "border-b border-[#e8e3d6]" : ""}
                  >
                    <button
                      type="button"
                      onClick={() => handleSelect(group.cluster_id)}
                      className={`group grid w-full grid-cols-[56px_1fr_auto_44px] items-center gap-x-4 px-6 py-5 text-left transition-colors hover:bg-white/60 ${
                        isSelected ? "bg-white" : ""
                      }`}
                    >
                      <span className="font-serif text-[26px] leading-none text-[#9a958b] tabular-nums">
                        {String(idx + 4).padStart(2, "0")}
                      </span>

                      <div className="min-w-0">
                        <h3 className="truncate font-serif text-[20px] font-medium leading-tight tracking-[-0.005em] text-[#161616]">
                          {group.label}
                        </h3>
                        <div className="mt-2 flex flex-wrap items-center gap-3">
                          <span
                            className="rounded-full px-2 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.18em]"
                            style={{ background: tone.bg, color: tone.ink }}
                          >
                            {tone.label}
                          </span>
                          <span className="font-mono text-[11px] tabular-nums text-[#6b6760]">
                            전체의 {ratio}%
                          </span>
                        </div>
                      </div>

                      <div className="text-right">
                        <p className="font-serif text-[22px] leading-none text-[#161616] tabular-nums">
                          {group.count.toLocaleString()}
                        </p>
                        <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[#9a958b]">
                          mentions
                        </p>
                      </div>

                      <span
                        className="ml-auto inline-flex h-9 w-9 items-center justify-center rounded-full border transition-colors"
                        style={{
                          borderColor: isSelected ? "#ff2c63" : "#dcd6c5",
                          color: isSelected ? "#ff2c63" : "#6b6760",
                          background: isSelected ? "#ffe8ef" : "transparent",
                        }}
                      >
                        <span className="font-serif text-[22px] leading-none">
                          {isSelected ? "−" : "+"}
                        </span>
                      </span>
                    </button>

                    {isSelected && (
                      <div className="px-6 pb-6 pt-0">
                        {renderExpandedReviews(group)}
                      </div>
                    )}
                  </li>
                );
              })}
            </ol>
          </div>
        </section>
      )}
    </>
  );
}
