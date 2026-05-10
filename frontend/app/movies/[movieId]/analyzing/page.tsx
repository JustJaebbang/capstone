"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { createBatchJob, runBatchPipeline } from "@/lib/api";

export default function AnalyzingPage() {
  const params = useParams<{ movieId: string }>();
  const router = useRouter();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  // 개발 모드의 StrictMode 중복 실행 방지용
  const startedRef = useRef(false);

  useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;

    const movieId = params?.movieId;
    if (!movieId) {
      setErrorMessage("영화 ID가 없습니다.");
      return;
    }

    const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD

    (async () => {
      try {
        // 1) job 생성
        const job = await createBatchJob(movieId, today);

        // 2) LLM → cluster → final 차례로 실행
        await runBatchPipeline(job.job_id);

        // 3) 결과 페이지로 (replace로 history에서 빼서 뒤로가기 방지)
        router.replace(`/jobs/${job.job_id}/result`);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "알 수 없는 오류";
        setErrorMessage(msg);
      }
    })();
  }, [params, router]);

  // 에러 화면
  if (errorMessage) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6">
        <div className="max-w-md rounded-2xl border border-red-200 bg-white p-8 text-center shadow-sm">
          <p className="text-3xl">⚠️</p>
          <h1 className="mt-3 text-xl font-bold text-gray-900">
            분석을 시작하지 못했습니다
          </h1>
          <p className="mt-2 text-sm text-gray-500">{errorMessage}</p>
          <button
            type="button"
            onClick={() => router.replace("/movies")}
            className="mt-6 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            영화 목록으로 돌아가기
          </button>
        </div>
      </main>
    );
  }

  // 분석 중 화면
  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-6">
      <div className="flex flex-col items-center">
        {/* 스피너 */}
        <div className="h-16 w-16 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />

        <h1 className="mt-6 text-2xl font-bold text-gray-900">
          분석 중...
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          리뷰 데이터를 분석하고 있습니다.
        </p>
        <p className="mt-1 text-sm text-gray-500">
          30초~1분 정도 소요될 수 있습니다.
        </p>
      </div>
    </main>
  );
}