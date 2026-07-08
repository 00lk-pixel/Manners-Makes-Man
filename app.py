# -*- coding: utf-8 -*-
"""
남성 그루밍/뷰티 초보자를 위한 '목적별 제품 추천 + 카드 스와이프' 프로토타입 (Streamlit 버전)
기획서(코스맥스 GCC R&I팀) 기반 구현 - 단일 파일(app.py) 버전

Function 1. 개인 정보 데이터베이스화 (세션 상태로 대체)
Function 2. 목적별 메이크업 및 제품 추천 시스템 (데일리 / 이벤트 / 데이트)
Function 3. 프로필 설정 (나이대 / 피부타입·고민 태그 / 가격대)
Function 4. 제품 카드 스와이프 UI (드래그 대신 패스/찜 버튼으로 구현)

실행: pip install -r requirements.txt && streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="맨케어 추천", page_icon="🧴", layout="centered")

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
SKIN_TYPES = ["지성", "건조함", "복합성", "민감성"]

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
# Function 1: 개인 정보 (Streamlit 세션 상태로 대체 - 브라우저 세션 동안 유지)
# =========================================================================
def init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "age_group": None,
            "skin_type": None,
            "concerns": [],
            "price_min": 10000,
            "price_max": 30000,
            "history": [],
        }
    st.session_state.setdefault("page", "index")
    st.session_state.setdefault("profile_step", 1)
    st.session_state.setdefault("mode", None)
    st.session_state.setdefault("stack", [])


def goto(page):
    st.session_state.page = page
    st.rerun()


def swipe(product_id, action):
    st.session_state.profile["history"].append({
        "mode": st.session_state.mode,
        "product_id": product_id,
        "action": action,
    })
    st.session_state.stack.pop(0)
    st.rerun()


init_state()

# =========================================================================
# 브랜드 룩앤필 (원본 Flask 프로토타입의 색상 팔레트 유지)
# =========================================================================
st.markdown("""
<style>
:root {
  --paper:#FFFFFF; --ink:#23262B; --ink-soft:#5B6169; --line:#DBD6C9;
  --teal:#2F6F62; --teal-dark:#234F45; --rust:#C1613B;
}
.block-container{max-width:480px; padding-top:1.5rem;}
h1,h2,h3{color:var(--ink);}
.hero-eyebrow{text-transform:uppercase; letter-spacing:.14em; font-size:11px;
  color:var(--rust); font-weight:700; margin:0 0 6px;}
.mode-badge{font-size:11px; font-weight:700; color:var(--teal-dark); background:#EAF2EF;
  padding:4px 10px; border-radius:999px; display:inline-block;}
.mini-tag{font-size:11px; background:#F1EFE9; color:var(--ink-soft); padding:4px 9px;
  border-radius:999px; display:inline-block; margin:2px 4px 0 0;}
.product-price{font-weight:800; font-size:17px; color:var(--ink);}
div.stButton>button[kind="primary"]{background:var(--teal-dark); border-color:var(--teal-dark);}
div.stButton>button[kind="primary"]:hover{background:var(--teal); border-color:var(--teal);}
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 상단 바
# =========================================================================
top_l, top_r = st.columns([3, 1])
top_l.markdown("### MEN·CARE")
if top_r.button("찜한 제품", use_container_width=True):
    goto("saved")

st.divider()


# =========================================================================
# 페이지별 렌더 함수
# =========================================================================
def page_index():
    st.markdown('<p class="hero-eyebrow">화장품 매장이 아직 낯선 당신에게</p>', unsafe_allow_html=True)
    st.title("복잡한 루틴 없이, 딱 필요한 제품만 추천해드려요")
    st.write(
        "민현우, 28세, 영업 신입사원. 화장품에 대한 개념이 없는 초보자도 "
        "\"무엇을, 왜 써야 하는지\"부터 자연스럽게 알아갈 수 있도록 설계했어요."
    )
    if st.button("1분만에 내 취향 설정하기", type="primary", use_container_width=True):
        goto("profile")

    st.write("")
    steps = [
        ("STEP 1", "간단 프로필 설정", "나이대, 피부타입, 고민만 골라주세요. 어렵지 않아요."),
        ("STEP 2", "상황(모드) 선택", "데일리 · 이벤트 · 데이트 — 오늘 필요한 만큼만 준비해요."),
        ("STEP 3", "카드 스와이프", "마음에 들면 찜, 아니면 패스. 취향이 쌓일수록 추천이 똑똑해져요."),
    ]
    for tag, title, desc in steps:
        with st.container(border=True):
            st.caption(tag)
            st.markdown(f"**{title}**")
            st.write(desc)


