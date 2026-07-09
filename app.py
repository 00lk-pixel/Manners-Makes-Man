# -*- coding: utf-8 -*-
"""
MMM — Makeup maketh man (브랜드 메인 랜딩페이지)

Streamlit Cloud는 Streamlit 스크립트만 서빙할 수 있어서(순수 Flask/정적 서버 불가),
직접 만든 for_him_prototype.html(스플래시 + 히어로 + 사이트 인덱스 + 갤러리 + CTA)을
수정 없이 그대로 iframe에 로드해서 원본과 동일한 화면/동작을 보여준다.

실행: pip install -r requirements.txt && streamlit run app.py
"""

import pathlib

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MMM — Makeup maketh man", page_icon="💄", layout="wide")

HTML_PATH = pathlib.Path(__file__).parent / "for_him_prototype.html"
html = HTML_PATH.read_text(encoding="utf-8")

components.html(html, height=900, scrolling=True)
