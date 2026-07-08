# -*- coding: utf-8 -*-
"""
남성 그루밍/뷰티 초보자를 위한 '목적별 제품 추천 + 카드 스와이프' 프로토타입
기획서(코스맥스 GCC R&I팀) 기반 구현 - 단일 파일(app.py) 버전

Function 1. 개인 정보 데이터베이스화
Function 2. 목적별 메이크업 및 제품 추천 시스템 (데일리 / 이벤트 / 데이트)
Function 3. 프로필 설정 (나이대 / 피부타입·고민 태그 / 가격대)
Function 4. 제품 카드 스와이프 UI

실행: pip install -r requirements.txt && python app.py
접속: http://localhost:5000
"""

from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import uuid

app = Flask(__name__)
app.secret_key = "mencare-prototype-secret-key"

# =========================================================================
# Function 1: 개인 정보 데이터베이스 (실제 서비스에서는 DB, 프로토타입은 in-memory)
# =========================================================================
USERS = {}  # session_id -> profile dict


def get_or_create_profile():
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())
    uid = session["uid"]
    if uid not in USERS:
        USERS[uid] = {
            "age_group": None,       # 10대 / 20대 / 30대 / 40대 이상
            "skin_type": None,       # 지성 / 건조함 / 복합성 / 민감성
            "concerns": [],          # 걱정거리 태그 리스트
            "price_min": 10000,
            "price_max": 30000,
            "history": [],           # (mode, product_id, action) 로그 - 동적 태깅용
        }
    return USERS[uid]


# =========================================================================
# Function 2: 목적별 모드 정의 (기획서 표 그대로 반영)
# =========================================================================
MODES = {
    "daily": {
        "label": "데일리",
        "subtitle": "충전 · 방전용, 최소한의 케어",
        "intensity": "최소 (1~2단계)",
        "guide": "선크림 + 톤업크림 정도, \"티 안 나게\" 초점, 소요시간 3분 이내",
    },
    "event": {
        "label": "이벤트",
        "subtitle": "소개팅, 면접, 프로필 촬영",
        "intensity": "중간 (3~4단계)",
        "guide": "톤업 + 컨실러(다크서클/트러블 커버) + 눈썹 정리, 소요시간 7~10분",
    },
    "date": {
        "label": "데이트",
        "subtitle": "조명/사진빨 고려",
        "intensity": "중상 (사진 잘 받는 실팩 정도)",
        "guide": "\"자연스러운데 화면에 잘 나오는\" 밸런스",
    },
}

AGE_GROUPS = ["10대", "20대", "30대", "40대 이상"]

CONCERN_TAGS = [
    "지성/번들거림", "건조함", "다크서클", "트러블/뾰루지",
    "모공", "칙칙한 피부톤", "눈썹 정리 안 됨", "무슨 제품을 써야 할지 모르겠음",
]

