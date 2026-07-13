# -*- coding: utf-8 -*-
"""
MMM 단일 HTML 빌더 — Streamlit 앱(app.py)이 서빙하던 5개 화면을 서버 없이
더블클릭으로 열 수 있는 단일 파일(MMM_standalone.html)로 합친다.

실행: python build_standalone.py

app.py가 하던 일을 그대로 클라이언트 JS로 옮긴다:
- 상단 네비게이션(?page= 전환) → 래퍼 페이지의 nav + srcdoc iframe 교체
- postMessage 브리지(가입/구글목업로그인/프로필저장/로그아웃/화면이동) → 래퍼 리스너
- data/signups.json 저장 → localStorage('mmm_signups')
- iframe 자동 높이 스크립트 → 그대로 복사
화면 파일들은 폰트/영상까지 전부 base64 인라인이라 외부 파일 의존이 없다.
(groom_ai.html이 71MB라 결과물은 약 80MB — git에는 커밋하지 않는 걸 권장)
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "MMM_standalone.html"

PAGES = [
    ("login", "LOGIN", "for_him_prototype.html"),
    ("home", "HOME", "home_prototype.html"),
    ("profile", "PROFILE", "profile.html"),
    ("curation", "STYLING", "curation.html"),
    ("groom", "GROOM AI", "groom_ai.html"),
]

# 모든 화면에 주입하는 헬퍼 — 화면 간 이동을 부모(래퍼)에게 알린다.
HELPER_SCRIPT = (
    "<script>function mmmGoto(page, search){try{window.parent.postMessage("
    "{__mmm:true,type:'goto_page',page:page,search:search||''},'*');}catch(e){}}</script>"
)

# app.py의 GOTO_HOME_SCRIPT와 동일 (로그인 화면 전용 헬퍼)
GOTO_HOME_SCRIPT = """
<script>
  function mmmNotify(payload) {
    try { window.parent.postMessage(Object.assign({ __mmm: true }, payload), '*'); } catch (err) {}
  }
  function gotoHome(hash) { mmmNotify({ type: 'goto_home', hash: hash }); }
