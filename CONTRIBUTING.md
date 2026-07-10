# 팀 작업 규칙 (브랜치 & 컨펌 워크플로)

5명이 각자 다른 파트를 맡아 작업하고, **모든 변경은 컨트롤타워(@00lk-pixel)의 컨펌 후에만
`main`(본 작업물)에 반영**됩니다. `main`에는 누구도 직접 push할 수 없습니다.

## 한눈에 보는 흐름

```
main (본 작업물, 보호됨)
 ├─ feat/철수/signup-page      ← 각자 자기 브랜치에서 작업
 ├─ feat/영희/profile-screen
 └─ feat/민수/product-scan
        ↓ 작업 완료되면 Pull Request(PR) 생성
    컨트롤타워 리뷰 & 승인 (Approve)
        ↓ 승인된 것부터 하나씩 순서대로
    main에 머지 → 전원이 pull 받아 최신 상태 유지
```

## 팀원이 하는 일

### 1. 작업 시작 — 항상 최신 main에서 브랜치 만들기

```bash
git switch main
git pull origin main
git switch -c feat/이름/작업내용     # 예: feat/chulsoo/signup-page
```

브랜치 이름 규칙: `feat/자기이름/무슨작업` (버그 수정은 `fix/이름/내용`)

### 2. 작업 & 커밋 & 푸시

```bash
git add <바꾼 파일>
git commit -m "가입 화면: 비밀번호 확인 입력창 추가"
git push -u origin feat/이름/작업내용
```

- 커밋은 작게, 자주. 커밋 메시지는 "무엇을 왜" 바꿨는지 알 수 있게.
- **자기 담당 파트의 파일만** 수정하기. 다른 파트 파일을 꼭 바꿔야 하면 PR 설명에 이유를 적기.

### 3. PR 올리기

푸시하면 GitHub에 "Compare & pull request" 버튼이 뜹니다. PR 템플릿에 따라
무엇을/왜 바꿨는지, 스크린샷과 함께 적어주세요. 컨트롤타워가 자동으로 리뷰어로 지정됩니다.

### 4. 리뷰 대응 & 머지 후 정리

- 수정 요청이 오면 같은 브랜치에 커밋을 더 쌓아 push하면 PR에 자동 반영됩니다.
- 내 PR보다 먼저 다른 PR이 머지되면 "Update branch" 버튼(또는 아래 명령)으로
  최신 main을 반영해야 머지할 수 있습니다:

```bash
git switch feat/이름/작업내용
git pull origin main    # 충돌이 나면 여기서 해결하고 커밋
git push
```

- 머지가 끝난 브랜치는 GitHub의 "Delete branch" 버튼으로 정리합니다.

## 컨트롤타워가 하는 일

1. **Pull Requests 탭**에서 대기 중인 PR 확인 — 각 PR의 "Files changed"에서
   누가 무엇을 바꿨는지 diff로 확인
2. 괜찮으면 **Review → Approve**, 고칠 게 있으면 **Request changes**로 코멘트
3. 승인한 PR을 **하나씩 순서대로 머지** (Merge pull request 버튼)
   - 하나를 머지하면 나머지 PR은 자동으로 "branch out-of-date" 상태가 되어,
     각 담당자가 최신 main을 반영한 뒤에야 다음 머지가 가능 → 꼬임 방지
4. 전체 진행 상황은 Pull Requests 탭(진행 중)과 main의 커밋 히스토리(반영 완료)로 파악

## 프로젝트 현 상태 확인 (전원)

- **본 작업물의 현 상태**: `main` 브랜치 = 항상 컨펌 완료된 최신 상태
- **누가 지금 뭘 하는지**: GitHub → Pull Requests 탭 (열려 있는 PR 목록)
- **각자 로컬을 최신으로**: 하루 시작할 때 `git switch main && git pull origin main`

## 실시간 미리보기 (Streamlit Cloud)

브랜치에 push가 들어올 때마다 해당 브랜치의 앱이 1~2분 안에 자동 재배포된다.
diff만 보지 말고, 아래 링크에서 실제 동작하는 화면으로 서로의 작업 상태를 확인하자.

| 브랜치 | 용도 | 미리보기 URL |
| --- | --- | --- |
| `main` | 본 작업물 (컨펌 완료된 최신 상태) | (기존 배포 앱 URL) |
| `BUNNY` | 담당: 경세 (컨트롤타워) | https://bunny.streamlit.app |
| `KITTY` | 담당: 소담 | https://kitty.streamlit.app |
| `PUPPY` | 담당: 서현 | https://puppy.streamlit.app |
| `FAWN` | 담당: 아림 | https://fawn.streamlit.app |
| `CALF` | 담당: 관용 | https://calf.streamlit.app |

- URL 이름이 이미 선점되어 배포 시 다른 이름(예: `mmm-bunny`)을 썼다면 이 표를 고쳐줄 것.
- 미리보기 앱은 접속이 며칠 없으면 잠든다 — "Zzz" 화면이 뜨면 깨우기 버튼 한 번이면 된다.
- 각 앱의 가입 데이터(`data/signups.json`)는 앱마다 독립이고 재배포 시 초기화된다.
