import re
from datetime import date, timedelta

from app.db.models.movie import Movie
from app.db.models import Review
from app.db.session import SessionLocal

MOVIE_SEARCH_LIMIT_MAX = 50


def _normalize(text: str) -> str:
    """공백 무시 + 소문자. '슈퍼마리오'로 '슈퍼 마리오 갤럭시' 매칭되게."""
    return re.sub(r"\s+", "", text or "").lower()


def get_movies() -> list[dict]:
    db = SessionLocal()

    try:
        movies = db.query(Movie).order_by(Movie.movie_id).all()

        return [
            {
                "movie_id": movie.movie_id,
                "movie_title": movie.movie_title,
                "release_year": movie.release_year,
                "source": movie.source,
                "registered_at": movie.registered_at,
                "updated_at": movie.updated_at,
            }
            for movie in movies
        ]

    finally:
        db.close()


def search_movies(query: str, limit: int = 20) -> dict:
    """제목 부분일치(대소문자·공백 무시) 검색. 빈/공백 q는 빈 결과.

    랭킹: 정확일치(0) > 접두일치(1) > 부분일치(2), 동순위는 최신 release 우선.
    total_count는 limit 적용 전 매칭 수.
    """
    nq = _normalize(query)
    limit = max(1, min(limit, MOVIE_SEARCH_LIMIT_MAX))

    if not nq:
        return {"query": query, "total_count": 0, "items": []}

    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
    finally:
        db.close()

    matched = []
    for m in movies:
        nt = _normalize(m.movie_title)
        if nq not in nt:
            continue
        if nt == nq:
            rank = 0
        elif nt.startswith(nq):
            rank = 1
        else:
            rank = 2
        # 최신 우선: release_date > release_year. None은 가장 뒤로.
        recency = m.release_date or (date(m.release_year, 1, 1) if m.release_year else date.min)
        matched.append((rank, recency, m))

    # rank 오름차순, recency 내림차순(-ordinal), 제목 오름차순.
    matched.sort(key=lambda t: (t[0], -t[1].toordinal(), t[2].movie_title))

    items = [
        {
            "movie_id": m.movie_id,
            "movie_title": m.movie_title,
            "poster_url": m.poster_url,
            "release_year": m.release_year,
            "genre": m.genre,
            "source": m.source,
        }
        for _, _, m in matched[:limit]
    ]
    return {"query": query, "total_count": len(matched), "items": items}


def _week_start(d: date) -> date:
    """해당 날짜가 속한 주의 월요일."""
    return d - timedelta(days=d.weekday())


def get_review_traffic(movie_id: str, granularity: str = "day") -> dict:
    """영화의 리뷰 작성일(written_at) 기준 시계열 트래픽.

    written_at이 있는 전체 리뷰를 일/주 버킷으로 집계하고, min~max 사이
    빈 버킷은 count=0으로 채워 연속된 그래프 데이터를 만든다.
    movie_id가 movies 테이블에 없으면 ValueError.
    """
    if granularity not in ("day", "week"):
        raise ValueError(f"Unsupported granularity: {granularity}")

    db = SessionLocal()
    try:
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).one_or_none()
        if movie is None:
            raise ValueError(f"movie_id '{movie_id}' not found in movies table")

        rows = (
            db.query(Review.written_at)
            .filter(Review.movie_id == movie_id, Review.written_at.isnot(None))
            .all()
        )

        counts: dict[date, int] = {}
        for (written_at,) in rows:
            bucket = written_at.date()
            if granularity == "week":
                bucket = _week_start(bucket)
            counts[bucket] = counts.get(bucket, 0) + 1

        points = _fill_gaps(counts, granularity)

        return {
            "movie_id": movie.movie_id,
            "movie_title": movie.movie_title,
            "granularity": granularity,
            "total_reviews": sum(counts.values()),
            "points": points,
        }
    finally:
        db.close()


def _fill_gaps(counts: dict[date, int], granularity: str) -> list[dict]:
    if not counts:
        return []

    step = timedelta(days=1 if granularity == "day" else 7)
    cursor, end = min(counts), max(counts)

    points = []
    while cursor <= end:
        points.append({"date": cursor, "count": counts.get(cursor, 0)})
        cursor += step
    return points