def page_profile():
    prof = st.session_state.profile
    step = st.session_state.profile_step
    st.progress(step / 3)

    if step == 1:
        st.subheader("나이대가 어떻게 되세요?")
        st.caption("비슷한 또래가 많이 찾는 제품을 우선 보여드릴게요.")
        default_idx = AGE_GROUPS.index(prof["age_group"]) if prof["age_group"] in AGE_GROUPS else None
        age = st.radio("나이대", AGE_GROUPS, index=default_idx, horizontal=True, label_visibility="collapsed")
        if st.button("다음", type="primary", use_container_width=True, disabled=age is None):
            prof["age_group"] = age
            st.session_state.profile_step = 2
            st.rerun()

    elif step == 2:
        st.subheader("피부타입과 고민을 알려주세요")
        st.caption("잘 모르겠으면 \"민감성 / 잘 모르겠어요\"를 골라도 괜찮아요.")
        st.markdown("**피부타입**")
        default_idx = SKIN_TYPES.index(prof["skin_type"]) if prof["skin_type"] in SKIN_TYPES else None
        skin = st.radio(
            "피부타입", SKIN_TYPES,
            format_func=lambda s: "민감성 / 잘 모르겠어요" if s == "민감성" else ("건성" if s == "건조함" else s),
            index=default_idx, horizontal=True, label_visibility="collapsed",
        )
        st.markdown("**지금 가장 신경 쓰이는 것 (복수 선택 가능)**")
        concerns = st.multiselect("고민", CONCERN_TAGS, default=prof["concerns"], label_visibility="collapsed")

        col1, col2 = st.columns(2)
        if col1.button("이전", use_container_width=True):
            st.session_state.profile_step = 1
            st.rerun()
        if col2.button("다음", type="primary", use_container_width=True, disabled=skin is None):
            prof["skin_type"] = skin
            prof["concerns"] = concerns
            st.session_state.profile_step = 3
            st.rerun()

    elif step == 3:
        st.subheader("대략적인 예산은요?")
        st.caption("제품 1개 기준 가격대를 알려주시면 그 안에서만 추천할게요.")
        price_min, price_max = st.slider(
            "가격대(원)", min_value=0, max_value=80000,
            value=(prof["price_min"], prof["price_max"]), step=1000,
        )
        col1, col2 = st.columns(2)
        if col1.button("이전", use_container_width=True):
            st.session_state.profile_step = 2
            st.rerun()
        if col2.button("추천받으러 가기", type="primary", use_container_width=True):
            prof["price_min"], prof["price_max"] = price_min, price_max
            goto("mode")


def page_mode():
    prof = st.session_state.profile
    if not prof["age_group"]:
        goto("profile")
        return
    st.subheader("오늘은 어떤 상황이세요?")
    st.caption("상황에 맞춰 딱 필요한 만큼만 추천해드려요.")
    for key, m in MODES.items():
        with st.container(border=True):
            head_l, head_r = st.columns([3, 2])
            head_l.markdown(f"**{m['label']}**")
            head_r.markdown(f'<span class="mode-badge">{m["intensity"]}</span>', unsafe_allow_html=True)
            st.write(m["subtitle"])
            st.caption(m["guide"])
            if st.button(f"{m['label']} 선택하기", key=f"mode-{key}", use_container_width=True):
                st.session_state.mode = key
                st.session_state.stack = [p["id"] for p in recommend_products(prof, key)]
                goto("recommend")
    if st.button("← 프로필 다시 설정하기"):
        st.session_state.profile_step = 1
        goto("profile")


def page_recommend():
    mode = st.session_state.mode
    if mode not in MODES:
        goto("mode")
        return
    prof = st.session_state.profile
    m = MODES[mode]
    st.subheader(f"{m['label']} 추천")
    st.caption(m["guide"])

    stack = st.session_state.stack
    if not stack:
        st.success("오늘 준비된 카드를 모두 확인했어요 🎉")
        col1, col2 = st.columns(2)
        if col1.button("다른 상황 보기", use_container_width=True):
            goto("mode")
        if col2.button("찜한 제품 보러가기", use_container_width=True):
            goto("saved")
        return

    pid = stack[0]
    p = next(x for x in PRODUCTS if x["id"] == pid)
    with st.container(border=True):
        st.caption(f"{p['point']}  ·  {len(stack)}장 남음")
        st.markdown(f"### {p['name']}")
        st.write(p["desc"])
        st.markdown(f'<span class="product-price">{p["price"]:,}원</span>', unsafe_allow_html=True)
        st.markdown(
            "".join(f'<span class="mini-tag">{c}</span>' for c in p["concerns"]),
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    if col1.button("✕ 패스", key=f"pass-{pid}", use_container_width=True):
        swipe(pid, "pass")
    if col2.button("♥ 찜", key=f"like-{pid}", type="primary", use_container_width=True):
        swipe(pid, "like")


def page_saved():
    prof = st.session_state.profile
    liked_ids = [h["product_id"] for h in prof["history"] if h["action"] == "like"]
    liked_products = [p for p in PRODUCTS if p["id"] in liked_ids]

    st.subheader("찜한 제품")
    if not liked_products:
        st.info("아직 찜한 제품이 없어요.")
        if st.button("추천받으러 가기", type="primary", use_container_width=True):
            goto("mode")
    else:
        for p in liked_products:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.caption(p["category"])
                col1.markdown(f"**{p['name']}**")
                col1.write(p["desc"])
                col2.markdown(f'<span class="product-price">{p["price"]:,}원</span>', unsafe_allow_html=True)

    if st.button("← 상황 다시 고르기"):
        goto("mode")


# =========================================================================
# 라우팅
# =========================================================================
PAGES = {
    "index": page_index,
    "profile": page_profile,
    "mode": page_mode,
    "recommend": page_recommend,
    "saved": page_saved,
}
PAGES.get(st.session_state.page, page_index)()

with st.sidebar:
    st.caption("프로토타입 제어")
    if st.button("세션 초기화 (reset)"):
        st.session_state.clear()
        st.rerun()
