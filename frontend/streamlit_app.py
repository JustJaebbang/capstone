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

# 🚨 찬우님의 디자인 가이드라인 (바둑판 배열 업데이트!)
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
/* 🚀 [핵심] 본문(Chapter 3) 리뷰 버튼 3열 바둑판 배열! */
    div[data-testid="stMain"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        /* ✨ [긴급 보강] 내용물이 없어도 박스 형태를 유지하도록 최소 높이 추가! */
        min-height: 100px !important; 
        border: 1px solid #e0e0e0 !important; /* 항상 보이는 바깥 테두리 */
        border-radius: 12px !important;
        padding: 10px !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stMain"] div[role="radiogroup"] label {
        width: auto !important;
        flex: 1 1 calc(33.333% - 10px) !important; /* 한 줄에 3개씩 쏙쏙! */
        min-width: 220px !important;
        margin-bottom: 0 !important;
        justify-content: center !important; /* 글자 가운데 정렬 */
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

# API 연동을 위한 필수 바구니들
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
    st.session_state.selected_movie_id = None
    st.session_state.selected_label = None
    st.session_state.selected_cluster_id = None
    st.session_state.job_id = None # 쓰레기값 청소
    st.session_state.final_result = None # 쓰레기값 청소
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
# 🚀 [메뉴 2] 분석 요청 (4단계 자동화 버전)
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

    should_run = st.session_state.auto_start
    if st.button("🚀 분석 시작") or should_run:
        st.session_state.auto_start = False 
        payload = {"movie_id": st.session_state.selected_movie_id, "target_date": str(target_date)}
        
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            try:
                # 1단계: Job 생성
                st.write("📡 1/4: 분석 작업 생성 중...")
                post_res = requests.post(f"{BASE_URL}/batch/jobs", json=payload, timeout=30)
                post_res.raise_for_status()
                st.session_state.job_id = post_res.json()['job_id']
                
                # 2단계: LLM 실행 (넉넉하게 대기)
                st.write("🧠 2/4: AI 모델 분석 중... ")
                requests.post(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/run-llm", timeout=300)
                
                # 3단계: 클러스터링 실행 (hdbscan 모드 파라미터 추가)
                st.write("✨ 3/4: 비슷한 의견 그룹화 중...")
                requests.post(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/run-cluster", json={"cluster_mode": "hdbscan"}, timeout=300)
                
                # 4단계: 최종 결과 빌드
                st.write("📦 4/4: 최종 요약 리포트 생성 중...")
                requests.post(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/build-final", timeout=60)
                
                status.update(label="🏁 모든 분석 완료!", state="complete")
                st.session_state.analysis_done = True
                
            except Exception as e:
                st.error(f"🚨 서버 에러 또는 타임아웃 발생: {e}")
                status.update(label="에러 발생", state="error")
                st.session_state.job_id = None # 가짜 ID 생성 방지

    if st.session_state.get("analysis_done"):
        st.success("🎉 분석이 완벽하게 완료되었습니다!")
        if st.button("📊 분석 결과 보기 →", type="primary", use_container_width=True):
            st.session_state.analysis_done = False
            # 결과 화면으로 가기 전에 이전 결과 초기화
            st.session_state.final_result = None 
            st.session_state.current_menu = "3. 분석 결과 보기"
            st.rerun()

# ---------------------------------------------------
# 🚀 [메뉴 3: 분석 결과 (진짜 API 연동 + 이름표 수정 완료!)]
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    st.title(f"📊 분석 리포트")
    
    # 예외 처리: job_id가 없으면 경고
    if not st.session_state.job_id:
        st.warning("📭 아직 분석된 작업이 없습니다. [1. 영화 목록] 메뉴에서 영화를 다시 선택하고 분석해주세요.")
        st.stop()
        
    st.caption(f"작업 ID: {st.session_state.job_id}")
    
    # --- 1. 진짜 API 호출 (final-result) ---
    if st.session_state.final_result is None:
        with st.spinner("분석 요약 결과를 불러오는 중..."):
            try:
                res = requests.get(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/final-result", timeout=5)
                res.raise_for_status()
                st.session_state.final_result = res.json()
            except Exception as e:
                st.error(f"API 호출 실패: {e}")
                st.stop() # 에러 나면 여기서 멈춤

    # 데이터 안전하게 가져오기
    summary_data = st.session_state.final_result.get("summary", st.session_state.final_result)

    # --- 2. 상단 요약 UI 구현 ---
    st.subheader("🏆 많이 나온 의견 TOP 3")
    
    col1, col2, col3 = st.columns(3)
    top_ops = summary_data.get("top_opinions", [])
    
    if len(top_ops) > 0:
        col1.metric("🥇 1위", top_ops[0]["label"], f"{top_ops[0]['count']}건")
    if len(top_ops) > 1:
        col2.metric("🥈 2위", top_ops[1]["label"], f"{top_ops[1]['count']}건")
    if len(top_ops) > 2:
        col3.metric("🥉 3위", top_ops[2]["label"], f"{top_ops[2]['count']}건")

    st.divider()

    # --- 3. 긍정/부정 비율 UI 구현 (✨ 버그 수정 완료) ---
    st.subheader("💡 긍정/부정 비율")
    
    # 백엔드가 주는 '진짜 이름표'로 수정 완료!
    sentiment = summary_data.get("sentiment_ratio", {"positive_percent": 0, "negative_percent": 0})
    pos_percent = sentiment.get("positive_percent", 0)
    neg_percent = sentiment.get("negative_percent", 0)
    
    c1, c2 = st.columns(2)
    c1.write(f"**😊 긍정 {pos_percent}%**")
    c2.write(f"<div style='text-align: right;'>**🤔 부정 {neg_percent}%**</div>", unsafe_allow_html=True)
    
    try:
        st.progress(float(pos_percent) / 100.0)
    except:
        st.progress(0.0)
        
    st.divider()

# --- 4. 챕터 3: 의견 그룹 및 진짜 리뷰 상세 보기 🚀 ---
    st.divider()
    st.subheader("💬 의견 그룹별 상세 리뷰")
    
    # 1) 전체 의견 그룹(클러스터) 목록 가져오기
    if not st.session_state.opinion_groups:
        with st.spinner("의견 그룹을 분석하는 중..."):
            try:
                res = requests.get(f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/opinion-groups", timeout=5)
                res.raise_for_status()
                data = res.json()
                # 데이터가 리스트인지 확인하는 방어 코드 포함
                st.session_state.opinion_groups = data if isinstance(data, list) else data.get("groups", data.get("items", []))
            except Exception as e:
                st.session_state.opinion_groups = []
                
    groups = st.session_state.opinion_groups
    
    # ✨ 방어막: groups가 정상적인 리스트일 때만 UI를 그립니다.
    if groups and isinstance(groups, list) and len(groups) > 0:
        # 2) 의견 그룹 선택 라디오 버튼 (CSS에 의해 3열 바둑판으로 보임)
        g_opts = {g['cluster_id']: f"✨ {g['label']} ({g.get('count', 0)}건)" for g in groups}
        
        if st.session_state.selected_cluster_id not in g_opts:
            st.session_state.selected_cluster_id = groups[0]['cluster_id']
            
        selected_id = st.radio(
            "궁금한 의견을 선택해서 진짜 리뷰를 확인해 보세요!",
            options=list(g_opts.keys()),
            format_func=lambda x: g_opts[x],
            horizontal=True,
            key="cluster_radio_final"
        )
        
        # 선택된 그룹이 바뀌면 페이지를 1로 되돌림
        if selected_id != st.session_state.selected_cluster_id:
            st.session_state.selected_cluster_id = selected_id
            st.session_state.reviews_page = 1
            st.rerun()

        # 선택한 클러스터의 이름표 추출
        selected_group = next((g for g in groups if g['cluster_id'] == selected_id), {})
        clean_label = selected_group.get('label', '선택된 의견')

        # 3) 선택된 그룹의 실제 리뷰 원문 가져오기
        try:
            page = st.session_state.reviews_page
            size = 10 # 팀장님 요구사항에 맞춰 10개씩
            rev_res = requests.get(
                f"{BASE_URL}/batch/jobs/{st.session_state.job_id}/opinion-groups/{st.session_state.selected_cluster_id}/reviews",
                params={"page": page, "page_size": size}, 
                timeout=30
            )
            rev_res.raise_for_status()
            reviews_data = rev_res.json()
            
          # 임시 디버그 - API 응답 구조 확인용
            

            items = reviews_data.get("reviews", []) if isinstance(reviews_data, dict) else []
            total_count = reviews_data.get("total_count", 0)
            total_pages = reviews_data.get("total_pages", 1)
            # 🎯 UI 1: 상단 정보 표시 (기획서 8번 스타일)
            st.markdown(f"#### 🔎 {clean_label} - 리뷰 목록")
            st.markdown(f"<div style='background-color:#f8f9fa; padding:10px; border-radius:10px; color:#555; font-weight:500;'>📊 total_count: {total_count} 건</div>", unsafe_allow_html=True)
            st.write("") 
            
            # 리뷰 출력
            if not items:
                st.info("해당 의견에 대한 리뷰를 불러오는 중입니다...")
            
            for i, item in enumerate(items):
                s_label = item.get('sentiment', 'neutral').lower()
                emo = "😊" if s_label == "positive" else "🤔" if s_label == "negative" else "😐"
                
                with st.container(border=True):
                    review_num = (page - 1) * size + i + 1 
                    st.markdown(f"<div style='font-size:13px; color:#1f77b4; font-weight:bold;'>리뷰 {review_num}</div>", unsafe_allow_html=True)
                    st.markdown(f"**{emo} {item.get('text', '내용이 없습니다.')}**")
                    
            # 🎯 UI 2: 하단 페이징 (이전 - 페이지 번호 중앙 - 다음)
            st.write("") 
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if page > 1:
                    if st.button("⬅️ 이전", use_container_width=True):
                        st.session_state.reviews_page -= 1
                        st.rerun()
            with col2:
                # 페이지 번호를 중앙에 예쁘게 배치
                st.markdown(f"<div style='text-align:center; padding-top:8px; font-weight:bold; color:#333;'>Page {page} / {total_pages}</div>", unsafe_allow_html=True)
            with col3:
                if page < total_pages: 
                    if st.button("다음 ➡️", use_container_width=True):
                        st.session_state.reviews_page += 1
                        st.rerun()
                        
        except Exception as e:
            st.warning("리뷰 데이터를 불러오는 중입니다. 잠시만 기다려주세요.")
    else:
        # 데이터가 아예 없을 때 보여줄 빈 박스 UI
        st.info("💡 표시할 의견 그룹이 없습니다. 분석이 완료될 때까지 잠시만 기다려주시거나 [메뉴 2]를 확인해 주세요.")