import os
import streamlit as st
from supabase import create_client, Client

# 환경 변수에서 Supabase 설정 불러오기
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# 환경 변수가 설정되지 않은 경우 안내
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ 환경 변수 'SUPABASE_URL' 또는 'SUPABASE_KEY'가 설정되지 않았습니다.")
    st.info("터미널에서 환경 변수를 설정하거나, 시스템 환경 변수를 등록한 후 앱을 다시 실행해 주세요.")
    st.stop()

# Supabase 클라이언트 초기화 (캐시 적용)
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# 페이지 설정
st.set_page_config(page_title="한 줄 건의함 (Supabase 연동)", page_icon="📮", layout="centered")

st.title("📮 한 줄 건의함")
st.caption("자유롭게 한 줄 건의사항을 남겨주세요. (Supabase 실시간 연동)")

# 입력 폼 구성
with st.form(key="suggestion_form", clear_on_submit=True):
    # category 칸 대응을 위한 카테고리 선택
    category = st.selectbox(
        "카테고리",
        options=["일반", "기능 요청", "버그 신고", "기타"],
        label_visibility="collapsed"
    )
    user_input = st.text_input(
        label="건의 내용",
        placeholder="건의할 내용을 한 줄로 입력하세요...",
        label_visibility="collapsed"
    )
    submit_button = st.form_submit_button(label="제출하기")

# 제출 버튼이 눌렸을 때 처리
if submit_button:
    if user_input.strip():
        try:
            # Supabase 'suggestions' 테이블에 데이터 삽입
            # id, created_at은 Supabase에서 자동 생성되므로 content, category, likes만 전송
            response = supabase.table("suggestions").insert({
                "content": user_input.strip(),
                "category": category,
                "likes": 0
            }).execute()
            
            st.toast("건의사항이 Supabase에 안전하게 등록되었습니다!", icon="✅")
            st.rerun()  # 화면을 새로고침하여 최신 목록 즉시 반영
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {e}")
    else:
        st.error("내용을 입력해 주세요.")

st.divider()

# 등록된 건의사항 목록 출력 (최신순)
st.subheader("📋 등록된 건의사항")

try:
    # created_at 기준 내림차순(최신순)으로 데이터 조회
    response = supabase.table("suggestions").select("*").order("created_at", desc=True).execute()
    suggestions = response.data

    if not suggestions:
        st.info("아직 등록된 건의사항이 없습니다. 첫 건의를 남겨보세요!")
    else:
        for item in suggestions:
            cat = item.get("category", "일반")
            content = item.get("content", "")
            # 날짜 형식 다듬기 (YYYY-MM-DD HH:MM 형태 중 앞부분 추출)
            created_at = item.get("created_at", "")[:19].replace("T", " ")
            
            with st.container(border=True):
                st.markdown(f"**[{cat}]** {content}")
                st.caption(f"등록일: {created_at}")
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")