# =========================================================================
# Function 4에 쓰일 제품 카드 데이터 (프로토타입용 샘플 데이터)
# =========================================================================
PRODUCTS = [
    {
        "id": 1, "name": "올데이 톤업 선크림", "category": "선케어",
        "price": 18000, "modes": ["daily", "event", "date"],
        "skin_types": ["지성", "복합성", "민감성"],
        "concerns": ["칙칙한 피부톤", "지성/번들거림"],
        "point": "SPF50+/PA++++ · 백탁 없는 톤업",
        "desc": "자외선 차단과 동시에 피부톤을 밝혀줘서 '꾸안꾸' 베이스에 최적.",
    },
    {
        "id": 2, "name": "수분 진정 올인원 로션", "category": "스킨케어",
        "price": 15000, "modes": ["daily"],
        "skin_types": ["건조함", "민감성"],
        "concerns": ["건조함"],
        "point": "스킨+로션+에센스 3in1",
        "desc": "복잡한 루틴 없이 한 번 바르면 끝나는 초간단 보습 케어.",
    },
    {
        "id": 3, "name": "그린 컨실러 스틱", "category": "베이스",
        "price": 12000, "modes": ["event", "date"],
        "skin_types": ["지성", "복합성", "건조함"],
        "concerns": ["트러블/뾰루지", "다크서클"],
        "point": "펜슬형, 발색 자연스러움",
        "desc": "면접·소개팅 전 트러블과 다크서클만 콕 짚어 커버.",
    },
    {
        "id": 4, "name": "브로우 픽서 (눈썹 정리 젤)", "category": "아이브로우",
        "price": 9000, "modes": ["event", "date"],
        "skin_types": ["지성", "건조함", "복합성", "민감성"],
        "concerns": ["눈썹 정리 안 됨"],
        "point": "투명 젤, 하루종일 고정",
        "desc": "숱을 그대로 살리면서 방향만 잡아주는 초보자용 브로우 젤.",
    },
    {
        "id": 5, "name": "매트 모공 프라이머", "category": "베이스",
        "price": 21000, "modes": ["date"],
        "skin_types": ["지성", "복합성"],
        "concerns": ["모공", "지성/번들거림"],
        "point": "모공 커버 + 피지 컨트롤",
        "desc": "사진 찍을 때 조명에 번들거리지 않게 잡아주는 매트 마무리.",
    },
    {
        "id": 6, "name": "저자극 클렌징 폼", "category": "클렌징",
        "price": 11000, "modes": ["daily"],
        "skin_types": ["민감성", "건조함", "복합성", "지성"],
        "concerns": ["건조함", "트러블/뾰루지"],
        "point": "약산성, 저자극",
        "desc": "세안만으로도 트러블을 줄여주는 순한 클렌징 시작 아이템.",
    },
    {
        "id": 7, "name": "글로우 하이라이터 스틱", "category": "포인트 메이크업",
        "price": 14000, "modes": ["date"],
        "skin_types": ["건조함", "복합성"],
        "concerns": ["칙칙한 피부톤"],
        "point": "은은한 광채, 과하지 않음",
        "desc": "사진빨을 살려주는 은은한 하이라이트로 입체감 부여.",
    },
    {
        "id": 8, "name": "산뜻 쿨링 아이크림", "category": "스킨케어",
        "price": 23000, "modes": ["event", "date"],
        "skin_types": ["건조함", "민감성", "복합성", "지성"],
        "concerns": ["다크서클"],
        "point": "쿨링 롤러 팁, 즉각 진정",
        "desc": "중요한 일정 직전 다크서클과 피로한 눈매를 빠르게 케어.",
    },
]


def recommend_products(profile, mode):
    """프로필(피부타입/고민/가격대) + 선택 모드 기준 추천 리스트 생성"""
    skin_type = profile.get("skin_type")
    concerns = set(profile.get("concerns") or [])
    price_min = profile.get("price_min") or 0
    price_max = profile.get("price_max") or 10 ** 9

    scored = []
    for p in PRODUCTS:
        if mode not in p["modes"]:
            continue
        if not (price_min <= p["price"] <= price_max):
            continue
        score = 0
        if skin_type and skin_type in p["skin_types"]:
            score += 2
        score += len(concerns & set(p["concerns"])) * 3
        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        scored = [(0, p) for p in PRODUCTS if mode in p["modes"]]

    return [p for _, p in scored]


