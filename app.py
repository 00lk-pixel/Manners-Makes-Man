# -*- coding: utf-8 -*-
"""
MMM — Makeup maketh man (1페이지: 헤더 + 감성 스플래시 → 가입/로그인 → 프로필 설정)

Streamlit Cloud는 Streamlit 스크립트만 서빙할 수 있어서(순수 Flask/정적 서버 불가),
직접 만든 for_him_prototype.html(헤더 + 스플래시 + 가입 화면 + 프로필 설정 화면)을
수정 없이 그대로 iframe에 로드해서 원본과 동일한 화면/동작을 보여준다.

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
MOCK_GOOGLE_EMAIL = "mock-google-user@local"
st.session_state.setdefault("mock_logged_in", False)
st.session_state.setdefault("signed_up_user", None)

# 가입/로그인/프로필 정보를 담는 사용자 명단 - 지금은 실제 DB가 없어서 가벼운
# JSON 파일로 대체한다 (Streamlit Cloud가 재배포/재시작되면 파일이 초기화될 수
# 있는 데모 수준 저장소). 이메일을 키로 삼아 한 사람당 한 레코드만 유지하고,
# 로그인 정보(name/email)와 나중에 저장되는 프로필 정보가 같은 레코드에 합쳐진다.
# 비밀번호는 폼에서부터 여기로 아예 전달되지 않으므로 저장되지 않는다.
USERS_PATH = pathlib.Path(__file__).parent / "data" / "signups.json"


def load_users():
    try:
        return json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def upsert_user(email, **fields):
    if not email:
        return
    users = load_users()
    for user in users:
        if user.get("email") == email:
            user.update(fields)
            break
    else:
        fields.setdefault("signed_up_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
        users.append({"email": email, **fields})
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USERS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def current_user():
    """지금 로그인/가입된 사용자를 (name, email)로 반환. 없으면 None."""
    if AUTH_CONFIGURED and st.user.is_logged_in:
        return st.user.name, st.user.email
    if st.session_state["mock_logged_in"]:
        return "테스트 사용자", MOCK_GOOGLE_EMAIL
    signed_up_user = st.session_state["signed_up_user"]
    if signed_up_user:
        return signed_up_user["name"], signed_up_user["email"]
    return None


def profile_completed():
    """현재 사용자가 프로필 입력까지 마쳤는지. 서비스 흐름이
    '메인(스플래시) → 가입 → 프로필 입력 → 나머지 화면(큐레이션 등)'이라서,
    나머지 화면으로 가는 네비게이션은 이게 True일 때만 노출한다."""
    user = current_user()
    if not user:
        return False
    email = user[1]
    return any(u.get("email") == email and u.get("profile") for u in load_users())


# 스플래시의 "Sign up with Google" 링크, 이메일 가입 폼, 프로필 저장 버튼은 모두
# iframe 안에 있어서 직접 최상단 페이지를 못 옮긴다 (아래 st.markdown으로 심는
# postMessage 브리지가 대신 ?login=google / ?signup=1&fullname=...&email=... /
# ?profile_save=1&profile=... 로 이동시킨다). 그걸 여기서 감지해서 처리한다 - 실제
# 저장/구글 인증 콜백이 iframe이 아니라 이 Streamlit 앱 자체 URL에서 일어나야 하기 때문.
if st.query_params.get("login") == "google":
    st.query_params.clear()
    if AUTH_CONFIGURED:
        if not st.user.is_logged_in:
            st.login()
    else:
        st.session_state["mock_logged_in"] = True
        upsert_user(MOCK_GOOGLE_EMAIL, name="테스트 사용자")
        st.rerun()

if st.query_params.get("signup") == "1":
    name = st.query_params.get("fullname", "").strip() or "회원"
    email = st.query_params.get("email", "").strip()
    st.query_params.clear()
    if email:
        upsert_user(email, name=name)
    st.session_state["signed_up_user"] = {"name": name, "email": email}
    # 가입 완료 → 곧바로 홈 화면의 프로필 설정 화면으로 이어지게 한다.
    st.query_params["page"] = "home"
    st.query_params["screen"] = "profile-screen"
    st.rerun()

if st.query_params.get("profile_save") == "1":
    profile_raw = st.query_params.get("profile", "")
    st.query_params.clear()
    try:
        profile = json.loads(profile_raw)
    except (ValueError, TypeError):
        profile = {}
    user = current_user()
    if user:
        upsert_user(user[1], profile=profile)
    # 프로필 입력 완료 → 이때부터 나머지 화면이 열리고, 첫 화면으로 큐레이션을 보여준다.
    st.query_params["page"] = "curation"
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
.mmm-nav { display: flex; gap: 22px; align-items: center; padding: 12px 28px; background: #111; }
.mmm-nav a { color: #999; text-decoration: none; font-size: 13px; letter-spacing: 0.12em; }
.mmm-nav a:hover { color: #fff; }
.mmm-nav a.is-active { color: #fff; font-weight: 700; border-bottom: 2px solid #fff; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# 팀원별 화면을 ?page= 쿼리 파라미터로 골라 iframe에 로드한다 (상단 네비게이션으로 전환).
# FAWN이 프로토타입을 로그인 화면(for_him_prototype.html)과 홈 화면(home_prototype.html,
# 히어로/갤러리/가입/프로필)으로 분리했고, KITTY 화면 3종과 목업 페이지도 여기 매핑된다.
PAGES = {
    "login": ("LOGIN", "for_him_prototype.html"),
    "home": ("HOME", "home_prototype.html"),
    "mockup": ("MOCKUP", "mockup.html"),
    "profile": ("PROFILE", "profile.html"),
    "curation": ("STYLING", "curation.html"),
    "groom": ("GROOM AI", "groom_ai.html"),
}
page_key = st.query_params.get("page", "login")
if page_key not in PAGES:
    page_key = "login"


def load_html(name):
    return (pathlib.Path(__file__).parent / name).read_text(encoding="utf-8")


# 로그인 화면의 링크들은 home_prototype.html#... 상대 경로로 이동하는데, components.html
# iframe(srcdoc)은 상대 경로 파일을 서빙하지 못해 클릭이 전부 깨진다. 그래서 서빙 시점에
# 그 링크들을 postMessage(goto_home)로 바꿔치기하고, 최상단 브리지가 ?page=home&screen=...
# 으로 변환해 Streamlit이 홈 화면을 해당 위치로 열게 한다. notifyParent는 홈 파일에만
# 있어서 로그인 화면에는 mmmNotify/gotoHome 헬퍼를 직접 주입한다.
GOTO_HOME_SCRIPT = """
<script>
  function mmmNotify(payload) {
    try { window.top.postMessage(Object.assign({ __mmm: true }, payload), '*'); } catch (err) {}
  }
  function gotoHome(hash) { mmmNotify({ type: 'goto_home', hash: hash }); }
