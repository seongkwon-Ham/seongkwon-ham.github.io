# 개인 웹사이트 (seongkwon-ham.github.io)

공개 주소: <https://seongkwon-ham.github.io>

## 폴더 구조

```
personal-website/
├─ README.md      이 설명서
├─ publish.bat    ★ 더블클릭 한 번으로 빌드 + 업로드
├─ build.py       사이트를 만드는 스크립트 (설정값은 맨 위에 있음)
├─ content/       ★ 글을 고치는 곳 (페이지 하나 = 파일 하나)
│   ├─ home.html      Home: 한 줄 소개, 사진 자리, 인사말, 논문 목록
│   ├─ research.html  Research: 논문 3편 (초록, 그림, 초안 요청 링크)
│   ├─ cv.html        CV
│   └─ contact.html   Contact
├─ static/        ★ 그대로 복사되는 파일 (디자인, 그림 데이터, 사진)
│   ├─ site.css       디자인 (색, 글꼴, 배치)
│   ├─ site.js        동작 (다크 모드, 스크롤 효과, 논문 그림 그리기)
│   ├─ figdata.js     논문 그림의 숫자 (build.py --figures 가 만듦)
│   └─ photo.jpg      프로필 사진 (넣으면 Home 에 나옴, 없으면 SH 이니셜)
└─ docs/          자동 생성. GitHub 가 이 폴더를 공개한다. 직접 고치지 않는다.
```

`content/` 와 `static/` 만 고친다. `docs/` 는 `build.py` 를 실행할 때마다 지우고 새로 만든다.

## 고치는 순서

가장 쉬운 방법: `content/` 나 `static/` 의 파일을 고친 뒤 **`publish.bat` 을 더블클릭**한다.
빌드, 버전 저장(commit), 업로드(push)를 한 번에 하고 창에 결과를 보여 준다.

직접 하려면 아래 순서다.

1. `content/` 또는 `static/` 의 파일을 고친다.
2. 터미널에서 빌드한다.
   ```
   python build.py
   ```
3. 미리 본다 (선택). `python -m http.server 8777 --directory docs` 실행 후 <http://localhost:8777> 접속.
4. 올린다. 1~2분 뒤 사이트에 반영된다.
   ```
   git add -A
   git commit -m "무엇을 바꿨는지 한 줄"
   git push
   ```

Claude 에게 "사이트 OO 고쳐서 올려줘" 라고 해도 위 순서대로 처리한다.

## 자주 하는 수정

| 하고 싶은 것 | 고칠 곳 |
|---|---|
| 사진 넣기·바꾸기 | `static/photo.jpg` 로 저장 (세로 4:5, 예: 1200x1500). `.png`, `.webp` 도 됨 |
| 인사말 | `content/home.html` 의 `인사말 시작` ~ `인사말 끝` 사이 |
| 논문 추가 | `content/research.html` 에서 `<article class="paper">` 블록 하나를 복사해 고치고, `home.html` 과 `cv.html` 목록에도 한 줄 추가 |
| CV 항목 추가 | `content/cv.html` 에서 `<div class="tl-row">` 한 줄 복사 |
| 이메일 변경 | `content/` 네 파일에서 찾아 바꾸기 + `build.py` 맨 위 `EMAIL` |
| 하단 "Last updated" | `build.py` 맨 위 `UPDATED` |
| 논문 그림 숫자 갱신 | 각 프로젝트 CSV 가 바뀐 뒤 `python build.py --figures` |
| 색·글꼴 | `static/site.css` 맨 위 TOKENS (라이트/다크 두 벌) |

## 그림 데이터 출처

`python build.py --figures` 는 이 폴더 옆 프로젝트 폴더에서 숫자를 읽는다.

| 그림 | 파일 |
|---|---|
| Fig. 1 (Tracing Carbon Costs) | `Pf.Jo tracing carbon costs/output/paper_figures/figure_data.csv` 의 `cond_nuc_IP` |
| Fig. 2 (Being Green) | `Pf.In_and_Park/output/20261119/data/f1_cum_emi.csv` |
| Fig. 3 (Environmental Bias) | `Pf.Choi/output/261120_figures/data/figure41.csv` |

## 검색 노출

- `build.py` 가 `docs/sitemap.xml`, `docs/robots.txt`, 페이지별 설명(meta description)과 인물 정보(JSON-LD)를 자동으로 만든다.
- Google Search Console, 네이버 서치어드바이저 소유 확인 코드는 `build.py` 맨 위 `GOOGLE_VERIFICATION`, `NAVER_VERIFICATION` 에 넣고 빌드·푸시한다.

## 디자인 원칙

- 글꼴 세 가지: Archivo (이름·제목), Newsreader (본문), IBM Plex Mono (연도·라벨·숫자).
- 악센트 색 `#1E31A8` 한 가지만 쓴다. 바탕 `#E8EAEC`.
- 장식 대신 경제학 그림(계수 플롯, 신뢰구간, 0 기준선)을 정체성으로 쓴다.
