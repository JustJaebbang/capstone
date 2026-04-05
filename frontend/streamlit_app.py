import streamlit as st
import json
import time
import os
import requests
from datetime import datetime

# 1. 환경 설정 및 UI 테마(CSS) 적용
BASE_URL = "http://localhost:8000"
current_dir = os.path.dirname(os.path.abspath(__file__))
DUMMY_PATH = os.path.join(current_dir, 'dummy_data.json')

# 🚨 CSS 마법: 최상단 Home 버튼 + 사이드바 박스 UI + 빨간 원 제거
st.markdown("""
    <style>
    /* 1. 최상단 Home 버튼 스타일링 */
    div[data-testid="stSidebar"] [data-testid="stButton"] button {
        background-color: #ffffff !important;
        color: #31333F !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        margin-bottom: 10px !important; /* 타이틀과의 간격 */
        transition: all 0.2s ease;
    }
    div[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background-color: #f0f2f6 !important;
        border-color: #ced4da !important;
    }

    /* 2. 사이드바 메뉴 전체 스타일 (왼쪽 정렬 박스) */
    div[role="radiogroup"] label {
        display: flex !important;
        width: 100% !important;
        padding: 12px 16px !important;
        margin-bottom: 8px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        justify-content: flex-start !important; 
        align-items: center !important;
        text-align: left !important;
    }

    /* ❌ 유령 여백 및 빨간 원 완전 제거 */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 라벨 텍스트 스타일 */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
        font-weight: 600 !important;
        font-size: 1.02rem !important;
        color: #31333F !important;
    }

    /* ✅ 선택된 상태 비주얼 */
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #2e7d32 !important; 
        border-color: #1b5e20 !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: white !important;
    }

    /* 본문 영역 호버 효과 */
    div.stButton > button:hover {
        background-color: #f0f2f6 !important;
        border-color: #8c92a1 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #8c92a1 !important;
        background-color: #fafbfc !important;
    }
    </style>
""", unsafe_allow_html=True)

with open(DUMMY_PATH, 'r', encoding='utf-8') as f:
    FALLBACK_DATA = json.load(f)

# 2. 세션 상태 초기화
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = FALLBACK_DATA["movie_list"][0]["movie_id"]
if 'selected_label' not in st.session_state:
    st.session_state.selected_label = None

# ---------------------------------------------------
# 🚨 사이드바 구성 (순서 변경: Home 버튼 -> 타이틀 -> 메뉴)
# ---------------------------------------------------

# 1단계: 최상단 Home 버튼
if st.sidebar.button("🏠 Home", use_container_width=True, key="home_btn"):
    st.session_state.main_menu = "1. 영화 목록"
    st.session_state.selected_label = None
    st.rerun()

# 2단계: 타이틀
st.sidebar.title("🎬 영화 분석 시스템")

# 3단계: 메뉴 이동 라디오 버튼
menu = st.sidebar.radio("메뉴 이동", ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"], key="main_menu")


# ---------------------------------------------------
# [메뉴 1] 영화 목록 
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
                st.session_state.selected_label = None
                st.toast(f"'{movie['movie_title']}' 선택됨")

# ---------------------------------------------------
# [메뉴 2] 분석 요청 
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
                post_res = requests.post(f"{BASE_URL}/batch/jobs", json=payload, timeout=2)
                post_res.raise_for_status()
                job = post_res.json()
                job_id = job['job_id']
                st.write(f"✅ 작업 생성 완료 (ID: {job_id})")
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
# [메뉴 3] 분석 결과 
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    mid = st.session_state.selected_movie_id
    st.title(f"📊 분석 리포트")
    st.caption(f"대상 영화 ID: {mid}")
    is_data_loaded = False
    try:
        res = requests.get(f"{BASE_URL}/movies/{mid}/review-summary", timeout=2)
        if res.status_code == 404:
            st.info("📭 아직 분석 결과가 없습니다. [2. 분석 요청] 메뉴에서 먼저 배치를 실행해주세요.")
        else:
            res.raise_for_status()
            data = res.json()
            is_data_loaded = True
            st.success("🟢 실시간 분석 결과 로드 완료")
    except:
        data = FALLBACK_DATA["result_data"]
        is_data_loaded = True
        st.warning("⚠️ 서버 연결 실패. 더미 결과를 표시합니다.")

    if is_data_loaded:
        st.metric("총 리뷰 수", f"{data['total_reviews']}건")
        st.write(f"📅 최종 분석일: {data['analysis_date']}")
        st.divider()
        for item in data["review_summary"]:
            with st.container(border=True):
                if st.button(f"✨ {item['label']}", key=f"btn_{item['label']}", use_container_width=True):
                    if st.session_state.selected_label == item['label']:
                        st.session_state.selected_label = None 
                    else:
                        st.session_state.selected_label = item['label']
                st.progress(float(item['ratio'])) 
                st.caption(f"비중: {int(item['ratio']*100)}% | 건수: {item['count']}건")
                if st.session_state.selected_label == item['label']:
                    st.divider()
                    st.markdown(f"**🔍 상세 리뷰 ({len(item['examples'])}건)**")
                    with st.container(height=300):
                        for ex in item['examples']:
                            st.markdown(f"> {ex}")
                            st.divider()