"use client";

/**
 * Scoped font + helper-class stylesheet for the Watcha style experiment.
 * Each page in /style-experiments/watcha/* renders this once inside its
 * <main> so it doesn't have to live in app/layout.tsx (which would leak
 * into the rest of the app).
 *
 * Classes only apply inside `.watcha-page` to avoid global pollution.
 */
export default function WatchaFontStyles() {
  return (
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

      .watcha-page {
        font-family: 'Manrope', var(--font-geist-sans), 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, sans-serif;
        font-feature-settings: 'ss01';
        -webkit-font-smoothing: antialiased;
        color: #161616;
      }
      .watcha-page .font-serif {
        font-family: 'Fraunces', 'Noto Serif KR', 'Apple SD Gothic Neo', Georgia, serif;
        font-feature-settings: 'lnum';
      }
      .watcha-page .font-mono {
        font-family: 'JetBrains Mono', var(--font-geist-mono), ui-monospace, monospace;
      }
      .watcha-page .tabular-nums {
        font-variant-numeric: tabular-nums lining-nums;
      }

      @keyframes watcha-pulse-dot {
        0%, 100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.35); opacity: 0.55; }
      }
      @keyframes watcha-shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
      }
      @keyframes watcha-fade-up {
        0%   { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      .watcha-page .watcha-pulse-dot {
        animation: watcha-pulse-dot 1.4s ease-in-out infinite;
      }
      .watcha-page .watcha-shimmer {
        background-image: linear-gradient(
          90deg,
          rgba(255, 44, 99, 0) 0%,
          rgba(255, 44, 99, 0.95) 45%,
          rgba(255, 44, 99, 0.6) 55%,
          rgba(255, 44, 99, 0) 100%
        );
        background-size: 200% 100%;
        animation: watcha-shimmer 2.4s linear infinite;
      }
      .watcha-page .watcha-fade-up {
        animation: watcha-fade-up 360ms ease-out both;
      }
    `}</style>
  );
}
