# 관심기업 실적 반영 런북 (company-pipeline 브랜치)

이 브랜치는 macro-notes/companies 기업 페이지를 만든 파이프라인의 스냅샷입니다. 원본 공시 파일(raw/, raw_events/)은 빼 두었으니 실적 반영 때 새로 받습니다.
사이트(main 브랜치)는 GitHub Pages로 공개됩니다. 이 브랜치는 Pages에 올라가지 않습니다.

## 0. 준비
```bash
git clone https://github.com/bonakim-itm29/bonakim-itm29.github.io /home/claude/bonakim-itm29.github.io   # main (사이트)
git -C /home/claude/bonakim-itm29.github.io fetch origin company-pipeline
mkdir -p /mnt/user-data/outputs/fruiting
git -C /home/claude/bonakim-itm29.github.io archive origin/company-pipeline | tar -x -C /mnt/user-data/outputs/fruiting
```
스크립트는 각 폴더 안에서 상대경로로 실행하고, 결과 페이지를 `/home/claude/bonakim-itm29.github.io/macro-notes/companies/<slug>/index.html`에 씁니다.

| 폴더 | 기업(slug) | 공시 출처 | 순서 |
|---|---|---|---|
| deep | crescent-energy, kosmos-energy, sm-energy | SEC 10-Q/8-K | load.py → build_data.py → score.py → nav_scen.py → mult_scen.py → content.py → gen_pages.py |
| china | alibaba, baidu, jd | SEC 6-K 실적발표문, 20-F | 추출(EXTRACT_PROMPT A/B) → verify_cn.py → valuation_cn.py → content_cn.py → gen_cn.py |
| china2 | pdd, netease, trip-com | SEC 6-K, 20-F | 추출 A/B → verify_cn2.py → valuation_cn2.py → build_cn2.py → content_cn2.py → gen_cn2.py |
| hk | tencent, meituan | HKEX 실적발표(PDF) | 추출 A/B → verify_hk.py → valuation_hk.py → build_hk.py → content_hk.py → gen_hk.py |
| hk3 | lenovo, xiaomi, byd | HKEX 실적발표·연차보고서(PDF, 레노버 US$·3월 결산, BYD 중국회계기준) | 추출 A/B(EXTRACT_PROMPT.md) → verify_hk3.py → eda_hk3.py → moves_hk3.py → 이벤트(EVENT_PROMPT_HK3.md) → valuation_hk3.py → build_hk3.py → content_hk3.py 수정 → gen_hk3.py |
| kr | samsung-electronics, sk-hynix | DART 분기보고서·잠정실적 | 추출 A/B → verify_kr.py → valuation_kr.py → build_kr.py → content_kr.py → gen_kr.py |

각 스크립트를 열어 실제 입력 파일과 기준일(ASOF) 상수를 확인한 뒤 실행합니다. 순서가 표와 다르면 스크립트가 읽는 파일 기준으로 맞춥니다.

## 1. 공시 받기
- SEC는 클라우드에서 403이 납니다. 사용자 PC의 내장 브라우저(선호 브라우저)로 EDGAR에 접속해 JS fetch → blob 다운로드 → Downloads → device_stage_files로 가져옵니다. 큰 파일은 나눠서 받습니다.
- SEC 요청 헤더에 사용자 이메일을 절대 넣지 않습니다.
- **원본 HTML/PDF 그대로 읽습니다. 텍스트로 변환하지 않습니다.** 표 구조(tr/td, 열 머리, 단위)를 유지해 읽습니다.
- 숫자의 소속 항목·기간이 줄바꿈·공백 깨짐으로 모호하면 **추정 계산 금지**. status=ambiguous로 두고 사용자에게 해당 부분 확인을 요청합니다(무인 실행이면 그 기업은 게시하지 않고 알림만).
- 받은 파일은 해당 폴더 raw/에 기존 파일명 규칙(`{TICKER}__{FORM}__{날짜}...`)으로 둡니다. 작업이 끝나면 PC Downloads에서 Claude가 받은 파일만 정리합니다.

## 2. 추출·검증
- EXTRACT_PROMPT.md(폴더별)로 서로 독립인 두 번 추출(A/B)을 별도 에이전트로 돌리고, verify 스크립트로 A·B·XBRL을 대조합니다. 불일치는 원문으로 다시 확인합니다.
- 프레임워크 적합도 기둥(칼럼 기반)은 실적과 무관하므로 기존 값을 유지합니다. 프루츠 칼럼 원문·새 칼럼(442번 이후)의 제목·인용·번호는 공개 페이지에 넣지 않습니다.

## 3. 페이지 갱신
- valuation → content → gen 순으로 다시 만듭니다. content의 서술은 새 분기 숫자에 맞게 고쳐 씁니다(이선철 대표 1인칭 금지, 투자 권유 금지, 목표주가 표현 금지).
- 이후 main 저장소에서:
```bash
python3 scripts/build_company_base.py     # 주가 연동 기준값 갱신 (live-price.js가 사용)
python3 scripts/build_notes_index.py      # 투자노트 목록 점수 배지
```
- `macro-notes/companies/earnings.json`: 해당 기업 `reflected_period`를 새 분기로, `date`/`status`를 다음 분기 예상일로 고칩니다.
- Playwright(Chromium 내장, `playwright install` 금지)로 페이지를 열어 오류·레이아웃(390px 폭 포함)을 확인합니다.
- 숫자는 원문과 한 번 더 대조(가능하면 작업을 보지 않은 별도 에이전트로)한 뒤 커밋·푸시합니다. 커밋 메시지 끝에 세션 지시의 attribution 줄을 붙입니다.
- 이 브랜치의 data/ 등 파이프라인 변경분도 company-pipeline 브랜치에 커밋해 둡니다(raw/는 제외).

## 4. 알림
사용자에게 한국어로: 반영한 기업·분기, 점수 변화(전→후)와 주된 이유, 모호해서 확인이 필요한 수치. 투자 권유가 아님을 밝힙니다.

## 5. 중국·홍콩 프레임워크 v1.1 (2026-10-07)
- 프레임워크 적합도: 중국/홍콩 강세 1.5 + 종목 거명 0.25~0.5 + 위안화 베타 0.5 + **미국 실질금리 베타 0.5**(hk3/framework_v11.py, rr_beta.py).
- 실질금리 베타: 2021년 이후 월간(4주) 수익률을 미 10년 TIPS 금리(FRED DFII10) 변화에 단순회귀, −0.20 이하 만점.
- 기존 중국 8개 페이지는 hk3/patch_pages.py로 점수·peers를 갱신했습니다. 새 기업을 추가하면 run_peers로 모든 중국 페이지의 peers를 다시 맞춥니다.
- 각 페이지 실적 갱신 시 위 규칙을 그대로 적용합니다(파이프라인의 valuation 스크립트에서 위안화 항목 대신 framework_v11.items 사용).
