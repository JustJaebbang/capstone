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

# 🚨 찬우님의 디자인 가이드라인 (바둑판 + 텍스트 잘림 방지 + Top3 카드 개조 + 버튼 색상 복구)
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

    /* 2. 라디오 버튼 공통 스타일 (버튼 모양) */
    div[role="radiogroup"] label {
        display: flex !important;
        padding: 12px 16px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        align-items: center !important;
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

    /* 라벨 텍스트 기본 스타일 */
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

    /* 🚀 본문(Chapter 3) 리뷰 버튼 3열 바둑판 배열! */
    div[data-testid="stMain"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        min-height: 100px !important; 
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 10px !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stMain"] div[role="radiogroup"] label {
        width: auto !important;
        flex: 1 1 calc(33.333% - 10px) !important;
        min-width: 220px !important;
        margin-bottom: 0 !important;
        justify-content: center !important;
    }
    div[data-testid="stMain"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        text-align: center !important;
    }

    /* 🛡️ 사이드바 메뉴는 망가지지 않게 세로로 꽉 차게 유지 */
    div[data-testid="stSidebar"] div[role="radiogroup"] label {
        width: 100% !important;
        justify-content: flex-start !important;
        margin-bottom: 8px !important;
    }

    /* 🔥 [핵심 추가] TOP 3 버튼 텍스트 잘림(...) 방지 및 예쁜 카드 스타일링 */
    div[data-testid="stButton"] button p {
        white-space: pre-wrap !important; 
        word-break: keep-all !important;
        line-height: 1.5 !important;
        font-size: 16px !important;
    }

    /* 🤍 일반 버튼 (TOP 3 카드 등) 스타일 */
    div[data-testid="stButton"] button[kind="secondary"] {
        height: auto !important; 
        padding: 20px 10px !important;
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stButton"] button[kind="secondary"] p {
        color: #31333F !important; /* 까만 글씨 강제 적용 */
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #1f77b4 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* 💙 Primary 버튼 (분석 결과 보기) 전용 스타일 구출 작전! */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #1f77b4 !important; /* 파란색 배경 */
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
    }
    div[data-testid="stButton"] button[kind="primary"] p {
        color: #ffffff !important; /* 하얀색 글씨 */
        font-weight: bold !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #155a8a !important; /* 마우스 올리면 더 진한 파란색 */
    }
    </style>
""", unsafe_allow_html=True)

with open(DUMMY_PATH, 'r', encoding='utf-8') as f:
    FALLBACK_DATA = json.load(f)

# ---------------------------------------------------
# [Chapter 1] 데이터 바구니 
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

# 🔥 [새로 추가] 리뷰 게시판이 나타날 위치를 기억하는 변수!
if 'active_review_section' not in st.session_state:
    st.session_state.active_review_section = "top3" # 기본값은 TOP 3 밑!

MOVIE_EMOJI = ["🎬", "🍿", "🎥", "🎞️", "📽️", "🎭", "🌟", "🚀"]
MENU_OPTIONS = ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"]

# ---------------------------------------------------
# 🚨 사이드바 구성
# ---------------------------------------------------
if st.sidebar.button("🏠 Home", use_container_width=True, key="home_btn"):
    st.session_state.current_menu = "1. 영화 목록"
    st.session_state.selected_movie_id = None
    st.session_state.selected_label = None
    st.session_state.selected_cluster_id = None
    st.session_state.job_id = None 
    st.session_state.final_result = None 
    st.session_state.active_review_section = "top3"
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
                    st.session_state.active_review_section = "top3"
                    st.session_state.current_menu = "2. 분석 요청(배치)"
                    st.rerun()

# ---------------------------------------------------
# 🚀 [메뉴 2] 분석 요청 
# ---------------------------------------------------
elif menu == "2. 분석 요청(배치)":
    st.title("⚙️ 분석 요청하기")
    try:
        m_res = requests.get(f"{BASE_URL}/movies", timeout=2)
        m_list = m_res.json()
    except:
        m_list = FALLBACK_DATA["movie_list"]
        
    movie_names = [m['movie_title'] for m in m_list]
    current_idx = next((i for i, m in enumerate(m_list) if m['movie_id'] == st.session_state.selected_movie_id), 0)
    
    selected_title = st.selectbox("분석 대상 영화", movie_names, index=current_idx)
    target_date = st.date_input("기준 날짜", value=datetime.now())

    selected_movie = next((m for m in m_list if m["movie_title"] == selected_title), None)

    if selected_movie:
        st.session_state.selected_movie_id = selected_movie["movie_id"]

    should_run = st.session_state.auto_start
    if st.button("🚀 분석 시작") or should_run:
        st.session_state.auto_start = False 
        
        if not selected_movie:
            st.error("❌ 선택한 영화 정보를 찾을 수 없습니다. 영화 목록을 다시 확인해 주세요.")
            st.stop()

        payload = {
            "movie_id": str(selected_movie["movie_id"]), 
            "target_date": target_date.isoformat()       
        }
        
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            try:
                st.write("📡 1/4: 분석 작업 생성 중...")
                post_res = requests.post(f"{BASE_URL}/batch/jobs", json=payload, timeout=30)
                
                if post_res.status_code == 422:
                    st.error(f"데이터 검증 실패(422): {post_res.text}")
                    st.stop()
                    
                post_res.raise_for_status()
                st.session_state.job_id = post_res.json()['job_id']
                
                st.write("🧠 2/4: AI 모델 분석 중... ")
                requests.post(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/run-llm", timeout=300)
                
                st.write("✨ 3/4: 비슷한 의견 그룹화 중...")
                requests.post(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/run-cluster", json={"cluster_mode": "hdbscan"}, timeout=300)
                
                st.write("📦 4/4: 최종 요약 리포트 생성 중...")
                requests.post(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/build-final", timeout=60)
                
                status.update(label="🏁 모든 분석 완료!", state="complete")
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"🚨 에러 발생: {e}")
                status.update(label="에러 발생", state="error")

    if st.session_state.get("analysis_done"):
        st.success("🎉 분석이 완벽하게 완료되었습니다!")
        if st.button("📊 분석 결과 보기 →", type="primary", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.final_result = None 
            st.session_state.opinion_groups = []
            st.session_state.active_review_section = "top3"
            st.session_state.current_menu = "3. 분석 결과 보기"
            st.rerun()

# ---------------------------------------------------
# 🚀 [메뉴 3: 분석 결과 - UX 마스터피스!]
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    if not st.session_state.job_id:
        st.warning("📭 아직 분석된 작업이 없습니다. [1. 영화 목록] 메뉴에서 영화를 다시 선택하고 분석해주세요.")
        st.stop()
        
    # --- 1. 진짜 API 호출 ---
    if st.session_state.final_result is None:
        with st.spinner("분석 요약 결과를 불러오는 중..."):
            try:
                res = requests.get(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/final-result", timeout=5)
                res.raise_for_status()
                st.session_state.final_result = res.json()
            except Exception as e:
                st.error(f"API 호출 실패: {e}")
                st.stop()

    if not st.session_state.opinion_groups:
        with st.spinner("상세 의견 목록을 준비하는 중..."):
            try:
                res = requests.get(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/opinion-groups", timeout=5)
                res.raise_for_status()
                data = res.json()
                st.session_state.opinion_groups = data if isinstance(data, list) else data.get("groups", data.get("items", []))
            except Exception as e:
                st.session_state.opinion_groups = []

    summary_data = st.session_state.final_result.get("summary", st.session_state.final_result)
    groups = st.session_state.opinion_groups

    if "other_radio" not in st.session_state:
        st.session_state.other_radio = None

    # 🔥 [마법의 함수] 리뷰 게시판을 '이동식 모듈'로 만들었습니다! 🔥
    def display_review_board(key_prefix):
        selected_group = next((g for g in groups if g['cluster_id'] == st.session_state.selected_cluster_id), {})
        clean_label = selected_group.get('label', '선택된 의견')

        try:
            page = st.session_state.reviews_page
            size = 10 
            
            rev_res = requests.get(
                f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/opinion-groups/{st.session_state.selected_cluster_id}/reviews",
                params={"page": page, "page_size": size}, 
                timeout=10 
            )
            
            if rev_res.status_code == 200:
                reviews_data = rev_res.json()
                items = reviews_data.get("reviews", []) if isinstance(reviews_data, dict) else []
                total_count = reviews_data.get("total_count", 0)
                total_pages = reviews_data.get("total_pages", 1)
            else:
                items, total_count, total_pages = [], 0, 1

            if items:
                st.markdown(f"#### 🔎 {clean_label} - 리뷰 목록")
                st.markdown(f"<div style='background-color:#f8f9fa; padding:10px; border-radius:10px; color:#555; font-weight:500;'>📊 검색된 리뷰: {total_count} 건</div>", unsafe_allow_html=True)
                st.write("") 
                
                for i, item in enumerate(items):
                    s_label = item.get('sentiment', 'neutral').lower()
                    emo = "😊" if s_label == "positive" else "🤔" if s_label == "negative" else "😐"
                    
                    with st.container(border=True):
                        review_num = (page - 1) * size + i + 1 
                        st.markdown(f"<div style='font-size:13px; color:#1f77b4; font-weight:bold;'>리뷰 {review_num}</div>", unsafe_allow_html=True)
                        st.markdown(f"**{emo} {item.get('text', '내용이 없습니다.')}**")
                        
                st.write("") 
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if page > 1:
                        if st.button("⬅️ 이전", key=f"prev_{key_prefix}", use_container_width=True):
                            st.session_state.reviews_page -= 1
                            st.rerun()
                with col2:
                    st.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:bold; color:#333;'>Page {page} / {total_pages}</div>", unsafe_allow_html=True)
                with col3:
                    if page < total_pages: 
                        if st.button("다음 ➡️", key=f"next_{key_prefix}", use_container_width=True):
                            st.session_state.reviews_page += 1
                            st.rerun()
            else:
                st.info("🔄 서버에서 진짜 리뷰 데이터를 불러오거나 정리하는 중입니다. 잠시만 기다려주세요!")
                
        except Exception as e:
            st.warning("서버와 통신하는 중입니다. (분석이 100% 완료되었는지 확인해 주세요!)")


    # --- 2. [통합 영역] 분석 리포트 제목/ID 및 긍정부정 비율 ---
    report_cols = st.columns([2.5, 1]) 
    with report_cols[0]: 
        st.subheader("📊 분석 리포트") 
        st.caption(f"ID: {st.session_state.job_id}") 

    with report_cols[1]: 
        sentiment = summary_data.get("sentiment_ratio", {"positive_percent": 0, "negative_percent": 0})
        pos_percent = sentiment.get("positive_percent", 0)
        neg_percent = sentiment.get("negative_percent", 0)

        st.write(f"<div style='text-align: right; font-size: 0.9rem; font-weight: bold; margin-bottom: 2px;'>"
                 f"😊 긍정 {pos_percent}% &nbsp;&nbsp;&nbsp;&nbsp;🤔 부정 {neg_percent}%"
                 f"</div>", unsafe_allow_html=True)

        try:
            st.progress(float(pos_percent) / 100.0)
        except:
            st.progress(0.0)
    st.write("") 

    # --- 3. 상단 요약 UI (TOP 3) ---
    st.subheader("🏆 많이 나온 의견 TOP 3 (클릭하면 바로 아래에 리뷰가 열려요!)")
    
    col1, col2, col3 = st.columns(3)
    top_ops = summary_data.get("top_opinions", [])
    top3_labels = [op["label"] for op in top_ops] 
    
    for idx, col in enumerate([col1, col2, col3]):
        if len(top_ops) > idx:
            op_data = top_ops[idx]
            label = op_data["label"]
            count = op_data["count"]
            rank_str = ["🥇 1위", "🥈 2위", "🥉 3위"][idx]
            
            btn_label = f"{rank_str}\n\n{label}\n({count}건)"
            
            with col:
                if st.button(btn_label, key=f"top3_btn_{idx}", use_container_width=True):
                    matched_id = next((g['cluster_id'] for g in groups if g['label'] == label), None)
                    if matched_id:
                        st.session_state.selected_cluster_id = matched_id
                        st.session_state.other_radio = None 
                        st.session_state.active_review_section = "top3" # 🌟 TOP3 섹션 활성화!
                        st.session_state.reviews_page = 1
                        st.rerun()

    st.write("") 
    st.markdown("<hr style='margin: 10px 0px 20px 0px; border-top: 2px solid #1f77b4;'>", unsafe_allow_html=True)

    # 🌟 아무것도 안 눌렀을 땐 기본으로 1위(top3)를 띄워줌
    if st.session_state.selected_cluster_id is None and groups:
        st.session_state.selected_cluster_id = groups[0]['cluster_id']
        st.session_state.active_review_section = "top3"

    # 🚀 TOP 3를 눌렀을 때만 여기서 리뷰 게시판 함수 호출!
    if st.session_state.active_review_section == "top3":
        display_review_board("top")

    # --- 4. 그 외 의견 박스 영역 ---
    st.divider()
    st.subheader("💡 그 외의 다양한 의견들도 확인해 보세요!")

    other_groups = [g for g in groups if g['label'] not in top3_labels]

    if other_groups:
        other_opts = {g['cluster_id']: f"✨ {g['label']} ({g.get('count', 0)}건)" for g in other_groups}
        
        st.radio(
            "궁금한 추가 의견을 선택해서 리뷰를 확인해 보세요!",
            options=list(other_opts.keys()),
            format_func=lambda x: other_opts[x],
            horizontal=True,
            key="other_radio",
            index=None 
        )
        
        # '그 외 의견' 라디오 버튼을 클릭하면!
        if st.session_state.other_radio is not None and st.session_state.other_radio != st.session_state.selected_cluster_id:
            st.session_state.selected_cluster_id = st.session_state.other_radio
            st.session_state.active_review_section = "other" # 🌟 하단 섹션 활성화!
            st.session_state.reviews_page = 1
            st.rerun()

        # 🚀 '그 외 의견'을 눌렀을 때만 여기서 리뷰 게시판 함수 호출!
        if st.session_state.active_review_section == "other":
            st.markdown("<hr style='margin: 10px 0px 20px 0px; border-top: 2px solid #2e7d32;'>", unsafe_allow_html=True)
            display_review_board("bottom")
            
    else:
        st.info("TOP 3 외에 추가 의견 그룹이 없습니다.")