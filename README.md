# bonakim-itm29.github.io

김보나의 개인 사이트입니다. GitHub Pages로 운영하며, 주소는 https://bonakim-itm29.github.io 입니다.

## 폴더 구조

```
index.html                 메인 페이지
assets/style.css           하위 페이지 공통 디자인
courses/                   대학원 과목 (KAIST I&TM)
  index.html               과목 목록
  <과목>/index.html        과목 소개 + 과제 목록
  <과목>/<과제>/index.html 과제 페이지
macro-notes/               매크로 투자노트
  index.html
  companies/<기업>/index.html
  columns/index.html       fruiting 칼럼
```

## 과목 폴더 이름

| 폴더 | 과목 |
|---|---|
| ai-management-law | 인공지능 경영과 법 |
| tm-case-research-methods | 기술경영사례 연구방법론 |
| finance-accounting-for-tm | 기술경영을 위한 재무와 회계 |
| entrepreneurship | 기업가 정신 |
| climate-tech-net-zero | 기후기술과 탄소중립경영 |
| innovation-management | 이노베이션 경영 |
| semiconductor-innovation | 첨단기술 특수논제 · 반도체산업혁신론 |

## 새 과제 추가하는 법

1. `courses/<과목>/` 안에 과제 폴더를 만들고(영문 소문자·하이픈), 과제 html을 `index.html`로 넣습니다.
2. `courses/<과목>/index.html`의 "과제 목록" 부분에 카드(`<a class="card" ...>`) 하나를 추가합니다.
3. `courses/index.html`의 해당 과목 카드 태그를 "과제 N건"으로 바꿉니다.

## 규칙

- 폴더·파일 이름은 영문 소문자와 하이픈(`-`)만 씁니다. 화면에 보이는 제목은 한글로 씁니다.
- 원본 데이터, 내부 자료, 작업 파일은 이 저장소에 넣지 않습니다.