# =========================================================================
# 공통 CSS + 레이아웃 (base.html 대신 문자열로 인라인)
# =========================================================================
STYLE_CSS = """
:root {
  --bg: #EEEBE3; --paper: #FFFFFF; --ink: #23262B; --ink-soft: #5B6169;
  --line: #DBD6C9; --teal: #2F6F62; --teal-dark: #234F45; --rust: #C1613B;
  --slate: #8B93A1; --radius: 18px;
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:-apple-system,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif;
  -webkit-font-smoothing:antialiased; }
.app-shell { max-width:480px; margin:0 auto; min-height:100vh; background:var(--paper);
  box-shadow:0 0 40px rgba(0,0,0,0.06); display:flex; flex-direction:column; }
.topbar { display:flex; align-items:center; justify-content:space-between; padding:18px 22px;
  border-bottom:1px solid var(--line); }
.brand { font-weight:800; letter-spacing:0.06em; color:var(--teal-dark); text-decoration:none; font-size:15px; }
.saved-link { font-size:13px; color:var(--ink-soft); text-decoration:none; border:1px solid var(--line);
  padding:6px 12px; border-radius:999px; }
.saved-link:hover { border-color:var(--rust); color:var(--rust); }
.content { flex:1; padding:28px 22px 40px; }
.hero-eyebrow { text-transform:uppercase; letter-spacing:0.14em; font-size:11px; color:var(--rust);
  font-weight:700; margin:0 0 10px; }
.hero h1 { font-size:28px; line-height:1.35; margin:0 0 14px; font-weight:800; letter-spacing:-0.01em; }
.hero-desc { color:var(--ink-soft); line-height:1.6; font-size:14.5px; margin-bottom:26px; }
.btn-primary { display:inline-block; background:var(--teal-dark); color:#fff; text-decoration:none;
  padding:14px 22px; border-radius:999px; font-weight:700; font-size:14.5px; border:none; cursor:pointer; text-align:center; }
.btn-primary:active { transform:scale(0.98); }
.btn-ghost { display:inline-block; background:transparent; color:var(--ink-soft); text-decoration:none;
  padding:13px 20px; border-radius:999px; font-weight:600; font-size:14px; border:1px solid var(--line);
  cursor:pointer; text-align:center; }
.info-cards { margin-top:36px; display:flex; flex-direction:column; gap:12px; }
.info-card { border:1px solid var(--line); border-radius:var(--radius); padding:16px 18px; background:#FBFAF7; }
.info-card .tag { font-size:10.5px; letter-spacing:0.1em; color:var(--teal); font-weight:800; }
.info-card h3 { margin:6px 0 4px; font-size:16px; }
.info-card p { margin:0; color:var(--ink-soft); font-size:13.5px; }
.step-dots { display:flex; gap:6px; margin-bottom:26px; }
.dot { flex:1; height:4px; border-radius:2px; background:var(--line); }
.dot.active { background:var(--teal); }
.step h2 { font-size:21px; margin-bottom:6px; }
.step-sub { color:var(--ink-soft); font-size:13.5px; margin-bottom:22px; }
.hidden { display:none; }
.field-label { font-size:12.5px; font-weight:700; color:var(--ink-soft); text-transform:uppercase;
  letter-spacing:0.06em; margin:18px 0 10px; }
.choice-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.choice-grid-4 { grid-template-columns:1fr 1fr; }
.choice-card { border:1.5px solid var(--line); border-radius:14px; padding:16px; text-align:center;
  font-weight:600; cursor:pointer; position:relative; background:#FBFAF7; }
.choice-card.small { padding:12px 8px; font-size:13.5px; }
.choice-card input { position:absolute; opacity:0; }
.choice-card:has(input:checked) { border-color:var(--teal); background:#EAF2EF; color:var(--teal-dark); }
.chip-grid { display:flex; flex-wrap:wrap; gap:8px; }
.chip { border:1.5px solid var(--line); border-radius:999px; padding:9px 14px; font-size:13px;
  cursor:pointer; background:#FBFAF7; position:relative; }
.chip input { position:absolute; opacity:0; }
.chip:has(input:checked) { border-color:var(--rust); background:#FBEAE1; color:var(--rust); font-weight:700; }
.price-range { margin-top:6px; }
.price-labels { display:flex; justify-content:space-between; font-weight:800; color:var(--teal-dark);
  margin-bottom:12px; font-size:15px; }
input[type="range"] { width:100%; margin-bottom:18px; accent-color:var(--teal); }
.step-nav { display:flex; gap:10px; margin-top:24px; }
.step-nav .btn-primary, .step-nav .btn-ghost { flex:1; }
.next-btn { margin-top:24px; width:100%; }
.page-title { font-size:21px; margin-bottom:4px; }
.mode-list { display:flex; flex-direction:column; gap:12px; margin-top:18px; }
.mode-card { display:block; border:1.5px solid var(--line); border-radius:var(--radius); padding:18px;
  text-decoration:none; color:var(--ink); background:#FBFAF7; }
.mode-card:hover { border-color:var(--teal); }
.mode-card-head { display:flex; justify-content:space-between; align-items:center; }
.mode-card-head h3 { margin:0; font-size:18px; }
.mode-badge { font-size:11px; font-weight:700; color:var(--teal-dark); background:#EAF2EF;
  padding:4px 10px; border-radius:999px; }
.mode-subtitle { margin:8px 0 4px; font-weight:600; font-size:13.5px; color:var(--ink-soft); }
.mode-guide { margin:0; font-size:13px; color:var(--ink-soft); }
.edit-profile-link { display:inline-block; margin-top:22px; font-size:13px; color:var(--ink-soft); text-decoration:none; }
.recommend-header h2 { margin-bottom:2px; font-size:20px; }
.card-stack { position:relative; height:420px; margin:24px 0 18px; }
.product-card { position:absolute; inset:0; background:var(--paper); border:1px solid var(--line);
  border-radius:22px; box-shadow:0 14px 30px rgba(35,38,43,0.10); display:flex; flex-direction:column;
  justify-content:flex-end; touch-action:none; cursor:grab; transition:transform 0.2s ease; overflow:hidden; }
.product-card:active { cursor:grabbing; }
.product-card-point { position:absolute; top:16px; left:16px; background:var(--teal-dark); color:#fff;
  font-size:11.5px; font-weight:700; padding:6px 12px; border-radius:999px; }
.product-card-body { padding:20px; background:linear-gradient(180deg, rgba(255,255,255,0) 0%, #FFFFFF 22%); }
.product-category { font-size:11px; color:var(--rust); font-weight:800; letter-spacing:0.06em; }
.product-card-body h3 { margin:6px 0 8px; font-size:20px; }
.product-desc { color:var(--ink-soft); font-size:13.5px; line-height:1.5; margin:0 0 10px; }
.product-price { font-weight:800; font-size:17px; margin:0 0 10px; color:var(--ink); }
.product-tags { display:flex; flex-wrap:wrap; gap:6px; }
.mini-tag { font-size:11px; background:#F1EFE9; color:var(--ink-soft); padding:4px 9px; border-radius:999px; }
.swipe-flag { position:absolute; top:24px; font-weight:900; font-size:22px; padding:6px 14px;
  border-radius:8px; border:3px solid; opacity:0; pointer-events:none; }
.flag-like { right:20px; color:var(--teal); border-color:var(--teal); transform:rotate(8deg); }
.flag-pass { left:20px; color:var(--slate); border-color:var(--slate); transform:rotate(-8deg); }
.fly-right { transform:translateX(600px) rotate(20deg) !important; opacity:0; }
.fly-left { transform:translateX(-600px) rotate(-20deg) !important; opacity:0; }
.stack-empty { position:absolute; inset:0; display:none; flex-direction:column; align-items:center;
  justify-content:center; gap:12px; text-align:center; border:1.5px dashed var(--line); border-radius:22px; padding:24px; }
.stack-empty.visible { display:flex; }
.swipe-actions { display:flex; justify-content:center; gap:22px; }
.round-btn { width:58px; height:58px; border-radius:50%; border:none; font-size:22px; cursor:pointer;
  box-shadow:0 8px 18px rgba(0,0,0,0.12); }
.round-btn.pass { background:#fff; color:var(--slate); border:2px solid var(--line); }
.round-btn.like { background:var(--rust); color:#fff; }
.empty-state { text-align:center; padding:40px 10px; color:var(--ink-soft); }
.empty-state p { margin-bottom:18px; }
.saved-list { display:flex; flex-direction:column; gap:12px; margin-top:16px; }
.saved-item { display:flex; justify-content:space-between; align-items:center; border:1px solid var(--line);
  border-radius:16px; padding:16px; background:#FBFAF7; gap:12px; }
.saved-item h3 { margin:4px 0; font-size:16px; }
.saved-price { font-weight:800; white-space:nowrap; color:var(--teal-dark); }
@media (max-width:380px) { .content { padding:22px 16px 32px; } .hero h1 { font-size:24px; } }
"""

