# 홍콩 상장 인터넷 기업 공시 추출 지침 ({TICKER}, 실행 {RUN})

원본 파일: /mnt/user-data/outputs/fruiting/hk/raw/ 의 `{PREFIX}__*.pdf` (HKEX 원본 PDF).
- 최신 분기 실적발표: `{PREFIX}__results_2026Q2__*.pdf` (2026년 6월 말 분기·반기)
- 직전 분기: `{PREFIX}__results_2026Q1__*.pdf`
- 연간 실적발표: `{PREFIX}__results_FY2025__*.pdf`, 연차보고서: `{PREFIX}__AR2025__*.pdf` (5개년 재무요약 표가 있음)
다른 실행 결과 파일(extract_*_*.json)과 data/ 폴더는 열지 마라 — 독립 추출이다.

## 절대 규칙
1. PDF를 한 덩어리 평문으로 바꿔 정규식으로 숫자를 줍지 마라. pdfplumber로 해당 페이지의 표 구조(행 라벨, 열 머리 = 기간, 단위 캡션 "RMB million" 등)를 유지해 읽어라. 표 추출이 깨지면 `pdftotext -layout -f N -l N` 로 그 페이지만 열 정렬을 유지해 읽고, 열과 기간의 대응을 눈으로 확인하라.
2. 줄바꿈·공백 깨짐으로 어떤 숫자가 어느 행/기간에 속하는지 모호하면 status=ambiguous + 이유. 절대 추정하지 마라.
3. 괄호 숫자 (1,234) = 음수. 단위(RMB million / thousand, HK$)를 확인하고 RMB millions로 통일(변환 시 note).
4. 모든 값에 출처(파일명, 페이지 번호, 원문 행 라벨, 원문 열 머리, 단위).

## 추출 항목
최신 분기(3개월, 2026-04-01~06-30). 같은 표에 전년 동기·직전 분기 값이 있으면 period를 구분해 함께:
- Q1 총매출 / Q2 부문별 매출(회사 부문명 그대로, 각각 Q2_부문명) / Q3 영업이익(Operating profit/loss, IFRS)
- Q4 회사 제시 조정 이익: Non-IFRS operating profit(텐센트) 또는 Adjusted EBITDA와 부문별 operating profit(메이퇀) — 명칭 그대로
- Q5 지배주주 귀속 순이익(IFRS) / Q6 Non-IFRS(Adjusted) 순이익(명칭 그대로)
- Q7 주당 희석 EPS(IFRS·Non-IFRS, 통화 명시) / Q8 영업활동 현금흐름 / Q9 회사 제시 Free cash flow(정의 문구) / Q10 설비투자(capex, 회사 제시 값)
반기(1~6월) 누계가 표에 있으면 H1_매출, H1_귀속순이익도.
재무상태(2026-06-30):
- B1 현금및현금성자산 / B2 정기예금·단기 금융투자 등 현금성 항목(행 이름 그대로 각각) / B3 차입 항목(borrowings 유동·비유동, notes payable, convertible bonds 각각) / B4 회사가 제시한 net cash(있으면, 정의 포함) / B5 총자산 / B6 총자본과 지배주주지분
주식·주주환원:
- S1 발행 주식 수(기준일, 텐센트는 보통주, 메이퇀은 Class A+B 합계와 각각) / S2 분기 희석 가중평균 주식 수
- R1 분기(또는 반기) 자사주 매입 주식 수·금액(HK$)과 남은 계획 / R2 최근 배당(주당, HK$, 연간/특별 구분, 지급 총액)
연간(연간 실적발표 또는 연차보고서, 2025 회계연도; 5개년 요약이 있으면 2021~2025 모두):
- A1 총매출 / A2 귀속 순이익 / A3 영업활동 현금흐름 / A4 설비투자 / A5 Non-IFRS(Adjusted) 순이익
- X1 보고통화와 HK$ 환산 등 환율 문구(있으면)

## 출력
`/mnt/user-data/outputs/fruiting/hk/extract_{TICKER}_{RUN}.json`:
{"ticker":"","items":[{"id":"Q1","period":"","value":0,"raw":"","unit":"RMB millions","status":"ok|ambiguous|null","source":{"file":"","page":0,"row":"","col":""},"note":""}]}
5개년 항목은 id를 A1_2021 … A1_2025처럼. python으로 파싱 확인 후 100단어 이내 한국어 보고: ok/ambiguous/null 수, 모호 항목 이유.
