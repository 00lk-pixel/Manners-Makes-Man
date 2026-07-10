# MMM (Makeup Maketh Man) — 프로젝트 가이드

남성용 화장품 추천 서비스 프로토타입. Streamlit 앱 하나로 배포된다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 구조 — 꼭 알아야 할 것

- **`for_him_prototype.html`** — 실제 화면 전부 (헤더 + 스플래시 + 이메일 가입 + 프로필 설정).
  CSS/JS 포함 단일 파일이며, 화면 수정은 대부분 이 파일에서 한다.
  주의: base64 폰트가 인라인되어 있어 일부 줄이 매우 길다(수백만 자).
  파일 전체를 한 번에 읽지 말고 Grep으로 필요한 부분을 찾아서 offset/limit으로 읽을 것.
- **`app.py`** — Streamlit 래퍼. 위 HTML을 `components.html()` iframe으로 그대로 로드한다.
  - iframe sandbox 제약 때문에 iframe 안에서는 최상단 페이지를 이동시킬 수 없다.
    화면 쪽 JS는 `notifyParent()`(postMessage)로 알리기만 하고, app.py가
    `st.html(..., unsafe_allow_javascript=True)`로 심은 최상단 리스너가
    쿼리 파라미터(`?signup=1` 등)로 변환해 Streamlit이 처리한다. 이 브리지 구조를 깨지 말 것.
  - 사용자 데이터는 `data/signups.json`에 저장된다 (데모용, DB 없음). 비밀번호는 저장하지 않는다.
- **`index.html`** — 별도 시안 페이지 (현재 메인 플로우에는 연결 안 됨).

## 팀 작업 규칙 (Claude가 반드시 지킬 것)

이 프로젝트는 5명이 팀원별 브랜치(BUNNY, KITTY, PUPPY, FAWN, CALF)로 작업하고,
모든 변경은 PR로 컨트롤타워(@00lk-pixel)의 승인을 받아야 `main`에 반영된다.
자세한 절차는 `CONTRIBUTING.md` 참고.

1. **현재 체크아웃된 브랜치에서만 작업한다.** `main`으로 체크아웃을 바꾸거나
   `main`에 직접 커밋/푸시하지 않는다. 사용자가 어느 브랜치인지 모르는 것 같으면
   `git branch --show-current`로 확인해서 알려준다.
2. **머지는 PR로만.** 작업이 끝나면 자기 브랜치에 커밋 → `git push` →
   GitHub에서 자기 브랜치 → `main` PR 생성을 안내한다. 로컬에서 `git merge`로
   main에 합치지 않는다.
3. **자기 담당 파트의 파일만 수정한다.** 다른 팀원 파트의 파일을 바꿔야 할 이유가
   생기면 임의로 고치지 말고 사용자에게 먼저 확인한다.
4. **작업 시작 전 최신 main 반영.** 새 작업을 시작할 때는
   `git pull origin main`으로 자기 브랜치에 최신 main을 먼저 합친다.
5. 커밋 메시지는 "무엇을 왜 바꿨는지"가 드러나게 한 줄 요약으로 쓴다 (한국어 OK).