BASE_HTML = """
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>___TITLE___</title>
<style>""" + STYLE_CSS + """</style>
</head>
<body>
  <div class="app-shell">
    <header class="topbar">
      <a href="{{ url_for('index') }}" class="brand">MEN·CARE</a>
      <a href="{{ url_for('saved') }}" class="saved-link">찜한 제품</a>
    </header>
    <main class="content">
      ___CONTENT___
    </main>
  </div>
  ___SCRIPTS___
</body>
</html>
"""

# =========================================================================
# 페이지 템플릿 (문자열로 인라인, {% extends %} 로 BASE_HTML 상속)
# =========================================================================
INDEX_TITLE = "맨케어 추천 · 시작"
INDEX_CONTENT = """
<section class="hero">
  <p class="hero-eyebrow">화장품 매장이 아직 낯선 당신에게</p>
  <h1>복잡한 루틴 없이,<br>딱 필요한 제품만 추천해드려요</h1>
  <p class="hero-desc">
    민현우, 28세, 영업 신입사원. 화장품에 대한 개념이 없는 초보자도
    "무엇을, 왜 써야 하는지"부터 자연스럽게 알아갈 수 있도록 설계했어요.
  </p>
  <a class="btn-primary" href="{{ url_for('profile') }}">1분만에 내 취향 설정하기</a>
</section>
<section class="info-cards">
  <div class="info-card">
    <span class="tag">STEP 1</span>
    <h3>간단 프로필 설정</h3>
    <p>나이대, 피부타입, 고민만 골라주세요. 어렵지 않아요.</p>
  </div>
  <div class="info-card">
    <span class="tag">STEP 2</span>
    <h3>상황(모드) 선택</h3>
    <p>데일리 · 이벤트 · 데이트 — 오늘 필요한 만큼만 준비해요.</p>
  </div>
  <div class="info-card">
    <span class="tag">STEP 3</span>
    <h3>카드 스와이프</h3>
    <p>마음에 들면 오른쪽, 아니면 왼쪽. 취향이 쌓일수록 추천이 똑똑해져요.</p>
  </div>
</section>
"""

