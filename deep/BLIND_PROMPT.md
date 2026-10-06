# 독립 재추출 (blind) 지침

대상: {TICKER}. 원본 SEC 파일은 /mnt/user-data/outputs/fruiting/valuation/raw/ 에서 `{TICKER}__` 로 시작하는 파일들이다(SEC 원본 HTML).

**금지**: /mnt/user-data/outputs/fruiting/valuation/ 의 extract_*.json, valuation_metrics.json, *.html, xbrl_*.json 파일을 열지 마라. 이 작업은 기존 추출과 독립적으로 수행되어야 한다(나중에 대조함).

## 읽는 방법 (절대 규칙)
1. HTML을 평문으로 바꿔 정규식으로 숫자를 줍지 마라. BeautifulSoup(lxml) 또는 pandas.read_html로 `<table>`의 tr/td 구조를 유지해 행 라벨과 열 헤더(기간)를 함께 확인한다.
2. 10-Q/10-K는 인라인 XBRL이다. 가능하면 `ix:nonFraction`의 name, contextRef, scale, sign 속성과 `ix:context`의 기간을 이용해 값을 얻고, 같은 값을 표의 행/열로도 확인하라. 두 경로가 모두 되면 source에 둘 다 적는다.
3. 기간·항목·단위가 모호하면 값을 쓰지 말고 ambiguous로 표시하고 이유를 적는다. 추정 금지.
4. 음수 "(1,234)" → -1234. 표 머리 단위("in thousands", "in millions")를 반드시 확인하고 **최종 value는 백만 달러(USD millions)** 로, 물량은 원문 단위 그대로 + unit에 명시.

## 추출 항목 (id: 설명)
기간은 따로 적지 않으면 2026-06-30 종료 분기(10-Q).
- F1: Total revenues (또는 회사의 총매출 행), 3개월(2026-04-01~06-30)
- F2: 회사 귀속 순이익(Net income attributable to the company; 없으면 Net income), 3개월
- F3: 같은 항목, 6개월(2026-01-01~06-30)
- F4: Net cash provided by operating activities, 6개월
- F5: Cash and cash equivalents, 2026-06-30
- F6: Total assets, 2026-06-30
- F7: Total liabilities, 2026-06-30 (재무상태표에 합계 행이 없으면 ambiguous가 아니라 null + note)
- F8: Total equity(비지배지분 포함 합계 행) 와 회사 주주지분 합계 행 — 둘 다 있으면 둘 다
- F9: Long-term debt 장부가(유동+비유동 합계; 재무상태표 또는 부채 주석 합계 행), 2026-06-30
- F10: 표지(cover page)의 발행주식 수와 그 기준일 (Class 구분이 있으면 각각)
- O1: 2분기 총 생산량(일평균, Boe/d 또는 MBoe/d) — 생산 기준인지 판매 기준인지 note
- O2: 2분기 원유 생산량(일평균)
- O3: 2분기 원유 실현가격, 헤지 효과 제외($/Bbl)
- O4: 2분기 LOE(lease operating expense) $/Boe
- O5: 2분기 회사 제시 Adjusted EBITDAX(또는 Adjusted EBITDA) — 8-K 실적발표문(Ex.99.1 등)에서
- O6: 2분기 회사 제시 Free cash flow(명칭 그대로 기록) — 실적발표문
- O7: 회사 제시 Net debt(2026-06-30), 없으면 null + note
- O8: 2026년 하반기(7~12월) 원유 헤지 총량(Bbl)과 스왑 가중평균가격 — 10-Q 헤지 표 기준. 표의 기간 구분이 2026년 하반기로 확정되지 않으면 ambiguous
- R1: 2025-12-31 증명매장량 합계(MMBoe)
- R2: 증명개발(proved developed) 비중(%) 또는 PD 물량
- R3: Standardized measure of discounted future net cash flows, 2025-12-31
- R4: PV-10(회사 제시한 경우), 2025-12-31
- R5: 매장량 평가에 쓰인 SEC 가격(원유 $/Bbl, 가스 $/MMBtu)

## 출력
`/mnt/user-data/outputs/fruiting/deep/blind_{TICKER}.json`:
```json
{"ticker":"","items":[{"id":"F1","value":0,"raw":"","unit":"USD millions","period":"","status":"ok|ambiguous|null","source":{"file":"","method":"ixbrl|table|both","ix_name":"","contextRef":"","table":0,"row":"","col":""},"note":""}]}
```
python으로 JSON 파싱 확인 후, 150단어 이내로: ok/ambiguous/null 개수, ambiguous 항목과 이유 한 줄씩.
