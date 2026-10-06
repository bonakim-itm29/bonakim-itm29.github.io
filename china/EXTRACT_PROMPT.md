# 중국 인터넷 기업 공시 추출 지침 ({TICKER}, 실행 {RUN})

원본 파일: /mnt/user-data/outputs/fruiting/china/raw/ 의 `{TICKER}__*` (SEC 원본 HTML). 최신 분기 실적발표문은 {QREL}, 직전 분기 실적발표문은 {PREL}, 연간 보고서는 `{TICKER}__20-F__*`.
다른 실행 결과 파일(extract_*_*.json)과 data/ 폴더는 열지 마라 — 독립 추출이다.

## 절대 규칙
1. HTML을 평문으로 바꿔 정규식으로 숫자를 줍지 마라. BeautifulSoup(lxml)/pandas.read_html로 `<table>`의 tr/td 구조, 열 머리(기간·통화), 단위 캡션("in millions", "RMB", "US$")을 유지해 읽어라. 표 밖 수치는 한 문단 안에 온전히 있을 때만 인용.
2. 통화 구분 필수: 표에 RMB 열과 US$ 편의환산 열이 같이 있으면 **RMB 값**을 기록하고, 편의환산 환율(RMB per US$1)은 따로 기록.
3. 모든 값에 출처(파일명, 표 번호, 원문 행 라벨, 원문 열 머리, 단위)를 붙여라. 모호하면(기간·통화·단위 불분명, 같은 항목 두 값) status=ambiguous + 이유, 추정 금지.
4. 금액은 RMB millions로 통일(원문이 RMB 천 단위면 변환하고 note). 주식 수는 원문 단위 그대로.

## 추출 항목
최신 분기(3개월, 실적발표문 기준 — 기간을 period에 정확히):
- Q1 총매출 / Q2 주요 부문별 매출(회사 부문명 그대로, 목록) / Q3 영업이익(Income from operations)
- Q4 회사 제시 조정 이익: Adjusted EBITA(알리바바) 또는 Non-GAAP operating income(바이두·JD) — 명칭 그대로
- Q5 보통주주 귀속 순이익(GAAP) / Q6 Non-GAAP 귀속 순이익
- Q7 ADS당 희석 EPS(GAAP, Non-GAAP) — 통화 명시
- Q8 영업활동 현금흐름 / Q9 회사 제시 Free cash flow(정의 문구 한 줄) / Q10 설비투자(유형자산 등 취득, 표에 있으면)
- 같은 항목의 직전 분기·전년 동기 값이 같은 표에 있으면 함께(period 구분)
재무상태(분기말):
- B1 현금및현금성자산 / B2 단기투자·정기예금·제한현금 등 현금성 항목(행 이름 그대로, 각각) / B3 차입 항목(단기차입, 장기차입, 선순위채, 전환사채 등 각각) / B4 회사가 문장으로 제시한 순현금(있으면) / B5 총자산 / B6 총자본(비지배 포함)과 주주지분
주식·주주환원:
- S1 발행 보통주 수와 기준일, ADS 1주당 보통주 비율 / S2 분기 희석 가중평균 ADS 수(있으면)
- R1 분기 자사주 매입(금액·수량)과 잔여 한도 / R2 최근 선언된 배당(ADS당, 연간/특별 구분)
연간(20-F 최근 회계연도, 연결손익·현금흐름표):
- A1 총매출 / A2 보통주주 귀속 순이익 / A3 영업활동 현금흐름 / A4 설비투자(현금흐름표 행 이름 그대로)
- X1 편의환산 환율(RMB per US$1과 기준일)

## 출력
`/mnt/user-data/outputs/fruiting/china/extract_{TICKER}_{RUN}.json`:
{"ticker":"","items":[{"id":"Q1","period":"","value":0,"raw":"","unit":"RMB millions","status":"ok|ambiguous|null","source":{"file":"","table":0,"row":"","col":""},"note":""}]}
(목록형 항목은 id를 Q2_부문명, B2_행이름처럼 나눠서 여러 개로.) python으로 파싱 확인 후 100단어 이내 한국어 보고: ok/ambiguous/null 수, 모호 항목 이유.