PROFILE_TITLE = "프로필 설정"
PROFILE_CONTENT = """
<form method="post" action="{{ url_for('profile') }}" id="profile-form">
  <div class="step-dots">
    <span class="dot active" data-dot="1"></span>
    <span class="dot" data-dot="2"></span>
    <span class="dot" data-dot="3"></span>
  </div>

  <section class="step" data-step="1">
    <h2>나이대가 어떻게 되세요?</h2>
    <p class="step-sub">비슷한 또래가 많이 찾는 제품을 우선 보여드릴게요.</p>
    <div class="choice-grid">
      {% for age in age_groups %}
      <label class="choice-card">
        <input type="radio" name="age_group" value="{{ age }}" required>
        <span>{{ age }}</span>
      </label>
      {% endfor %}
    </div>
    <button type="button" class="btn-primary next-btn" data-next="2">다음</button>
  </section>

  <section class="step hidden" data-step="2">
    <h2>피부타입과 고민을 알려주세요</h2>
    <p class="step-sub">잘 모르겠으면 "민감성 / 잘 모르겠어요"를 골라도 괜찮아요.</p>

    <h4 class="field-label">피부타입</h4>
    <div class="choice-grid choice-grid-4">
      <label class="choice-card small"><input type="radio" name="skin_type" value="지성" required><span>지성</span></label>
      <label class="choice-card small"><input type="radio" name="skin_type" value="건조함"><span>건성</span></label>
      <label class="choice-card small"><input type="radio" name="skin_type" value="복합성"><span>복합성</span></label>
      <label class="choice-card small"><input type="radio" name="skin_type" value="민감성"><span>민감성 / 잘 모르겠어요</span></label>
    </div>

    <h4 class="field-label">지금 가장 신경 쓰이는 것 (복수 선택 가능)</h4>
    <div class="chip-grid">
      {% for tag in concern_tags %}
      <label class="chip">
        <input type="checkbox" name="concerns" value="{{ tag }}">
        <span>{{ tag }}</span>
      </label>
      {% endfor %}
    </div>

    <div class="step-nav">
      <button type="button" class="btn-ghost prev-btn" data-prev="1">이전</button>
      <button type="button" class="btn-primary next-btn" data-next="3">다음</button>
    </div>
  </section>

  <section class="step hidden" data-step="3">
    <h2>대략적인 예산은요?</h2>
    <p class="step-sub">제품 1개 기준 가격대를 알려주시면 그 안에서만 추천할게요.</p>
    <div class="price-range">
      <div class="price-labels">
        <span id="price-min-label">10,000원</span>
        <span>~</span>
        <span id="price-max-label">30,000원</span>
      </div>
      <label class="field-label">최소 가격</label>
      <input type="range" id="price_min" name="price_min" min="0" max="50000" step="1000" value="10000">
      <label class="field-label">최대 가격</label>
      <input type="range" id="price_max" name="price_max" min="5000" max="80000" step="1000" value="30000">
    </div>
    <div class="step-nav">
      <button type="button" class="btn-ghost prev-btn" data-prev="2">이전</button>
      <button type="submit" class="btn-primary">추천받으러 가기</button>
    </div>
  </section>
</form>
"""
PROFILE_SCRIPTS = """
<script>
const steps = document.querySelectorAll(".step");
const dots = document.querySelectorAll(".dot");
function goToStep(n) {
  steps.forEach(s => s.classList.toggle("hidden", s.dataset.step !== String(n)));
  dots.forEach(d => d.classList.toggle("active", parseInt(d.dataset.dot) <= n));
}
document.querySelectorAll(".next-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const current = btn.closest(".step");
    const requiredInputs = current.querySelectorAll("input[required]");
    for (const inp of requiredInputs) {
      if (inp.type === "radio") {
        const name = inp.name;
        const checked = current.querySelector(`input[name="${name}"]:checked`);
        if (!checked) { alert("항목을 하나 선택해주세요."); return; }
      }
    }
    goToStep(parseInt(btn.dataset.next));
  });
});
document.querySelectorAll(".prev-btn").forEach(btn => {
  btn.addEventListener("click", () => goToStep(parseInt(btn.dataset.prev)));
});
const priceMin = document.getElementById("price_min");
const priceMax = document.getElementById("price_max");
const priceMinLabel = document.getElementById("price-min-label");
const priceMaxLabel = document.getElementById("price-max-label");
function fmt(v){ return Number(v).toLocaleString("ko-KR") + "원"; }
function syncPrice() {
  if (parseInt(priceMin.value) > parseInt(priceMax.value)) { priceMax.value = priceMin.value; }
  priceMinLabel.textContent = fmt(priceMin.value);
  priceMaxLabel.textContent = fmt(priceMax.value);
}
priceMin.addEventListener("input", syncPrice);
priceMax.addEventListener("input", syncPrice);
</script>
"""

