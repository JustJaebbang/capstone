재영아, /movies 대시보드 실 API 연동 다 끝냈어 — 영화들 잘 뜨고 포스터도 나와. 작업하면서 백엔드에 필요한 게 두 가지 나와서 정리해 보내. 둘 다 급한 건 아니고, 시간 될 때 해주면 돼.

[1] /dashboard/movies 응답에 latest_job_id 추가
각 영화 객체(items[])에 latest_job_id — 그 영화의 가장 최근 완료된 분석 job_id — 를 넣어줄 수 있을까?
왜 필요하냐: 프론트에서 영화 카드 누르면 /jobs/{job_id}/result 로 가야 하는데, 지금 movies 응답엔 job_id가 없어. 그래서 임시로 summary의 recent_jobs(최근 5개)에 있는 영화만 링크가 걸려. 나머지 카드는 전부 '결과 없음' 비활성이라, 영화 늘면 대부분 카드가 죽어.
어떻게: summary의 recent_jobs에 이미 job_id-movie_id 연결이 있으니 movies 응답에도 같은 식으로 넣어주면 돼.

[2] /batch/jobs/{job_id}/final-result 응답에 poster_url 추가
결과 페이지에서 영화 포스터를 띄우고 싶은데, final-result 응답엔 job_id, movie_id, movie_title, summary 네 개뿐이라 poster_url이 없어 (schemas.py FinalResultSchema). /dashboard/movies 에는 poster_url이 있으니, final-result 응답에도 poster_url 하나 넣어줄 수 있을까? movie_id는 이미 응답에 있으니 그걸로 movies 테이블의 poster_url 가져오면 될 것 같아.

프론트는 둘 다 받으면 바로 쓰도록 돼 있어서, 백엔드에서 넣어주기만 하면 돼. 고마워!
