import streamlit as st
import requests
import uuid

st.set_page_config(
    page_title="🎵 Music Search System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000/api"

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

def search_songs(query: str, search_type: str, limit: int = 10):
    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={
                "query": query,
                "search_type": search_type,
                "limit": limit,
                "user_id": st.session_state.user_id
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"검색 오류: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API 연결 오류: {e}")
        return None

def get_recommendations(song_id: str, rec_type: str = "genre", limit: int = 5):
    try:
        response = requests.get(
            f"{API_BASE_URL}/recommendations/{song_id}",
            params={"rec_type": rec_type, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"추천 API 오류: {e}")
        return []

def display_song_card(song, show_recommendations=True):
    with st.expander(f"🎵 {song['title']} - {song.get('artist_name', '알 수 없음')}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎶 곡 정보**")
            st.write(f"ID: `{song.get('song_id', 'N/A')}`")
            st.write(f"제목: **{song.get('title', 'N/A')}**")
            st.write(f"발매일: {song.get('issue_date', 'N/A')}")
        with col2:
            st.markdown("**🎤 아티스트 & 장르**")
            st.write(f"아티스트: **{song.get('artist_name', 'N/A')}**")
            st.write(f"장르: {song.get('genre_name', 'N/A')}")
            if song.get('subgenre_name'):
                st.write(f"서브장르: {song.get('subgenre_name')}")
        with col3:
            st.markdown("**💿 앨범 정보**")
            if song.get('album_title'):
                st.write(f"앨범: **{song.get('album_title')}**")
                if song.get('album_id'):
                    st.write(f"앨범 ID: {song.get('album_id')}")
            else:
                st.write("앨범 정보 없음")
        if show_recommendations and song.get('song_id'):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🎭 같은 장르 추천", key=f"genre_{song['song_id']}"):
                    recommendations = get_recommendations(song['song_id'], "genre")
                    if recommendations:
                        st.write("**같은 장르의 다른 노래:**")
                        for rec in recommendations:
                            display_song_card(rec, show_recommendations=False)
            with col2:
                if st.button(f"👨‍🎤 같은 아티스트", key=f"artist_{song['song_id']}"):
                    recommendations = get_recommendations(song['song_id'], "artist")
                    if recommendations:
                        st.write("**같은 아티스트의 다른 노래:**")
                        for rec in recommendations:
                            display_song_card(rec, show_recommendations=False)

# 페이지 타이틀 및 설명
st.title("🎵 AI 음악 검색 시스템")
st.markdown("**Neo4j + LangChain + OpenAI 기반 지능형 음악 검색 시스템**")

# 사이드바: API 서버 및 데이터베이스 상태 확인, 사용자 정보 표시
with st.sidebar:
    st.header("🛠️ 시스템 상태")
    try:
        health_response = requests.get(f"{API_BASE_URL.replace('/api', '')}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            if health_data["status"] == "healthy":
                st.success("✅ API 서버 연결됨")
                st.success(f"✅ 데이터베이스: {health_data['database']}")
            else:
                st.error("❌ 데이터베이스 연결 안됨")
        else:
            st.error("❌ API 서버 연결 안됨")
    except:
        st.error("❌ API 서버에 연결할 수 없음")

    st.markdown("---")
    st.write(f"**사용자 ID:** `{st.session_state.user_id[:8]}...`")

# 검색 UI
st.header("🔍 음악 검색")
search_method = st.radio(
    "검색 방법 선택",
    ["🎵 곡 제목 검색", "👨‍🎤 아티스트 검색", "🤖 자연어 RAG 검색"],
    horizontal=True
)
query = st.text_input("검색어를 입력하세요:")
limit = st.slider("결과 개수", 5, 50, 10)

if st.button("🔍 검색 실행", type="primary"):
    if query:
        if "곡 제목" in search_method:
            search_type = "title"
        elif "아티스트" in search_method:
            search_type = "artist"
        else:
            search_type = "rag"

        with st.spinner("검색 중..."):
            results = search_songs(query, search_type, limit)
            if results and results.get('songs'):
                st.success(f"🎉 {results['total_count']}개의 결과를 찾았습니다! (실행시간: {results['execution_time']:.2f}초)")
                for song in results['songs']:
                    display_song_card(song)
            else:
                st.warning("검색 결과가 없습니다.")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🎵 AI Music Search System v1.0 | Powered by Neo4j + LangChain + OpenAI</p>
    </div>
    """,
    unsafe_allow_html=True
)
