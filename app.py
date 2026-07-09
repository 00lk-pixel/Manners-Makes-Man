# -*- coding: utf-8 -*-
"""
MMM — Makeup maketh man (1페이지: 헤더 + 감성 스플래시)

Streamlit Cloud는 Streamlit 스크립트만 서빙할 수 있어서(순수 Flask/정적 서버 불가),
직접 만든 for_him_prototype.html(헤더 + 스플래시)을 수정 없이 그대로 iframe에
로드해서 원본과 동일한 화면/동작을 보여준다. 오렌지 히어로/사이트 인덱스/갤러리/CTA/
푸터는 아직 이 화면에 없다 — 다음 단계에서 순서대로 이어붙일 예정.

실행: pip install -r requirements.txt && streamlit run app.py
"""

import datetime
import html as html_lib
import json
import pathlib
import re

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MMM — Makeup maketh man", page_icon="💄", layout="wide")

# 아직 Google Cloud Console에서 발급받은 OAuth 클라이언트 ID/시크릿이 없어서,
# secrets.toml에 [auth]가 없을 때는 진짜 st.login() 대신 세션 상태로 로그인
# 상태만 흉내 내는 목업 경로를 쓴다. 나중에 실제 자격증명을 secrets에 넣으면
# 자동으로 진짜 구글 로그인(real=True 경로)으로 전환된다.
AUTH_CONFIGURED = "auth" in st.secrets
st.session_state.setdefault("mock_logged_in", False)
st.session_state.setdefault("signed_up_user", None)

# 이메일/비밀번호 가입자 명단 - 지금은 실제 DB가 없어서 가벼운 JSON 파일로 대체
# (Streamlit Cloud가 재배포/재시작되면 파일이 초기화될 수 있는 데모 수준 저장소).
# 비밀번호는 폼에서부터 여기로 아예 전달되지 않으므로 저장되지 않는다.
SIGNUPS_PATH = pathlib.Path(__file__).parent / "data" / "signups.json"


def save_signup(name, email):
    SIGNUPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        records = json.loads(SIGNUPS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    records.append({
        "name": name,
        "email": email,
        "signed_up_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    SIGNUPS_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


# 스플래시 안의 "Sign up with Google" 링크와 이메일 가입 폼은 iframe 안에 있어서,
# 둘 다 target="_top"으로 최상단 페이지를 ?login=google 또는 ?signup=1&name=...&email=...
# 로 이동시킨다. 그걸 여기서 감지해서 처리한다 - 실제 저장/구글 인증 콜백이
# iframe이 아니라 이 Streamlit 앱 자체 URL에서 일어나야 하기 때문.
if st.query_params.get("login") == "google":
    st.query_params.clear()
    if AUTH_CONFIGURED:
        if not st.user.is_logged_in:
            st.login()
    else:
        st.session_state["mock_logged_in"] = True
        st.rerun()

if st.query_params.get("signup") == "1":
    name = st.query_params.get("name", "").strip() or "회원"
    email = st.query_params.get("email", "").strip()
    st.query_params.clear()
    if email:
        save_signup(name, email)
    st.session_state["signed_up_user"] = {"name": name, "email": email}
    st.rerun()

if st.query_params.get("logout") == "1":
    st.query_params.clear()
    if AUTH_CONFIGURED and st.user.is_logged_in:
        st.logout()
    st.session_state["mock_logged_in"] = False
    st.session_state["signed_up_user"] = None
    st.rerun()

# Streamlit의 기본 크롬(햄버거 메뉴/헤더/푸터)과 block-container 여백을 지워서
# iframe 콘텐츠가 액자 없이 화면을 그대로 채우는 것처럼 보이게 한다.
st.markdown("""
<style>
#MainMenu, header, footer { visibility: hidden; height: 0; }
.block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
iframe { display: block; }
</style>
""", unsafe_allow_html=True)

HTML_PATH = pathlib.Path(__file__).parent / "for_him_prototype.html"
html = HTML_PATH.read_text(encoding="utf-8")

signed_up_user = st.session_state["signed_up_user"]
logged_in = (AUTH_CONFIGURED and st.user.is_logged_in) or st.session_state["mock_logged_in"] or bool(signed_up_user)
if logged_in:
    if AUTH_CONFIGURED and st.user.is_logged_in:
        name, email = st.user.name, st.user.email
    elif signed_up_user:
        name, email = signed_up_user["name"], signed_up_user["email"]
    else:
        name, email = "테스트 사용자", "google 연동 준비 중 (목업 로그인)"
    welcome_block = f"""
    <div class="splash-welcome">
      <p>{html_lib.escape(name)}님, 환영합니다 👋<br>{html_lib.escape(email)}</p>
      <a href="?logout=1" target="_top">로그아웃</a>
    </div>
    """
    html = re.sub(
        r"<!--AUTH_BLOCK_START-->.*?<!--AUTH_BLOCK_END-->",
        welcome_block,
        html,
        flags=re.DOTALL,
    )

components.html(html, height=880, scrolling=False)
