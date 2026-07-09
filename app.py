# -*- coding: utf-8 -*-
"""
MMM — Makeup maketh man (1페이지: 헤더 + 감성 스플래시)

Streamlit Cloud는 Streamlit 스크립트만 서빙할 수 있어서(순수 Flask/정적 서버 불가),
직접 만든 for_him_prototype.html(헤더 + 스플래시)을 수정 없이 그대로 iframe에
로드해서 원본과 동일한 화면/동작을 보여준다. 오렌지 히어로/사이트 인덱스/갤러리/CTA/
푸터는 아직 이 화면에 없다 — 다음 단계에서 순서대로 이어붙일 예정.

실행: pip install -r requirements.txt && streamlit run app.py
"""

import pathlib

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MMM — Makeup maketh man", page_icon="💄", layout="wide")

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

components.html(html, height=800, scrolling=False)
