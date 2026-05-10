const STEPS = [
  { icon: "📥", title: "리뷰 수집", desc: "리뷰 데이터를 수집합니다" },
  { icon: "😊", title: "감성 분석", desc: "긍/부정 감성 분석" },
  { icon: "👥", title: "클러스터링", desc: "토픽을 그룹화합니다" },
  { icon: "📄", title: "인사이트 요약", desc: "핵심 인사이트 제공" },
];

export default function ServiceFlowBanner() {
  return (
    <div className="rounded-2xl border border-blue-100 bg-blue-50/50 p-5">
      <div className="flex items-start gap-3">
        <div className="text-xl">💡</div>
        <div className="flex-1">
          <p className="text-sm font-bold text-gray-900">서비스 안내</p>
          <p className="mt-1 text-xs text-gray-600">
            영화를 선택하면 상세 분석 결과를 확인할 수 있습니다.
          </p>
          <p className="mt-0.5 text-xs text-gray-600">
            리뷰 수집 → 감성 분석 → 키워드 클러스터링 → 인사이트 요약 순으로
            진행됩니다.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-4">
          {STEPS.map((step) => (
            <div key={step.title} className="flex items-center gap-2">
              <span className="text-lg">{step.icon}</span>
              <div>
                <p className="text-xs font-semibold text-gray-900">
                  {step.title}
                </p>
                <p className="text-[10px] text-gray-500">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}