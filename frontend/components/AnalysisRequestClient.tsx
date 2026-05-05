"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type AnalysisRequestClientProps = {
  movieId: string;
};

function getTodayString() {
  return new Date().toISOString().slice(0, 10);
}

export default function AnalysisRequestClient({
  movieId,
}: AnalysisRequestClientProps) {
  const router = useRouter();

  const [targetDate, setTargetDate] = useState(getTodayString());
  const [isRunning, setIsRunning] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRunAnalysis = async () => {
    try {
      setIsRunning(true);
      setErrorMessage(null);

      const res = await fetch("/api/batch/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          movie_id: movieId,
          target_date: targetDate,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message ?? "분석 실행에 실패했습니다.");
      }

      router.push(`/jobs/${data.job_id}/result`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "분석 실행 중 오류가 발생했습니다."
      );
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="mt-8 rounded-2xl border border-gray-200 bg-gray-50 p-6">
      <h2 className="text-lg font-bold text-gray-900">분석 실행</h2>

      <p className="mt-2 text-sm text-gray-600">
        기준 날짜를 선택한 뒤 분석을 시작하면 LLM 분석, 클러스터링, 최종 결과
        생성이 순서대로 실행됩니다.
      </p>

      <div className="mt-5">
        <label className="text-sm font-semibold text-gray-700">기준 날짜</label>

        <input
          type="date"
          value={targetDate}
          onChange={(event) => setTargetDate(event.target.value)}
          className="mt-2 block w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none focus:border-blue-500"
        />
      </div>

      {errorMessage && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-600">
          {errorMessage}
        </div>
      )}

      <button
        type="button"
        onClick={handleRunAnalysis}
        disabled={isRunning}
        className="mt-5 inline-flex rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isRunning ? "분석 실행 중..." : "분석 시작하기"}
      </button>
    </div>
  );
}