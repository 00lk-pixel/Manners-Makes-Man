# -*- coding: utf-8 -*-
"""
For Him - AI 뷰티 가이드 프로토타입

Streamlit Cloud는 Streamlit 스크립트만 서빙할 수 있어서(순수 Flask/정적 서버 불가),
직접 만든 for_him_prototype.html(제품 그리드 + 3D 얼굴 와이어프레임 사용법 뷰어)을
그대로 iframe에 로드해서 원본과 동일한 화면/동작을 보여준다. 제품별 사용법 음성
안내(mp3)는 assets/audio/에 실제 파일로 두고, 이 스크립트가 실행 시점에 base64로
인코딩해 HTML의 자리표시자에 채워 넣는다 (git diff에 거대한 base64 문자열이 그대로
찍히는 걸 피하기 위함).

실행: pip install -r requirements.txt && streamlit run app.py
"""

import base64
import pathlib

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="For Him - AI 뷰티 가이드", page_icon="🧴", layout="wide")

BASE_DIR = pathlib.Path(__file__).parent
HTML_PATH = BASE_DIR / "for_him_prototype.html"
AUDIO_DIR = BASE_DIR / "assets" / "audio"

html = HTML_PATH.read_text(encoding="utf-8")

for audio_path in AUDIO_DIR.glob("*.mp3"):
    product_id = audio_path.stem
    data_uri = "data:audio/mpeg;base64," + base64.b64encode(audio_path.read_bytes()).decode("ascii")
    html = html.replace(f"__NARRATION_AUDIO_{product_id}__", data_uri)

components.html(html, height=1100, scrolling=True)
