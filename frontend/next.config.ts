import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // 워크스페이스 루트를 이 frontend 폴더로 고정.
  // (Next가 리포 루트 capstone\을 루트로 오인해 tailwindcss 모듈을
  //  capstone\node_modules에서 찾다 실패하는 문제 해결 — webpack/turbopack 공통)
  outputFileTracingRoot: path.resolve(__dirname),
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