MODE_TITLE = "상황 선택"
MODE_CONTENT = """
<h2 class="page-title">오늘은 어떤 상황이세요?</h2>
<p class="step-sub">상황에 맞춰 딱 필요한 만큼만 추천해드려요.</p>
<div class="mode-list">
  {% for key, m in modes.items() %}
  <a class="mode-card" href="{{ url_for('recommend', mode=key) }}">
    <div class="mode-card-head">
      <h3>{{ m.label }}</h3>
      <span class="mode-badge">{{ m.intensity }}</span>
    </div>
    <p class="mode-subtitle">{{ m.subtitle }}</p>
    <p class="mode-guide">{{ m.guide }}</p>
  </a>
  {% endfor %}
</div>
<a class="edit-profile-link" href="{{ url_for('profile') }}">← 프로필 다시 설정하기</a>
"""

RECOMMEND_TITLE_TPL = "{label} 추천"
RECOMMEND_CONTENT = """
<div class="recommend-header">
  <h2>{{ mode_info.label }} 추천</h2>
  <p class="step-sub">{{ mode_info.guide }}</p>
</div>
{% if products|length == 0 %}
<div class="empty-state">
  <p>조건에 맞는 제품이 아직 없어요. 예산 범위를 넓혀볼까요?</p>
  <a class="btn-primary" href="{{ url_for('profile') }}">프로필 다시 설정</a>
</div>
{% else %}
<div class="card-stack" id="card-stack" data-mode="{{ mode }}">
  {% for p in products %}
  <div class="product-card" data-id="{{ p.id }}" style="z-index: {{ loop.length - loop.index0 }}">
    <div class="product-card-point">{{ p.point }}</div>
    <div class="product-card-body">
      <span class="product-category">{{ p.category }}</span>
      <h3>{{ p.name }}</h3>
      <p class="product-desc">{{ p.desc }}</p>
      <p class="product-price">{{ "{:,}".format(p.price) }}원</p>
      <div class="product-tags">
        {% for c in p.concerns %}<span class="mini-tag">{{ c }}</span>{% endfor %}
      </div>
    </div>
    <div class="swipe-flag flag-like">찜!</div>
    <div class="swipe-flag flag-pass">패스</div>
  </div>
  {% endfor %}
  <div class="stack-empty" id="stack-empty">
    <p>오늘 준비된 카드를 모두 확인했어요 🎉</p>
    <a class="btn-primary" href="{{ url_for('mode_select') }}">다른 상황 보기</a>
    <a class="btn-ghost" href="{{ url_for('saved') }}">찜한 제품 보러가기</a>
  </div>
</div>
<div class="swipe-actions">
  <button id="btn-pass" class="round-btn pass">✕</button>
  <button id="btn-like" class="round-btn like">♥</button>
</div>
{% endif %}
"""
RECOMMEND_SCRIPTS = """
<script>
const stack = document.getElementById("card-stack");
const mode = stack ? stack.dataset.mode : null;
function sendSwipe(productId, action) {
  fetch("/api/swipe", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({mode: mode, product_id: parseInt(productId), action: action})
  }).catch(() => {});
}
function topCard() {
  const cards = document.querySelectorAll(".product-card");
  return cards.length ? cards[cards.length - 1] : null;
}
function removeTop(action) {
  const card = topCard();
  if (!card) return;
  sendSwipe(card.dataset.id, action);
  card.classList.add(action === "like" ? "fly-right" : "fly-left");
  setTimeout(() => {
    card.remove();
    if (!document.querySelector(".product-card")) {
      document.getElementById("stack-empty").classList.add("visible");
      const actions = document.querySelector(".swipe-actions");
      if (actions) actions.style.display = "none";
    }
  }, 220);
}
document.getElementById("btn-like")?.addEventListener("click", () => removeTop("like"));
document.getElementById("btn-pass")?.addEventListener("click", () => removeTop("pass"));
let startX = 0, currentX = 0, dragging = false, activeCard = null;
function attachDrag(card) {
  card.addEventListener("pointerdown", (e) => {
    dragging = true; activeCard = card; startX = e.clientX; card.setPointerCapture(e.pointerId);
  });
  card.addEventListener("pointermove", (e) => {
    if (!dragging || activeCard !== card) return;
    currentX = e.clientX - startX;
    card.style.transform = `translateX(${currentX}px) rotate(${currentX / 20}deg)`;
    card.querySelector(".flag-like").style.opacity = currentX > 30 ? Math.min(currentX / 100, 1) : 0;
    card.querySelector(".flag-pass").style.opacity = currentX < -30 ? Math.min(-currentX / 100, 1) : 0;
  });
  const end = () => {
    if (!dragging || activeCard !== card) return;
    dragging = false;
    if (currentX > 90) { removeTop("like"); }
    else if (currentX < -90) { removeTop("pass"); }
    else {
      card.style.transform = "";
      card.querySelector(".flag-like").style.opacity = 0;
      card.querySelector(".flag-pass").style.opacity = 0;
    }
    currentX = 0; activeCard = null;
  };
  card.addEventListener("pointerup", end);
  card.addEventListener("pointerleave", end);
}
document.querySelectorAll(".product-card").forEach(attachDrag);
</script>
"""

