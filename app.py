import streamlit as st
import json
import time
from datetime import datetime # 날짜 처리를 위해 추가

def get_all_data():
    try:
        with open('dummy_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

data = get_all_data()

st.sidebar.title("🎬 영화 분석 시스템")
menu = st.sidebar.radio("메뉴 이동", ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"])

if menu == "1. 영화 목록":
    st.title("🍿 분석 대상 영화 목록")
    for movie in data["movie_list"]:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.subheader(f"{movie['movie_title']} ({movie['release_year']})")
            details = f"🆔 ID: `{movie['movie_id']}` | 🌐 출처: `{movie['source']}` | 📅 등록: `{movie['registered_at'].split('T')[0]}`"
            col1.write(details)
            status_tag = "✅ 분석 가능" if movie['is_active'] else "❌ 분석 불가"
            col1.caption(f"상태: {status_tag} | 메모: {movie['notes']}")
            if col2.button("선택", key=f"btn_{movie['movie_id']}"):
                st.toast(f"'{movie['movie_title']}'가 선택되었습니다.")

elif menu == "2. 분석 요청(배치)":
    st.title("⚙️ 분석 요청하기")
    batch = data['batch_response']
    movie_names = [m['movie_title'] for m in data["movie_list"]]
    selected_movie = st.selectbox("어떤 영화를 분석할까요?", movie_names)
    
    # 🚨 에러 해결 포인트: datetime.strptime 사용
    t_date = datetime.strptime(batch['target_date'], '%Y-%m-%d')
    target_date = st.date_input("분석 기준 날짜", value=t_date)
    
    if st.button("분석 서버에 요청 보내기"):
        with st.status("배치 작업 진행 중...", expanded=True) as status:
            st.write(f"작업 생성 중... (`created_at`: {batch['created_at']})")
            time.sleep(0.5)
            st.write("리뷰 수집 중... (`collecting_reviews`)")
            time.sleep(0.8)
            st.write("AI 분석 중... (`llm_processing`)")
            time.sleep(1.0)
            status.update(label=f"✅ 작업 완료! 상태: {batch['status']}", state="complete", expanded=False)
        st.success(f"요청 성공! Job ID: `{batch['job_id']}`")

elif menu == "3. 분석 결과 보기":
    res = data["result_data"]
    st.title(f"📊 {res['movie_title']} 분석 결과")
    clean_date = res['analysis_date'].split('T')[0]
    st.write(f"**총 리뷰:** {res['total_reviews']}건 | **최종 분석일:** {clean_date}")
    st.divider()
    col1, col2 = st.columns(2)
    cards = [col1, col2]
    for i, item in enumerate(res["review_summary"]):
        with cards[i % 2]:
            st.success(f"**{item['label']} ({item['ratio']}%)**")
            st.write(f"📈 건수: {item['count']}건")
            with st.expander("대표 리뷰 보기"):
                for example in item['examples']:
                    st.write(f"💬 {example}")