</script>
"""


def build_login_html():
    html = load_html("for_him_prototype.html")
    html = html.replace("</head>", GOTO_HOME_SCRIPT + "</head>", 1)
    html = re.sub(
        r'href="home_prototype\.html#([A-Za-z0-9_-]+)"',
        lambda m: 'href="#" onclick="event.preventDefault(); gotoHome(\'%s\')"' % m.group(1),
        html,
    )
    html = html.replace(
        "window.location.href='home_prototype.html#signup-screen'",
        "gotoHome('signup-screen')",
    )
    return html


if page_key == "login":
    html = build_login_html()
else:
    html = load_html(PAGES[page_key][1])

# 로그인 화면에서 넘어올 때 홈의 어떤 화면(가입/프로필) 또는 앵커(#hero 등)를 열지
# ?screen=으로 전달받는다. 홈 파일 자체의 location.hash 부트스트랩은 srcdoc iframe에선
# 해시가 없어 동작하지 않으므로 같은 일을 하는 스크립트를 주입한다.
if page_key == "home":
    screen = st.query_params.get("screen", "")
    if re.fullmatch(r"[A-Za-z0-9_-]+", screen or ""):
        bootstrap = """
<script>
  document.addEventListener('DOMContentLoaded', function () {
    var screen = '%s';
    if (screen === 'signup-screen') { showSignup(); }
    else if (screen === 'profile-screen') { showProfileScreen(); }
    else { var el = document.getElementById(screen); if (el) el.scrollIntoView(); }
  });
