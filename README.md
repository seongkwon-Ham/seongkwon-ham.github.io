# 개인 웹사이트 (seongkwon-ham.github.io)

공개 주소: <https://seongkwon-ham.github.io>
편집 화면: <https://seongkwon-ham.github.io/admin> (본인 GitHub 계정으로만 들어갈 수 있음)

## 고치는 방법 (셋 중 아무거나)

1. **웹 편집 화면 (가장 쉬움)**: `/admin` 에 들어가 상자에 쓰고 **저장**. 1~2분 뒤 사이트에 반영된다.
   휴대폰에서도 된다. 컴퓨터 쪽 파일은 다음에 `publish.bat` 을 돌릴 때 자동으로 맞춰진다.
2. **파일 수정 + `publish.bat`**: `content/` 의 `.yml` 파일을 메모장으로 고친 뒤 `publish.bat` 더블클릭.
3. **Claude 에게 말하기**: "사이트 OO 고쳐서 올려줘".

고친 내용이 안 보일 때: 저장 후 1~2분은 GitHub 가 사이트를 다시 만드는 시간이다. 그 뒤에는 페이지가
새 버전을 스스로 확인해서 한 번 자동으로 새로고침한다. 그래도 옛 화면이면 Ctrl+F5 를 누른다.

## 폴더 구조

```
personal-website/
├─ README.md       이 설명서
├─ publish.bat     더블클릭: 빌드 확인 → 버전 저장 → 업로드
├─ build.py        데이터 파일로 페이지를 만드는 스크립트 (맨 위에 검색 확인 코드)
├─ content/        ★ 내용 (웹 편집 화면도 이 파일들을 고친다)
│   ├─ site.yml        이름, 한글 이름, 이메일, 하단 날짜
│   ├─ home.yml        Home: 한 줄 소개, 사진, 인사말, 정보 상자
│   ├─ research.yml    Research: 논문 목록 (Home 목록과 CV 에도 자동으로 들어감)
│   ├─ cv.yml          CV: 항목 묶음, 도구, 방법론
│   └─ contact.yml     Contact
├─ static/         ★ 그대로 복사되는 파일
│   ├─ site.css        디자인 (색, 글꼴, 배치)
│   ├─ site.js         동작 (다크 모드, 스크롤 효과, 논문 그림 그리기)
│   ├─ figdata.js      논문 그림의 숫자 (build.py --figures 가 만듦)
│   └─ (사진)          편집 화면에서 올린 사진이 여기에 저장된다
├─ admin/          웹 편집 화면 설정 (config.yml: 어떤 칸을 보여 줄지)
├─ .github/        GitHub 가 저장할 때마다 사이트를 다시 만드는 설정
└─ docs/           미리보기용 결과물. GitHub 에는 올라가지 않는다
```

## 글쓰기 규칙 (모든 글 칸 공통)

| 쓰는 법 | 결과 |
|---|---|
| `*글자*` | 기울임 (한 줄 소개에서는 파란 기울임) |
| `**글자**` | 굵게 |
| `[글자](https://주소)` | 링크 |
| 빈 줄 하나 | 새 문단 (인사말, 초록) |

## 자주 하는 수정

| 하고 싶은 것 | 웹 편집 화면에서 |
|---|---|
| 사진 넣기·바꾸기 | 페이지 → Home → 사진 (세로 4:5 권장) |
| 인사말 | 페이지 → Home → 인사말 |
| 논문 추가 | 페이지 → Research → 논문 → 추가. Home 과 CV 에도 자동으로 들어간다 |
| CV 항목 추가 | 페이지 → CV → 해당 묶음 → 항목 → 추가 |
| 이메일 변경 | 페이지 → 사이트 설정 → 이메일 (모든 페이지에 한 번에 반영) |
| 하단 "Last updated" | 페이지 → 사이트 설정 |

편집 화면에서 못 하는 것: 논문 그림의 숫자 갱신, 디자인 변경. 이 둘은 Claude 에게 맡긴다.

## 웹 편집 화면 로그인

처음 한 번 GitHub 에서 "개인 접근 토큰"(fine-grained personal access token)을 만들어 붙여 넣는다.

1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token
2. Repository access: Only select repositories → `seongkwon-ham.github.io`
3. Permissions → Contents: **Read and write**
4. 만든 토큰을 `/admin` 의 **Sign In Using Access Token** 에 붙여 넣는다.

토큰은 비밀번호와 같다. 남에게 보여 주지 않는다. 기한이 끝나면 같은 방법으로 새로 만든다.

## 그림 데이터 출처

`python build.py --figures` 는 이 폴더 옆 프로젝트 폴더에서 숫자를 읽는다 (이 컴퓨터에서만 된다).

| 그림 | 파일 |
|---|---|
| Tracing Carbon Costs | `Pf.Jo tracing carbon costs/output/paper_figures/figure_data.csv` 의 `cond_nuc_IP` |
| Being Green | `Pf.In_and_Park/output/20261119/data/f1_cum_emi.csv` |
| Environmental Bias | `Pf.Choi/output/261120_figures/data/figure41.csv` |

## 검색 노출

- Google Search Console, 네이버 서치어드바이저에 등록되어 있다 (2026-11-22).
- 소유 확인 코드는 `build.py` 맨 위 `GOOGLE_VERIFICATION`, `NAVER_VERIFICATION`. **지우면 소유 확인이 풀린다.**
- `sitemap.xml`, `robots.txt`, 인물 정보(JSON-LD)는 `build.py` 가 자동으로 만든다.

## 디자인 원칙

- 글꼴 세 가지: Archivo (이름·제목), Newsreader (본문), IBM Plex Mono (연도·라벨·숫자).
- 악센트 색 `#1E31A8` 한 가지만 쓴다. 바탕 `#E8EAEC`.
- 장식 대신 경제학 그림(계수 플롯, 신뢰구간, 0 기준선)을 정체성으로 쓴다.
