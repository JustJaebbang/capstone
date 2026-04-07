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

    /* ✨ 영화 카드 스타일 */
    .movie-card {
        display: flex;
        align-items: center;
        gap: 16px;
        background: #ffffff;
        border: 0.5px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        transition: border-color 0.15s ease;
    }
    .movie-card:hover {
        border-color: #adb5bd;
        background-color: #fafbfc;
    }
    .movie-thumb {
        width: 48px;
        height: 64px;
        border-radius: 6px;
        background: #f1f3f5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    .movie-info {
        flex: 1;
        min-width: 0;
    }
    .movie-title {
        font-size: 15px;
        font-weight: 600;
        color: #1a1a2e;
        margin: 0 0 6px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .movie-badges {
        display: flex;
        gap: 6px;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 4px;
    }
    .badge-year {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 20px;
        font-weight: 500;
        background: #f1f3f5;
        color: #6c757d;
        border: 0.5px solid #dee2e6;
    }
    .badge-source {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 20px;
        font-weight: 500;
        background: #e7f1ff;
        color: #1971c2;
    }
    .movie-id {
        font-size: 11px;
        color: #adb5bd;
        font-family: monospace;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

with open(DUMMY_PATH, 'r', encoding='utf-8') as f:
    FALLBACK_DATA = json.load(f)

# 2. 세션 상태 초기화
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None
if 'selected_label' not in st.session_state:
    st.session_state.selected_label = None
if 'auto_start' not in st.session_state:
    st.session_state.auto_start = False
if 'current_menu' not in st.session_state:
    st.session_state.current_menu = "1. 영화 목록"
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# 영화 장르별 이모지 매핑
MOVIE_EMOJI = ["🎬", "🍿", "🎥", "🎞️", "📽️", "🎭", "🌟", "🚀"]
MENU_OPTIONS = ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"]

# ---------------------------------------------------
# 🚨 사이드바 구성
# ---------------------------------------------------
if st.sidebar.button("🏠 Home", use_container_width=True, key="home_btn"):
    st.session_state.current_menu = "1. 영화 목록"
    st.session_state.selected_label = None
    st.rerun()

st.sidebar.title("🎬 영화 분석 시스템")
menu_radio = st.sidebar.radio(
    "메뉴 이동",
    MENU_OPTIONS,
    index=MENU_OPTIONS.index(st.session_state.current_menu),
    key="main_menu_radio"
)
# 사용자가 직접 사이드바 클릭 시에만 current_menu 업데이트
if st.session_state.get("_prev_menu_radio") != menu_radio:
    if st.session_state.get("_prev_menu_radio") is not None:
        st.session_state.current_menu = menu_radio
st.session_state["_prev_menu_radio"] = menu_radio
menu = st.session_state.current_menu


# ---------------------------------------------------
# [메뉴 1] 영화 목록 - 개선된 카드 UI
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

    for i, movie in enumerate(movie_list):
        emoji = MOVIE_EMOJI[i % len(MOVIE_EMOJI)]
        is_selected = st.session_state.selected_movie_id is not None and st.session_state.selected_movie_id == movie['movie_id']

        # 카드 + 버튼을 하나의 container 안에
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

    # 영화 목록에서 선택 시 자동 실행, 아니면 버튼 클릭 시 실행
    should_run = st.session_state.auto_start
    if st.button("🚀 분석 시작") or should_run:
        st.session_state.auto_start = False  # 플래그 초기화
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
                if curr_status == "completed":
                    st.session_state.analysis_done = True
            except:
                st.error("🚨 서버 연결 불가. 시뮬레이션을 시작합니다.")
                for s in ["queued", "collecting_reviews", "llm_processing", "clustering", "saving_results", "completed"]:
                    st.write(f"🕒 가상 상태: `{s}`")
                    time.sleep(0.5)
                status.update(label="✅ 시뮬레이션 완료", state="complete")
                st.session_state.analysis_done = True

    # 분석 완료 후 결과 보기 버튼 (if 블록 밖)
    if st.session_state.get("analysis_done"):
        st.success("🎉 분석이 완료되었습니다!")
        if st.button("📊 분석 결과 보기 →", type="primary", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.current_menu = "3. 분석 결과 보기"
            st.rerun()


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