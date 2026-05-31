import Link from "next/link";
import { getMovies } from "@/lib/api";
import AnalysisRequestClient from "@/components/AnalysisRequestClient";

type MovieDetailPageProps = {
  params: Promise<{
    movieId: string;
  }>;
};

export default async function MovieDetailPage({
  params,
}: MovieDetailPageProps) {
  const { movieId } = await params;

  const movies = await getMovies();
  const movie = movies.find((item) => item.movie_id === movieId);

  if (!movie) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-10">
        <div className="mx-auto max-w-3xl rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-gray-900">
            영화를 찾을 수 없습니다.
          </h1>

          <p className="mt-3 text-gray-600">요청한 영화 ID: {movieId}</p>

          <Link
            href="/movies"
            className="mt-6 inline-flex rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
          >
            영화 목록으로 돌아가기
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto max-w-4xl">
        <Link
          href="/movies"
          className="text-sm font-semibold text-blue-600 hover:underline"
        >
          ← 영화 목록으로
        </Link>

        <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
          <p className="text-sm font-semibold text-blue-600">
            Analysis Request
          </p>

          <h1 className="mt-2 text-3xl font-bold text-gray-900">
            {movie.movie_title} 분석 요청
          </h1>

          <div className="mt-4 flex gap-2 text-sm">
            <span className="rounded-full bg-gray-100 px-3 py-1 text-gray-600">
              {movie.release_year}
            </span>

            <span className="rounded-full bg-blue-50 px-3 py-1 text-blue-700">
              {movie.source}
            </span>

            {movie.is_active && (
              <span className="rounded-full bg-green-50 px-3 py-1 text-green-700">
                활성
              </span>
            )}
          </div>

          {movie.notes && <p className="mt-5 text-gray-600">{movie.notes}</p>}

          <div className="mt-8 rounded-2xl bg-gray-50 p-5">
            <p className="text-sm text-gray-500">선택된 영화 ID</p>
            <p className="mt-1 font-mono text-lg font-semibold text-gray-900">
              {movie.movie_id}
            </p>
          </div>

          <AnalysisRequestClient movieId={movie.movie_id} />
        </section>
      </div>
    </main>
  );
}