</script>
""" % screen
        html = html.replace("</body>", bootstrap + "</body>", 1)

# FAWN의 mockup.html은 <iframe src="for_him_prototype.html">로 로그인 화면을 불러오는데,
# srcdoc iframe 안에서는 상대 경로가 서빙되지 않아 빈 화면이 된다. 링크가 postMessage로
# 재작성된 로그인 HTML을 srcdoc으로 인라인해서 목업 안에서도 실제 화면이 동작하게 한다.
if page_key == "mockup":
    html = html.replace(
        '<iframe src="for_him_prototype.html" title="MMM prototype preview"></iframe>',
        '<iframe srcdoc="%s" title="MMM prototype preview"></iframe>' % html_lib.escape(build_login_html()),
    )

user = current_user()
if user and page_key == "login":
    name, email = user
    # 스플래시의 가입/로그인 버튼 자리에 환영 문구 + 프로필/로그아웃 링크를 넣는다.
    # (프로필 화면이 home_prototype.html로 분리되어 예전처럼 같은 문서 안에서
    # showProfileScreen()을 바로 부를 수 없고, gotoHome으로 홈 화면을 연다.)
    auth_block = f"""
    <div class="splash-welcome">
      <p>{html_lib.escape(name)}님, 환영합니다 👋<br>{html_lib.escape(email)}</p>
      <a href="#" onclick="event.preventDefault(); gotoHome('profile-screen');">프로필 설정</a> ·
      <a href="#" onclick="event.preventDefault(); mmmNotify({{type:'logout'}});">로그아웃</a>
    </div>
    """
    html = re.sub(
        r"<!--AUTH_BLOCK_START-->.*?<!--AUTH_BLOCK_END-->",
        auth_block,
        html,
        flags=re.DOTALL,
    )

# Streamlit의 components.html iframe은 sandbox에 allow-top-navigation이 빠져 있어서
# 그 iframe 안에서 target="_top"으로 최상단 페이지를 이동시키는 시도(폼 제출/앵커 클릭
# 모두)가 브라우저에 의해 조용히 막힌다. 그래서 iframe 쪽(for_him_prototype.html)은
# window.top.postMessage(...)로 "이런 일이 있었다"는 사실만 알리고, 실제 이동은 여기
# 최상단 페이지 자신의 스크립트가 대신 수행한다 (자기 자신을 이동시키는 건 sandbox와
# 무관하게 항상 허용됨). st.markdown(unsafe_allow_html=True)는 <script> 태그를 실제로는
# 실행하지 않으므로(React가 raw HTML을 엘리먼트 트리로 변환해서 렌더링하기 때문),
# st.html(..., unsafe_allow_javascript=True)를 대신 쓴다 - 이건 iframe 없이 최상단
# 페이지 자신의 컨텍스트에서 그대로 실행된다.
st.html(
    """
    <script>
      (function(){
        if (window.__mmmBridgeInstalled) return;
        window.__mmmBridgeInstalled = true;
        window.addEventListener('message', function(event) {
          var data = event.data;
          if (!data || data.__mmm !== true || !data.type) return;
          var params = new URLSearchParams(window.location.search);
          if (data.type === 'login_google') {
            params.set('login', 'google');
          } else if (data.type === 'signup') {
            params.set('signup', '1');
            params.set('fullname', data.fullname || '');
            params.set('email', data.email || '');
          } else if (data.type === 'profile_save') {
            params.set('profile_save', '1');
            params.set('profile', JSON.stringify(data.profile || {}));
          } else if (data.type === 'logout') {
            params.set('logout', '1');
          } else if (data.type === 'goto_home') {
            params.set('page', 'home');
            params.set('screen', data.hash || '');
          } else {
            return;
          }
          window.location.search = params.toString();
        });
      })();

      // components.html은 항상 고정 height의 iframe이라, 화면(스플래시/가입/프로필)마다
      // 실제 콘텐츠 길이가 달라도 그 고정 높이를 넘는 부분은 잘려 보인다. 그래서 iframe
      // 안쪽 문서의 실제 콘텐츠 높이를 재서 iframe 자신의 높이를 맞춰준다 - 그러면 내부
      // 스크롤 없이도 항상 전체 내용이 보이고, 화면이 길어지면 브라우저의 진짜 페이지
      // 스크롤로 이어서 볼 수 있다. sandbox에 allow-same-origin이 있어서 iframe.contentDocument
      // 접근이 막히지 않는다.
      (function(){
        if (window.__mmmAutoHeightInstalled) return;
        window.__mmmAutoHeightInstalled = true;
        var attachedDoc = null;
        var observer = null;
        function sync(doc, iframe) {
          var root = doc.documentElement;
          var h = Math.max(root.scrollHeight, doc.body ? doc.body.scrollHeight : 0);
          if (h > 0) iframe.style.height = h + 'px';
        }
        function tick() {
          var iframe = document.querySelector('iframe');
          if (!iframe) return;
          var doc;
          try { doc = iframe.contentDocument; } catch (err) { return; }
          if (!doc || !doc.documentElement) return;
          if (doc !== attachedDoc) {
            attachedDoc = doc;
            if (observer) observer.disconnect();
            observer = new ResizeObserver(function () { sync(doc, iframe); });
            observer.observe(doc.documentElement);
          }
          sync(doc, iframe);
        }
        setInterval(tick, 300);
      })();
    </script>
    """,
    unsafe_allow_javascript=True,
)

# 상단 네비게이션 - 링크는 iframe 밖(최상단 페이지)에서 렌더링되므로 sandbox 제약
# 없이 ?page= 쿼리 파라미터로 바로 이동해서 Streamlit이 해당 화면을 다시 그린다.
# 서비스 흐름상 프로필 입력을 마치기 전에는 메인(스플래시)만 보여야 해서,
# 네비게이션은 프로필 완료 후에만 노출한다.
if profile_completed():
    nav_links = "".join(
        '<a href="?page={key}" target="_self"{cls}>{label}</a>'.format(
            key=key,
            cls=' class="is-active"' if key == page_key else "",
            label=label,
        )
        for key, (label, _) in PAGES.items()
    )
    st.markdown(f'<nav class="mmm-nav">{nav_links}</nav>', unsafe_allow_html=True)

components.html(html, height=880, scrolling=True)
