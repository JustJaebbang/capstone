import streamlit as st
import json
import time
import os
from datetime import datetime
import requests

# 백엔드 서버 기본 주소
BASE_URL = "http://localhost:8000"

# --- 더미 데이터 불러오기 (서버가 꺼져있을 때 쓸 비상식량) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'dummy_data.json')
with open(file_path, 'r', encoding='utf-8') as f:
    dummy_data = json.load(f)

# 수첩(세션 상태) 초기화
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = dummy_data["movie_list"][0]["movie_id"]

st.sidebar.title("🎬 영화 분석 시스템")
menu = st.sidebar.radio("메뉴 이동", ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"])

# ---------------------------------------------------
# [메뉴 1] 영화 목록 (GET /movies)
# ---------------------------------------------------
if menu == "1. 영화 목록":
    st.title("🍿 분석 대상 영화 목록")
    
    # [API 연동] 서버에 영화 목록 달라고 요청하기
    try:
        response = requests.get(f"{BASE_URL}/movies", timeout=2)
        response.raise_for_status()
        movie_list = response.json()
        st.success("🟢 백엔드 서버와 연결되었습니다! (Real API)")
    except requests.exceptions.RequestException:
        movie_list = dummy_data["movie_list"]
        st.warning("🔴 서버가 꺼져 있어 더미 데이터를 보여줍니다.")

    for movie in movie_list:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.subheader(f"{movie['movie_title']} ({movie['release_year']})")
            details = f"🆔 ID: `{movie['movie_id']}` | 🌐 출처: `{movie['source']}` | 📅 등록: `{movie['registered_at'].split('T')[0]}`"
            col1.write(details)
            status_tag = "✅ 분석 가능" if movie['is_active'] else "❌ 분석 불가"
            col1.caption(f"상태: {status_tag} | 메모: {movie['notes']}")
            
            if col2.button("선택", key=f"btn_{movie['movie_id']}"):
                st.session_state.selected_movie_id = movie['movie_id']
                st.toast(f"'{movie['movie_title']}'가 선택되었습니다.")

# ---------------------------------------------------
# [메뉴 2] 분석 요청 (POST & GET Polling)
# ---------------------------------------------------
elif menu == "2. 분석 요청(배치)":
    st.title("⚙️ 분석 요청하기")
    movie_names = [m['movie_title'] for m in dummy_data["movie_list"]]
    
    current_index = 0
    for i, m in enumerate(dummy_data["movie_list"]):
        if m['movie_id'] == st.session_state.selected_movie_id:
            current_index = i
            
    selected_movie_title = st.selectbox("어떤 영화를 분석할까요?", movie_names, index=current_index)
    
    for m in dummy_data["movie_list"]:
        if m['movie_title'] == selected_movie_title:
            st.session_state.selected_movie_id = m['movie_id']
    
    t_date = datetime.strptime(dummy_data['batch_response']['target_date'], '%Y-%m-%d')
    target_date = st.date_input("분석 기준 날짜", value=t_date)
    
    if st.button("분석 서버에 요청 보내기"):
        # 1. POST 요청 (작업 등록)
        payload = {"movie_id": st.session_state.selected_movie_id, "target_date": str(target_date)}
        
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            try:
                # 🚨 [진짜 API] 1단계: POST로 작업 던지기
                res = requests.post(f"{BASE_URL}/batch/jobs", json=payload, timeout=2)
                res.raise_for_status() 
                batch = res.json()
                job_id = batch['job_id']
                st.write(f"작업 대기열 등록... (`POST /batch/jobs` 성공)")

                # 🚨 [진짜 API] 2단계: GET으로 상태 계속 물어보기 (Polling)
                current_status = batch['status']
                while current_status not in ["completed", "failed"]:
                    time.sleep(2) # 2초마다 상태 물어보기
                    poll_res = requests.get(f"{BASE_URL}/batch/jobs/{job_id}", timeout=2)
                    poll_res.raise_for_status()
                    poll_data = poll_res.json()
                    current_status = poll_data['status']
                    st.write(f"현재 상태: {current_status} (`GET /batch/jobs/{job_id}` 확인 완료)")

                # 3단계: 결과 확인
                if current_status == "completed":
                    status.update(label="✅ 작업 완료! 상태: completed", state="complete", expanded=False)
                else:
                    status.update(label="❌ 작업 실패!", state="error", expanded=False)

            except requests.exceptions.RequestException:
                # 🚨 [Fallback] 서버가 꺼져있을 땐 우리가 만든 6단계 시뮬레이션 돌리기
                st.write("🔴 서버 응답 없음. 더미 시뮬레이션을 시작합니다.")
                batch = dummy_data['batch_response']
                batch['movie_id'] = st.session_state.selected_movie_id
                
                st.write("작업 대기열 등록... (`queued`)")
                time.sleep(0.5)
                st.write("리뷰 수집 중... (`collecting_reviews`)")
                time.sleep(0.7)
                st.write("AI 텍스트 분석 중... (`llm_processing`)")
                time.sleep(0.7)
                st.write("유사 리뷰 군집화 중... (`clustering`)")
                time.sleep(0.7)
                st.write("최종 결과 저장 중... (`saving_results`)")
                time.sleep(0.5)
                status.update(label="✅ 작업 완료! 상태: completed (Dummy)", state="complete", expanded=False)

        st.success(f"요청 성공! Job ID: `{batch['job_id']}`")

# ---------------------------------------------------
# [메뉴 3] 분석 결과 보기 (GET /movies/{movie_id}/review-summary)
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    movie_id = st.session_state.selected_movie_id
    st.title(f"📊 분석 결과")
    st.info(f"💡 분석 대상 영화 ID: {movie_id}")
    
    # [API 연동] 서버에 완료된 결과 가져오라고 요청하기
    try:
        response = requests.get(f"{BASE_URL}/movies/{movie_id}/review-summary", timeout=2)
        response.raise_for_status()
        res = response.json()
    except requests.exceptions.RequestException:
        res = dummy_data["result_data"]
        res['movie_id'] = movie_id

    st.write(f"**총 리뷰:** {res['total_reviews']}건 | **최종 분석일:** {res['analysis_date']}")
    st.divider()
    
    col1, col2 = st.columns(2)
    cards = [col1, col2]
    
    for i, item in enumerate(res["review_summary"]):
        with cards[i % 2]:
            percent = int(item['ratio'] * 100)
            st.success(f"**{item['label']} ({percent}%)**")
            st.write(f"📈 건수: {item['count']}건")
            with st.expander("대표 리뷰 보기"):
                for example in item['examples']:
                    st.write(f"💬 {example}")