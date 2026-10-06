# 주가 급변동 이벤트 확인 지침 (홍콩 상장)

대상 {TICKER} (HK 종목코드 {HK}). HKEX 원본 공시: /mnt/user-data/outputs/fruiting/hk/raw_events/ 의 `{PREFIX}__*` (PDF/HTM) 와 /mnt/user-data/outputs/fruiting/hk/raw/ .
급변동 목록: /mnt/user-data/outputs/fruiting/hk/data/moves.json 의 ["{HK}"] → events (일간 급변동. R=당일 수익률(홍콩달러), fit=매크로 모델 예측(미국 지표는 전일 미국장 기준), res=잔차, type=비매크로/혼합/중국 공통 충격/매크로 충격, filings=±3일 HKEX 공시).
HKEX 공시 제목 전체 목록: /mnt/user-data/outputs/fruiting/hk/data/hk_hist.json 의 ["{HK}"].rows

## 할 일
1. filings가 있는 급변동은 raw_events의 원문 PDF/HTM을 페이지·문단 단위로 읽고(pdftotext -layout 페이지별, HTM은 BeautifulSoup), 무엇을 발표했는지 확인한다. 숫자는 표의 행·열이 분명하거나 한 문장 안에 온전히 있을 때만 인용.
2. 이 회사의 "매크로로 설명되지 않은 가장 중요한 이벤트" 1~2개를 골라라. 기준: |잔차|가 크고 회사의 방향을 바꾼 사건(규제, 실적 쇼크, 주주환원, 경쟁 격화, 구조 변경). type이 "중국 공통 충격"인 날은 제외.
3. filings가 없는 급변동 가운데 |잔차|가 매우 큰 1~2건은 WebSearch/WebFetch로 원인을 확인해도 된다. 단, 실제로 열어 본(WebFetch) 신뢰할 만한 출처(규제기관 원문, Reuters/Bloomberg/CNBC/FT/Caixin/SCMP 등)의 URL과 짧은 영문 인용(15단어 이내)이 있어야 하고, 날짜가 주가 반응일과 맞아야 한다. 확인 못 하면 "공시 없음·원인 미확인"으로 남겨라. 추정 금지.
4. 나머지 filings 있는 급변동은 others에 한 줄씩.

## 금지
- 원문에 없는 사실을 기억으로 보충하지 마라. 모든 사실은 파일명 또는 URL + 원문 인용(영문 15단어 이내)으로 뒷받침.
- 날짜·금액이 모호하면 "모호"로 표시.

## 출력
`/mnt/user-data/outputs/fruiting/hk/events_{PREFIX}.json`:
```json
{"ticker":"{HK}","top":[{"date":"주가 반응일","filed":"공시일 또는 보도일","title_ko":"짧은 제목","summary_ko":"2~3문장. 무엇이 발표됐고 주가가 어떻게 반응했는지(수익률, 매크로 예측, 잔차를 %로. 변수명 R/fit/res는 쓰지 말 것)","why_important_ko":"","facts":[{"fact_ko":"","quote":"","file":"파일명 또는 URL"}]}],
 "others":[{"date":"","filed":"","title_ko":"","R":0,"res":0,"file":""}],
 "no_filing_moves":[{"date":"","R":0,"res":0}]}
```
JSON 파싱 확인 후 120단어 이내로 요약 보고(한국어).