SAVED_TITLE = "찜한 제품"
SAVED_CONTENT = """
<h2 class="page-title">찜한 제품</h2>
{% if products|length == 0 %}
<div class="empty-state">
  <p>아직 찜한 제품이 없어요.</p>
  <a class="btn-primary" href="{{ url_for('mode_select') }}">추천받으러 가기</a>
</div>
{% else %}
<div class="saved-list">
  {% for p in products %}
  <div class="saved-item">
    <div>
      <span class="product-category">{{ p.category }}</span>
      <h3>{{ p.name }}</h3>
      <p class="product-desc">{{ p.desc }}</p>
    </div>
    <div class="saved-price">{{ "{:,}".format(p.price) }}원</div>
  </div>
  {% endfor %}
</div>
{% endif %}
<a class="edit-profile-link" href="{{ url_for('mode_select') }}">← 상황 다시 고르기</a>
"""


def render(title, content, scripts="", **ctx):
    """BASE_HTML의 자리표시자를 채운 뒤 한 번에 Jinja 렌더링"""
    page = (
        BASE_HTML.replace("___TITLE___", title)
        .replace("___CONTENT___", content)
        .replace("___SCRIPTS___", scripts)
    )
    return render_template_string(page, **ctx)


# =========================================================================
# 라우트
# =========================================================================

