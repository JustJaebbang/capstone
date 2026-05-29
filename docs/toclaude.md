팀장님, 회의에서 정해주신 B안으로 백엔드 적용이 아직 안 된 것 같아서 요청드립니다.

[현재 확인한 상황]
Swagger(127.0.0.1:8000/docs)에서 POST /collection/reviews/run-now를 펼쳐보니 request body가 아직 이렇게 돼 있습니다:
{
  "movie_id": "kobis_20252402",
  "cgv_movie_code": "30001046",
  "source": "cgv",
  "depth": "preview",
  "run_analysis": false
}

cgv_movie_code가 그대로 있어서, 팀장님이 말씀하신 B안(run-now가 movie_id만 받고 백엔드가 내부적으로 cgv_movie_code를 찾아서 처리)이 아직 적용안 된 것으로 보입니다.

[부탁드릴 것]
run-now의 request body에서 cgv_movie_code를 빼고, movie_id만 있어도 동작하도록 변경 부탁드립니다. depth·run_analysis는 그대로 유지하실 건지, source는 어떻게 할지도 같이 알려주시면 그에 맞춰 프론트 작업하겠습니다.

[subscribe 동일 문제]
POST /collection/subscribe 도 같은 cgv_movie_code를 받고 있어서, 같은 맥락이면 함께 수정 부탁드립니다.

적용 완료되면 알려주세요! 그때 프론트 작업 들어가겠습니다.
