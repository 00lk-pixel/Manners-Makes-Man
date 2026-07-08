# -*- coding: utf-8 -*-
"""
For Him - AI 뷰티 가이드 프로토타입

Streamlit Cloud는 Streamlit 스크립트만 서빙할 수 있어서(순수 Flask/정적 서버 불가),
직접 만든 for_him_prototype.html(제품 그리드 + 3D 얼굴 와이어프레임 사용법 뷰어)을
수정 없이 그대로 iframe에 로드해서 원본과 동일한 화면/동작을 보여준다.

실행: pip install -r requirements.txt && streamlit run app.py
"""

import pathlib

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="For Him - AI 뷰티 가이드", page_icon="🧴", layout="wide")

HTML_PATH = pathlib.Path(__file__).parent / "for_him_prototype.html"
html = HTML_PATH.read_text(encoding="utf-8")

components.html(html, height=1100, scrolling=True)
