import Link from "next/link";
import { getMovies } from "@/lib/api";

export default async function MoviesPage() {
  const movies = await getMovies();

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-blue-600">
              Movie Review Analysis
            </p>

            <h1 className="mt-2 text-3xl font-bold text-gray-900">
              분석 대상 영화 목록
            </h1>

            <p className="mt-2 text-gray-600">
              백엔드 API에서 불러온 영화 목록입니다.
            </p>
          </div>

          <Link
            href="/"
            className="rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-100"
          >
            홈으로
          </Link>
        </div>

        <div className="grid gap-4">
          {movies.map((movie) => (
            <div
              key={movie.movie_id}
              className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {movie.movie_title}
                  </h2>

                  <div className="mt-2 flex gap-2 text-sm">
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

                  {movie.notes && (
                    <p className="mt-3 text-sm text-gray-500">{movie.notes}</p>
                  )}

                  <p className="mt-2 text-xs text-gray-400">
                    ID: {movie.movie_id}
                  </p>
                </div>

                <Link
                  href={`/movies/${movie.movie_id}`}
                  className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
                >
                  선택
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}