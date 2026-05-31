import type { DashboardMovie } from "@/lib/types";
import MovieCard from "./MovieCard";

type Props = {
  movies: DashboardMovie[];
};

export default function MovieCardGrid({ movies }: Props) {
  if (movies.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center text-gray-400">
        분석된 영화가 아직 없습니다.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {movies.map((movie) => (
        <MovieCard key={movie.movie_id} movie={movie} />
      ))}
    </div>
  );
}