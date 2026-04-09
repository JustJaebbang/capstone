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

# 🚨 찬우님의 디자인 가이드라인 (절대 유지)
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
        margin-bottom: 10px !important;
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
    div[role="radiogroup"] label:hover {
        background-color: #d1d5db !important;
        border-color: #9ca3af !important;
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

# ---------------------------------------------------
# [Chapter 1] 데이터 바구니 (유지)
# ---------------------------------------------------
if 'current_menu' not in st.session_state:
    st.session_state.current_menu = "1. 영화 목록"
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None
if 'selected_label' not in st.session_state:
    st.session_state.selected_label = None
if 'auto_start' not in st.session_state:
    st.session_state.auto_start = False
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'final_result' not in st.session_state:
    st.session_state.final_result = None
if 'opinion_groups' not in st.session_state:
    st.session_state.opinion_groups = []
if 'selected_cluster_id' not in st.session_state:
    st.session_state.selected_cluster_id = None
if 'selected_cluster_label' not in st.session_state:
    st.session_state.selected_cluster_label = ""
if 'reviews_page' not in st.session_state:
    st.session_state.reviews_page = 1
if 'reviews_data' not in st.session_state:
    st.session_state.reviews_data = {"items": [], "total_pages": 1, "total_count": 0}

MOVIE_EMOJI = ["🎬", "🍿", "🎥", "🎞️", "📽️", "🎭", "🌟", "🚀"]
MENU_OPTIONS = ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"]

# ---------------------------------------------------
# 🚨 사이드바 구성
# ---------------------------------------------------
if st.sidebar.button("🏠 Home", use_container_width=True, key="home_btn"):
    st.session_state.current_menu = "1. 영화 목록"
    st.session_state.selected_label = None
    st.session_state.selected_cluster_id = None
    st.rerun()

st.sidebar.title("🎬 영화 분석 시스템")
menu_radio = st.sidebar.radio(
    "메뉴 이동",
    MENU_OPTIONS,
    index=MENU_OPTIONS.index(st.session_state.current_menu),
    key="main_menu_radio"
)

if st.session_state.get("_prev_menu_radio") != menu_radio:
    if st.session_state.get("_prev_menu_radio") is not None:
        st.session_state.current_menu = menu_radio
st.session_state["_prev_menu_radio"] = menu_radio
menu = st.session_state.current_menu


# ---------------------------------------------------
# [메뉴 1] 영화 목록 
# ---------------------------------------------------
if menu == "1. 영화 목록":
    st.title("🍿 분석 대상 영화 목록")
    try:
        res = requests.get(f"{BASE_URL}/movies", timeout=2)
        res.raise_for_status()
        movie_list = res.json()
    except:
        movie_list = FALLBACK_DATA["movie_list"]

    for i, movie in enumerate(movie_list):
        emoji = MOVIE_EMOJI[i % len(MOVIE_EMOJI)]
        is_selected = st.session_state.selected_movie_id is not None and st.session_state.selected_movie_id == movie['movie_id']

        with st.container(border=True):
            col_thumb, col_info, col_btn = st.columns([1, 6, 2])
            with col_thumb:
                st.markdown(f"<div style='font-size:28px; padding: 8px 0;'>{emoji}</div>", unsafe_allow_html=True)
            with col_info:
                st.markdown(f"**{movie['movie_title']}**")
                st.markdown(
                    f"<span style='font-size:11px; background:#f1f3f5; color:#6c757d; border:0.5px solid #dee2e6; border-radius:20px; padding:2px 8px; margin-right:6px;'>{movie['release_year']}</span>"
                    f"<span style='font-size:11px; background:#e7f1ff; color:#1971c2; border-radius:20px; padding:2px 8px;'>{movie['source']}</span>",
                    unsafe_allow_html=True
                )
                st.caption(movie['movie_id'])
            with col_btn:
                btn_label = "✓ 선택됨" if is_selected else "선택"
                btn_type = "primary" if is_selected else "secondary"
                if st.button(btn_label, key=f"sel_{movie['movie_id']}", use_container_width=True, type=btn_type):
                    st.session_state.selected_movie_id = movie['movie_id']
                    st.session_state.selected_label = None
                    st.session_state.auto_start = True
                    st.session_state.current_menu = "2. 분석 요청(배치)"
                    st.rerun()

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

    should_run = st.session_state.auto_start
    if st.button("🚀 분석 시작") or should_run:
        st.session_state.auto_start = False 
        payload = {"movie_id": st.session_state.selected_movie_id, "target_date": str(target_date)}
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            try:
                st.write("📡 분석 서버 호출 중...")
                post_res = requests.post(f"{BASE_URL}/batch/jobs", json=payload, timeout=2)
                job = post_res.json()
                st.session_state.job_id = job['job_id'] 
                
                curr_status = job.get('status', 'queued')
                while curr_status not in ["completed", "failed"]:
                    time.sleep(2)
                    poll = requests.get(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}", timeout=2)
                    curr_status = poll.json()['status']
                    st.write(f"🔄 현재 상태: `{curr_status}`")
                
                status.update(label=f"🏁 작업 {curr_status}!", state="complete" if curr_status=="completed" else "error")
                if curr_status == "completed":
                    st.session_state.analysis_done = True
            except:
                st.error("🚨 서버 연결 불가. 시뮬레이션을 시작합니다.")
                st.session_state.job_id = "simulated-job-id"
                for s in ["queued", "collecting_reviews", "llm_processing", "clustering", "completed"]:
                    st.write(f"🕒 가상 상태: `{s}`")
                    time.sleep(0.5)
                status.update(label="✅ 시뮬레이션 완료", state="complete")
                st.session_state.analysis_done = True

    if st.session_state.get("analysis_done"):
        st.success("🎉 분석이 완료되었습니다!")
        if st.button("📊 분석 결과 보기 →", type="primary", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.current_menu = "3. 분석 결과 보기"
            st.rerun()

# ---------------------------------------------------
# 🚀 [Chapter 2] 메뉴 3: 분석 결과 (상단 요약 적용)
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    mid = st.session_state.selected_movie_id
    st.title(f"📊 분석 리포트")
    st.caption(f"대상 영화 ID: {mid}")
    
    # --- 1. 데이터 로드 (API 연결 전 더미 데이터 세팅) ---
    if not st.session_state.final_result:
        # 작업 지시서에 명시된 형태의 가상 데이터
        st.session_state.final_result = {
            "summary": {
                "top_opinions": [
                    {"label": "연기가 좋아요", "count": 732},
                    {"label": "스토리가 아쉬워요", "count": 451},
                    {"label": "영상미가 좋아요", "count": 388}
                ],
                "sentiment_ratio": {
                    "positive": 78,
                    "negative": 22
                }
            }
        }
    
    summary_data = st.session_state.final_result["summary"]

    # --- 2. 상단 요약 UI 구현 ---
    st.subheader("🏆 많이 나온 의견 TOP 3")
    
    # 3개의 컬럼을 만들어 순위별로 배치
    col1, col2, col3 = st.columns(3)
    top_ops = summary_data["top_opinions"]
    
    if len(top_ops) > 0:
        col1.metric("🥇 1위", top_ops[0]["label"], f"{top_ops[0]['count']}건")
    if len(top_ops) > 1:
        col2.metric("🥈 2위", top_ops[1]["label"], f"{top_ops[1]['count']}건")
    if len(top_ops) > 2:
        col3.metric("🥉 3위", top_ops[2]["label"], f"{top_ops[2]['count']}건")

    st.divider()

    # --- 3. 긍정/부정 비율 UI 구현 ---
    st.subheader("💡 긍정/부정 비율")
    pos_percent = summary_data["sentiment_ratio"]["positive"]
    neg_percent = summary_data["sentiment_ratio"]["negative"]
    
    c1, c2 = st.columns(2)
    c1.write(f"**😊 긍정 {pos_percent}%**")
    c2.write(f"<div style='text-align: right;'>**🤔 부정 {neg_percent}%**</div>", unsafe_allow_html=True)
    
    # 게이지 바 추가 (0.0 ~ 1.0 사이 값)
    st.progress(pos_percent / 100.0)
    
    st.divider()

    # --- 기존 코드 임시 유지 (더 많은 의견 보기 영역) ---
    st.subheader("📂 더 많은 의견 보기 (임시 데이터)")
    try:
        res = requests.get(f"{BASE_URL}/movies/{mid}/review-summary", timeout=2)
        data = res.json()
    except:
        data = FALLBACK_DATA["result_data"]

    for item in data["review_summary"]:
        with st.container(border=True):
            if st.button(f"✨ {item['label']}", key=f"btn_{item['label']}", use_container_width=True):
                st.session_state.selected_label = None if st.session_state.selected_label == item['label'] else item['label']
            st.progress(float(item['ratio']))
            if st.session_state.selected_label == item['label']:
                st.divider()
                with st.container(height=300):
                    for ex in item['examples']:
                        st.markdown(f"> {ex}")