</script>
"""


def load_page(name):
    html = (ROOT / name).read_text(encoding="utf-8")
    # app.py load_html과 동일 — 브리지 리스너는 부모(래퍼)에 있다.
    html = html.replace("window.top.postMessage(", "window.parent.postMessage(")
    html = html.replace("</head>", HELPER_SCRIPT + "</head>", 1)
    # srcdoc iframe은 location.search가 비어 있으므로 래퍼가 주입하는
    # window.__MMM_SEARCH를 대신 읽게 한다 (groom_ai ?cat=&sub=, curation/profile ?reset=1).
    html = html.replace(
        "new URLSearchParams(window.location.search)",
        "new URLSearchParams(window.__MMM_SEARCH || window.location.search)",
    )
    return html


def build_login():
    # app.py build_login_html과 동일한 변환
    html = load_page("for_him_prototype.html")
    html = html.replace("</head>", GOTO_HOME_SCRIPT + "</head>", 1)
    html = re.sub(
        r'href="home_prototype\.html#([A-Za-z0-9_-]+)"',
        lambda m: 'href="#" onclick="event.preventDefault(); gotoHome(\'%s\')"' % m.group(1),
        html,
    )
    html = html.replace(
        "window.location.href='profile%203.html'".replace("%20", " "),
        "mmmNotify({ type: 'goto_page', page: 'profile' })",
    )
    html = re.sub(
        r"window\.location\.href='home_prototype\.html#([A-Za-z0-9_-]+)'",
        lambda m: "gotoHome('%s')" % m.group(1),
        html,
    )
    return html


def build_home():
    html = load_page("home_prototype.html")
    # 사이트 인덱스의 파일 직링크들을 래퍼 페이지 전환으로 교체
    html = html.replace(
        'href="profile.html"',
        'href="#" onclick="event.preventDefault(); mmmGoto(\'profile\')"',
    )
    html = html.replace(
        'href="groom_ai.html"',
        'href="#" onclick="event.preventDefault(); mmmGoto(\'groom\')"',
    )
    html = html.replace(
        'href="curation.html?reset=1"',
        'href="#" onclick="event.preventDefault(); mmmGoto(\'curation\', \'?reset=1\')"',
    )
    return html


def build_curation():
    html = load_page("curation.html")
    html = html.replace(
        "window.location.href = 'groom_ai.html?cat=' + encodeURIComponent(match.cat) + '&sub=' + encodeURIComponent(match.sub);",
        "mmmGoto('groom', '?cat=' + encodeURIComponent(match.cat) + '&sub=' + encodeURIComponent(match.sub));",
    )
    html = html.replace(
        "window.location.href = 'groom_ai.html';",
        "mmmGoto('groom');",
    )
    return html


def build_groom():
    html = load_page("groom_ai.html")
    html = html.replace(
        'href="curation.html"',
        'href="#" onclick="event.preventDefault(); mmmGoto(\'curation\')"',
    )
    return html


def js_string(s):
    # JS 문자열 리터럴로 안전하게. HTML 파서가 래퍼의 <script> 블록을 조기 종료하거나
    # escaped/double-escaped 상태로 빠지지 않도록 </, <!--, <script 를 모두 백슬래시로
    # 끊는다 (JS 문자열에서 \/, \!, \s 는 각각 /, !, s 와 동일하므로 의미 불변).
    out = json.dumps(s, ensure_ascii=False)
    out = out.replace("</", "<\\/")
    out = re.sub(r"(?i)<(!--|script)", lambda m: "<\\" + m.group(1), out)
    return out


BUILDERS = {
    "login": build_login,
    "home": build_home,
    "profile": lambda: load_page("profile.html"),
    "curation": build_curation,
    "groom": build_groom,
}

TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MMM — Makeup maketh man</title>
<style>
  html, body { margin: 0; padding: 0; background: #111; }
  /* 초기 높이가 없으면 100vh 레이아웃이 150px로 찌그러진다 (app.py는 height=880을 줬음) */
  iframe { display: block; width: 100%; border: 0; min-height: calc(100vh - 45px); }
  .mmm-nav { display: flex; gap: 22px; align-items: center; padding: 12px 28px; background: #111;
             position: sticky; top: 0; z-index: 100; }
  .mmm-nav a { color: #999; text-decoration: none; font-size: 13px; letter-spacing: 0.12em;
               font-family: system-ui, sans-serif; cursor: pointer; }
  .mmm-nav a:hover { color: #fff; }
  .mmm-nav a.is-active { color: #fff; font-weight: 700; border-bottom: 2px solid #fff; padding-bottom: 2px; }
</style>
</head>
<body>
<nav class="mmm-nav" id="mmmNav"></nav>
<iframe id="mmmFrame" title="MMM"></iframe>
<script>
/* ===== 화면 원본 (빌드 시 주입) ===== */
var PAGES = {
  login:    { label: 'LOGIN',    html: __PAYLOAD_login__ },
  home:     { label: 'HOME',     html: __PAYLOAD_home__ },
  profile:  { label: 'PROFILE',  html: __PAYLOAD_profile__ },
  curation: { label: 'STYLING',  html: __PAYLOAD_curation__ },
  groom:    { label: 'GROOM AI', html: __PAYLOAD_groom__ }
};

/* ===== 사용자 명단 — app.py의 data/signups.json을 localStorage로 대체 ===== */
var SIGNUPS_KEY = 'mmm_signups';
var SESSION_KEY = 'mmm_session_user';
function loadUsers() {
  try { return JSON.parse(localStorage.getItem(SIGNUPS_KEY) || '[]'); } catch (e) { return []; }
}
function upsertUser(email, fields) {
  if (!email) return;
  var users = loadUsers();
  var found = users.find(function (u) { return u.email === email; });
  if (found) { Object.assign(found, fields); }
  else {
    users.push(Object.assign({ email: email, signed_up_at: new Date().toISOString() }, fields));
  }
  try { localStorage.setItem(SIGNUPS_KEY, JSON.stringify(users)); } catch (e) {}
}
function currentUser() {
  try { return JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null'); } catch (e) { return null; }
}
function setCurrentUser(user) {
  try {
    if (user) sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));
    else sessionStorage.removeItem(SESSION_KEY);
  } catch (e) {}
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}

/* ===== 화면 렌더링 — app.py가 서빙 시점에 하던 주입을 여기서 수행 ===== */
var currentPage = 'login';
function render(pageKey, opts) {
  opts = opts || {};
  if (!PAGES[pageKey]) pageKey = 'login';
  currentPage = pageKey;
  var html = PAGES[pageKey].html;

  if (opts.search) {
    html = html.replace('<head>', '<head><script>window.__MMM_SEARCH=' +
      JSON.stringify(opts.search) + ';<' + '/script>');
  }
  // 홈: 로그인 화면에서 넘어올 때 열 화면/앵커 (app.py의 bootstrap 주입과 동일)
  if (pageKey === 'home' && opts.screen && /^[A-Za-z0-9_-]+$/.test(opts.screen)) {
    var bootstrap = '<script>document.addEventListener("DOMContentLoaded", function () {' +
      'var screen = ' + JSON.stringify(opts.screen) + ';' +
      'if (screen === "signup-screen") { showSignup(); }' +
      'else if (screen === "profile-screen") { showProfileScreen(); }' +
      'else { var el = document.getElementById(screen); if (el) el.scrollIntoView(); }' +
      '});<' + '/script>';
    // home_prototype.html은 </body> 닫는 태그가 없어서 replace가 무시된다 — 끝에 덧붙인다.
    if (html.indexOf('</body>') !== -1) html = html.replace('</body>', bootstrap + '</body>');
    else html += bootstrap;
  }
  // 로그인: 로그인된 상태면 가입/로그인 버튼 자리에 환영 문구 (app.py auth_block과 동일)
  var user = currentUser();
  if (pageKey === 'login' && user) {
    var block = '<div class="splash-welcome">' +
      '<p>' + escapeHtml(user.name) + '님, 환영합니다 \\uD83D\\uDC4B<br>' + escapeHtml(user.email) + '</p>' +
      '<a href="#" onclick="event.preventDefault(); gotoHome(\\'profile-screen\\');">프로필 설정</a> · ' +
      '<a href="#" onclick="event.preventDefault(); mmmNotify({type:\\'logout\\'});">로그아웃</a>' +
      '</div>';
    html = html.replace(/<!--AUTH_BLOCK_START-->[\\s\\S]*?<!--AUTH_BLOCK_END-->/, block);
  }

  document.getElementById('mmmFrame').srcdoc = html;
  renderNav();
  window.scrollTo(0, 0);
}
function renderNav() {
  var nav = document.getElementById('mmmNav');
  nav.innerHTML = '';
  Object.keys(PAGES).forEach(function (key) {
    var a = document.createElement('a');
    a.textContent = PAGES[key].label;
    if (key === currentPage) a.className = 'is-active';
    a.addEventListener('click', function (e) { e.preventDefault(); render(key); });
    nav.appendChild(a);
  });
}

/* ===== postMessage 브리지 — app.py의 쿼리 파라미터 처리와 동일한 분기 ===== */
window.addEventListener('message', function (event) {
  var data = event.data;
  if (!data || data.__mmm !== true || !data.type) return;
  if (data.type === 'login_google') {
    // 실제 OAuth 자격증명이 없을 때의 목업 경로 (app.py와 동일)
    upsertUser('mock-google-user@local', { name: '테스트 사용자' });
    setCurrentUser({ name: '테스트 사용자', email: 'mock-google-user@local' });
    render('login');
  } else if (data.type === 'signup') {
    var name = (data.fullname || '').trim() || '회원';
    var email = (data.email || '').trim();
    if (email) upsertUser(email, { name: name });
    setCurrentUser({ name: name, email: email });
    render('home', { screen: 'profile-screen' });
  } else if (data.type === 'profile_save') {
    var u = currentUser();
    if (u) upsertUser(u.email, { profile: data.profile || {} });
  } else if (data.type === 'logout') {
    setCurrentUser(null);
    render('login');
  } else if (data.type === 'goto_home') {
    render('home', { screen: data.hash || '' });
  } else if (data.type === 'goto_page') {
    render(data.page || 'login', { search: data.search || '' });
  } else if (data.type === 'guest_login') {
    render('profile');
  }
});

/* ===== iframe 자동 높이 — app.py의 스크립트 그대로 ===== */
(function () {
  var attachedDoc = null;
  var observer = null;
  function sync(doc, iframe) {
    var root = doc.documentElement;
    var h = Math.max(root.scrollHeight, doc.body ? doc.body.scrollHeight : 0);
    if (h > 0) iframe.style.height = h + 'px';
  }
  function tick() {
    var iframe = document.getElementById('mmmFrame');
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

render('login');
</script>
</body>
</html>
"""


def main():
    out = TEMPLATE
    for key, _label, _file in PAGES:
        payload = js_string(BUILDERS[key]())
        out = out.replace("__PAYLOAD_%s__" % key, payload)
    OUT.write_text(out, encoding="utf-8")
    print("OK: %s (%.1f MB)" % (OUT.name, OUT.stat().st_size / 1024 / 1024))


if __name__ == "__main__":
    main()
