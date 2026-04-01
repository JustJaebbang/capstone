import streamlit as st
import json
import time
import os
import requests
from datetime import datetime

# 1. 환경 설정
BASE_URL = "http://localhost:8000"
current_dir = os.path.dirname(os.path.abspath(__file__))
DUMMY_PATH = os.path.join(current_dir, 'dummy_data.json')

# 비상용 더미 데이터 미리 로드
with open(DUMMY_PATH, 'r', encoding='utf-8') as f:
    FALLBACK_DATA = json.load(f)

# 2. 세션 상태(수첩) 초기화
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = FALLBACK_DATA["movie_list"][0]["movie_id"]

st.sidebar.title("🎬 영화 분석 시스템")
menu = st.sidebar.radio("메뉴 이동", ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"])

# ---------------------------------------------------
# [메뉴 1] 영화 목록 (GET /movies)
# ---------------------------------------------------
if menu == "1. 영화 목록":
    st.title("🍿 분석 대상 영화 목록")
    
    try:
        res = requests.get(f"{BASE_URL}/movies", timeout=2)
        res.raise_for_status()
        movie_list = res.json()
        st.success("🟢 실시간 서버 데이터 연결 중")
    except:
        movie_list = FALLBACK_DATA["movie_list"]
        st.warning("⚠️ 서버 연결 실패. 더미 데이터를 표시합니다.")

    for movie in movie_list:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.subheader(f"{movie['movie_title']} ({movie['release_year']})")
            col1.write(f"🆔 ID: `{movie['movie_id']}` | 🌐 출처: `{movie['source']}`")
            if col2.button("선택", key=f"sel_{movie['movie_id']}"):
                st.session_state.selected_movie_id = movie['movie_id']
                st.toast(f"'{movie['movie_title']}' 선택됨")

# ---------------------------------------------------
# [메뉴 2] 분석 요청 (POST /batch/jobs & GET 폴링)
# ---------------------------------------------------
elif menu == "2. 분석 요청(배치)":
    st.title("⚙️ 분석 요청하기")
    
    try:
        m_res = requests.get(f"{BASE_URL}/movies", timeout=1)
        m_list = m_res.json()
    except:
        m_list = FALLBACK_DATA["movie_list"]

    movie_names = [m['movie_title'] for m in m_list]
    current_idx = next((i for i, m in enumerate(m_list) if m['movie_id'] == st.session_state.selected_movie_id), 0)
    
    selected_title = st.selectbox("분석 대상 영화", movie_names, index=current_idx)
    target_date = st.date_input("기준 날짜", value=datetime.now())

    if st.button("🚀 분석 시작"):
        payload = {"movie_id": st.session_state.selected_movie_id, "target_date": str(target_date)}
        
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            try:
                # 1. POST 요청
                post_res = requests.post(f"{BASE_URL}/batch/jobs", json=payload, timeout=2)
                post_res.raise_for_status()
                job = post_res.json()
                job_id = job['job_id']
                st.write(f"✅ 작업 생성 완료 (ID: {job_id})")

                # 2. GET 상태 조회 (Polling)
                curr_status = job.get('status', 'queued')
                while curr_status not in ["completed", "failed"]:
                    time.sleep(2)
                    poll = requests.get(f"{BASE_URL}/batch/jobs/{job_id}", timeout=2)
                    curr_status = poll.json()['status']
                    st.write(f"🔄 현재 상태: `{curr_status}`")
                
                status.update(label=f"🏁 작업 {curr_status}!", state="complete" if curr_status=="completed" else "error")
            
            except:
                st.error("🚨 서버 연결 불가. 시뮬레이션을 시작합니다.")
                for s in ["queued", "collecting_reviews", "llm_processing", "clustering", "saving_results", "completed"]:
                    st.write(f"🕒 가상 상태: `{s}`")
                    time.sleep(0.5)
                status.update(label="✅ 시뮬레이션 완료", state="complete")

# ---------------------------------------------------
# [메뉴 3] 분석 결과 (GET /movies/{id}/review-summary)
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    mid = st.session_state.selected_movie_id
    st.title(f"📊 분석 리포트")
    st.caption(f"대상 영화 ID: {mid}")

    # 🚨 A의 4번 피드백 완벽 적용 구역 🚨
    is_data_loaded = False
    
    try:
        res = requests.get(f"{BASE_URL}/movies/{mid}/review-summary", timeout=2)
        
        # [추가] 분석 결과가 아직 없을 때 (404 Not Found)
        if res.status_code == 404:
            st.info("📭 아직 분석 결과가 없습니다. [2. 분석 요청] 메뉴에서 먼저 배치를 실행해주세요.")
        else:
            res.raise_for_status()
            data = res.json()
            is_data_loaded = True
            st.success("🟢 실시간 분석 결과 로드 완료")
            
    except requests.exceptions.RequestException:
        # 서버가 꺼져있을 땐 예쁘게 더미 데이터 보여주기
        data = FALLBACK_DATA["result_data"]
        is_data_loaded = True
        st.warning("⚠️ 서버 연결 실패. 더미 결과를 표시합니다.")

    # 데이터가 있을 때만 화면에 그리기
    if is_data_loaded:
        st.metric("총 리뷰 수", f"{data['total_reviews']}건")
        st.write(f"📅 최종 분석일: {data['analysis_date']}")
        st.divider()
        
        for item in data["review_summary"]:
            with st.container(border=True):
                # 라벨과 프로그레스 바 (게이지 바) 적용!
                st.subheader(f"{item['label']}")
                
                # 비율 게이지 표시 (0.0 ~ 1.0 사이 값)
                st.progress(float(item['ratio'])) 
                
                st.caption(f"비중: {int(item['ratio']*100)}% | 건수: {item['count']}건")
                
                # 대표 리뷰 접기/펼치기
                with st.expander("💬 대표 리뷰 보기"):
                    for ex in item['examples']:
                        st.markdown(f"> {ex}")