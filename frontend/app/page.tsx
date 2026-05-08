import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 py-16">
        {/* 로고/배지 */}
        <p className="text-sm font-semibold tracking-wide text-blue-600">
          Movie Review Analysis
        </p>

        {/* 메인 타이틀 */}
        <h1 className="mt-4 text-center text-5xl font-bold text-gray-900">
          영화 리뷰, <br />
          <span className="text-blue-600">한눈에 분석하다</span>
        </h1>

        {/* 서브 타이틀 */}
        <p className="mt-6 max-w-xl text-center text-lg text-gray-600">
          AI 기반 감성 분석과 클러스터링으로 관객의 진짜 의견을 파악합니다.
          <br />
          리뷰 수집부터 인사이트 요약까지, 한 번에.
        </p>

        {/* CTA 버튼 */}
        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
          <Link
            href="/movies"
            className="rounded-xl bg-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-md transition hover:bg-blue-700 hover:shadow-lg"
          >
            영화 목록 보러가기 →
          </Link>
        </div>

        {/* 4단계 안내 */}
        <div className="mt-20 grid w-full grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { icon: "📥", title: "리뷰 수집", desc: "리뷰 데이터를 수집합니다" },
            { icon: "😊", title: "감성 분석", desc: "긍/부정 감성 분석" },
            { icon: "👥", title: "클러스터링", desc: "토픽을 그룹화합니다" },
            { icon: "📄", title: "인사이트 요약", desc: "핵심 인사이트 제공" },
          ].map((step, i) => (
            <div
              key={step.title}
              className="rounded-2xl border border-gray-200 bg-white p-5 text-center shadow-sm"
            >
              <div className="text-3xl">{step.icon}</div>
              <p className="mt-2 text-xs font-semibold text-blue-600">
                STEP {i + 1}
              </p>
              <p className="mt-1 text-sm font-bold text-gray-900">
                {step.title}
              </p>
              <p className="mt-1 text-xs text-gray-500">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}