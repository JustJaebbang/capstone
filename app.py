import streamlit as st
import json

# 데이터 불러오기
with open('dummy_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 왼쪽 사이드바에 3가지 메뉴 만들기
st.sidebar.title("영화 분석 시스템")
menu = st.sidebar.radio("메뉴 이동", ["1. 영화 목록", "2. 분석 요청(배치)", "3. 분석 결과 보기"])

# ---------------------------------------------------
# [메뉴 1] 영화 목록 (GET /movies 기준)
if menu == "1. 영화 목록":
    st.title("🎬 분석 대상 영화 목록")
    st.write("`GET /movies` 연동을 위한 영화 목록입니다.")
    
    for movie in data["movie_list"]:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.subheader(f"🍿 {movie['movie_title']} ({movie['release_year']})")
            col1.write(f"데이터 연동 ID: `{movie['movie_id']}`")
            if col2.button("이 영화 선택", key=f"btn_{movie['movie_id']}"):
                st.success(f"'{movie['movie_title']}' 영화가 선택되었습니다!")

# ---------------------------------------------------
# [메뉴 2] 분석 요청 (POST /batch/jobs 기준)
elif menu == "2. 분석 요청(배치)":
    st.title("⚙️ 분석 요청하기")
    st.write("`POST /batch/jobs` 연결 준비 완료!")
    
    movie_name = st.selectbox("어떤 영화를 분석할까요?", ["파묘", "듄: 파트 2"])
    target_date = st.date_input("분석 기준 날짜 (target_date)")
    
    if st.button("분석 서버에 요청 보내기"):
        st.success(f"요청 성공! 발급된 Job ID: `{data['batch_response']['job_id']}`")
        st.write(f"({target_date} 기준으로 '{movie_name}' 분석을 시작합니다.)")

# ---------------------------------------------------
# [메뉴 3] 분석 결과 보기 (GET /movies/{movie_id}/review-summary 기준)
elif menu == "3. 분석 결과 보기":
    res = data["result_data"]
    st.title(f"📊 {res['movie_title']} 분석 결과")
    st.write(f"총 리뷰 수: {res['total_reviews']}건 | 분석일: {res['analysis_date']}")
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    cards = [col1, col2]
    
    # 🚨 여기가 지령에 맞춰 review_summary로 변경된 부분입니다!
    for i, item in enumerate(res["review_summary"]):
        with cards[i]:
            st.success(f"**{item['label']} ({item['ratio']}%)**")
            st.write(f"- 건수: {item['count']}건")
            st.write(f"- 대표 예시: {item['examples'][0]}")