# Standardized Measure 구성요소 추출 지침

대상 {TICKER}. 파일: /mnt/user-data/outputs/fruiting/valuation/raw/{TICKER}__10-K__*.htm (2025-12-31 연차보고서, SEC 원본 HTML, 인라인 XBRL 포함). {EXTRA}

## 절대 규칙
1. HTML을 평문으로 바꿔 정규식으로 숫자를 줍지 마라. BeautifulSoup(lxml)/pandas.read_html로 `<table>`의 tr/td 구조와 열 머리(기간)를 유지해 읽어라. 가능하면 `ix:nonFraction`(name, contextRef, scale, sign)과 `ix:context`의 기간·dimension도 확인해 표 값과 대조(method=both). 표 밖 수치는 한 문단(<p>/<div>) 안에 온전히 있을 때만.
2. 모든 값에 출처(파일, 표 번호, 원문 행 라벨, 원문 열 머리, 단위 캡션, ix name/contextRef 있으면)를 붙여라.
3. 모호하면(열 기간 불분명, 부문 합계인지 불분명, 단위 캡션 없음, 같은 항목 두 값) 값을 쓰지 말고 status=ambiguous + 이유.
4. 최종 금액은 USD millions, 물량은 원문 단위 그대로 + unit 명시. 음수 "(1,234)" → -1234.
5. 다른 추출 파일(extract_*.json, valuation_metrics.json, deep/data/*)은 열지 마라.

## 추출 항목 (2025-12-31 기준, 회사 전체 합계 행)
- S1 Future cash inflows
- S2 Future production costs (생산세·운영비 포함 여부 note)
- S3 Future development costs (폐쇄·복구 비용이 별도 행이면 S3b로 따로)
- S4 Future income tax expense
- S5 Future net cash flows (할인 전)
- S6 10% annual discount for estimated timing of cash flows
- S7 Standardized measure of discounted future net cash flows
- S8 PV-10 (세전, 회사가 제시한 경우)
- P1 매장량 평가 SEC 기준가: 원유 기준(WTI 또는 Brent) $/Bbl, 가스 Henry Hub $/MMBtu
- P2 조정 후 평균 실현가격(회사가 제시한 경우): 원유 $/Bbl, NGL $/Bbl, 가스 $/Mcf
- V1 증명매장량 합계의 제품별 물량: 원유(또는 원유+콘덴세이트) MMBbl, NGL MMBbl, 가스 Bcf (원유와 NGL을 합쳐 공시하면 그대로 기록 + note)
- CHK: S1과 (V1×P2 합) 의 비교 (P2가 있을 때만; 차이 %). S5 = S1+S2+S3(+S3b)+S4, S7 = S5+S6 합계 검증 결과.

## 출력
`/mnt/user-data/outputs/fruiting/deep/std_{TICKER}.json`:
{"ticker":"","items":[{"id":"S1","value":0,"raw":"","unit":"","status":"ok|ambiguous|null","source":{...},"note":""}],"checks":[{"name":"","lhs":0,"rhs":0,"ok":true}]{EXTRAOUT}}
python으로 파싱 확인 후, 120단어 이내 한국어 보고: ok/ambiguous/null 수, 모호 항목 이유, 합계 검증 결과.