@app.route("/")
def index():
    get_or_create_profile()
    return render(INDEX_TITLE, INDEX_CONTENT)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    prof = get_or_create_profile()
    if request.method == "POST":
        prof["age_group"] = request.form.get("age_group")
        prof["skin_type"] = request.form.get("skin_type")
        prof["concerns"] = request.form.getlist("concerns")
        try:
            prof["price_min"] = int(request.form.get("price_min", 10000))
            prof["price_max"] = int(request.form.get("price_max", 30000))
        except ValueError:
            pass
        return redirect(url_for("mode_select"))
    return render(
        PROFILE_TITLE, PROFILE_CONTENT, PROFILE_SCRIPTS,
        profile=prof, age_groups=AGE_GROUPS, concern_tags=CONCERN_TAGS,
    )


@app.route("/mode")
def mode_select():
    prof = get_or_create_profile()
    if not prof["age_group"]:
        return redirect(url_for("profile"))
    return render(MODE_TITLE, MODE_CONTENT, modes=MODES, profile=prof)


@app.route("/recommend/<mode>")
def recommend(mode):
    if mode not in MODES:
        return redirect(url_for("mode_select"))
    prof = get_or_create_profile()
    products = recommend_products(prof, mode)
    title = RECOMMEND_TITLE_TPL.format(label=MODES[mode]["label"])
    return render(
        title, RECOMMEND_CONTENT, RECOMMEND_SCRIPTS,
        mode=mode, mode_info=MODES[mode], products=products, profile=prof,
    )


@app.route("/api/swipe", methods=["POST"])
def api_swipe():
    """카드 스와이프(찜/패스) 기록 저장 - Function 4"""
    data = request.get_json(force=True)
    prof = get_or_create_profile()
    prof["history"].append({
        "mode": data.get("mode"),
        "product_id": data.get("product_id"),
        "action": data.get("action"),  # 'like' or 'pass'
    })
    return jsonify({"ok": True})


@app.route("/saved")
def saved():
    prof = get_or_create_profile()
    liked_ids = [h["product_id"] for h in prof["history"] if h["action"] == "like"]
    liked_products = [p for p in PRODUCTS if p["id"] in liked_ids]
    return render(SAVED_TITLE, SAVED_CONTENT, products=liked_products)


@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
