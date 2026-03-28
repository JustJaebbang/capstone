import streamlit as st
import json
import time

# [1-4 단계] 데이터 불러오기 함수
def get_all_data():
    try:
        with open('dummy_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("🚨 dummy_data.json 파일을 찾을 수 없습니다!")
        return None

data = get_all_data()

# 사이드바 설정
st.sidebar.title("🎬 영화 분석 시스템")
menu = st.sidebar.radio("메뉴 이동", ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"])

# ---------------------------------------------------
# [메뉴 1] 영화 목록 (규칙: source, is_active, registered_at 등 반영)
# ---------------------------------------------------
if menu == "1. 영화 목록":
    st.title("🍿 분석 대상 영화 목록")
    st.info("💡 GET /movies 연동 및 공통 필드 규칙 적용 완료")
    
    for movie in data["movie_list"]:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            # 제목과 개봉 연도
            col1.subheader(f"{movie['movie_title']} ({movie['release_year']})")
            
            # [규칙 반영] 상세 필드 노출
            details = f"🆔 ID: `{movie['movie_id']}` | 🌐 출처: `{movie['source']}` | 📅 등록: `{movie['registered_at'].split('T')[0]}`"
            col1.write(details)
            
            # [규칙 반영] 활성 여부 표시
            status_tag = "✅ 분석 가능" if movie['is_active'] else "❌ 분석 불가"
            col1.caption(f"상태: {status_tag} | 메모: {movie['notes']}")
            
            if col2.button("선택", key=f"btn_{movie['movie_id']}"):
                st.toast(f"'{movie['movie_title']}'가 선택되었습니다.")

# ---------------------------------------------------
# [메뉴 2] 분석 요청(배치) (규칙: status 흐름 반영)
# ---------------------------------------------------
elif menu == "2. 분석 요청(배치)":
    st.title("⚙️ 분석 요청하기")
    batch = data['batch_response']
    
    movie_names = [m['movie_title'] for m in data["movie_list"]]
    selected_movie = st.selectbox("어떤 영화를 분석할까요?", movie_names)
    target_date = st.date_input("분석 기준 날짜", value=st.to_datetime(batch['target_date']))
    
    if st.button("분석 서버에 요청 보내기"):
        # [1-5 단계] 상태 흐름(Status Flow) 시뮬레이션
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            st.write(f"작업 생성 중... (`created_at`: {batch['created_at']})")
            time.sleep(0.5)
            st.write("리뷰 수집 중... (`collecting_reviews`)")
            time.sleep(0.8)
            st.write("AI 분석 중... (`llm_processing`)")
            time.sleep(1.0)
            # 규칙 반영: 'success' 대신 'completed' 사용
            status.update(label=f"✅ 작업 완료! 상태: {batch['status']}", state="complete", expanded=False)
            
        st.success(f"요청 성공! Job ID: `{batch['job_id']}`")
        st.info(f"작업 종료 시각: `{batch['finished_at']}`")

# ---------------------------------------------------
# [메뉴 3] 분석 결과 보기
# ---------------------------------------------------
elif menu == "3. 분석 결과 보기":
    res = data["result_data"]
    st.title(f"📊 {res['movie_title']} 분석 결과")
    
    # ISO 날짜 처리
    clean_date = res['analysis_date'].split('T')