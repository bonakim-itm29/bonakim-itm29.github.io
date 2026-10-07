# 주가 급변동 이벤트 확인 지침 (브라질 ADR)

대상 {T} (moves 키 "{K}"). SEC 원본 공시(6-K HTM): /mnt/user-data/outputs/fruiting/br/raw_events/ 의 `{K}__*` 파일(파일명 = 키__접수번호__원문파일명). 최근 실적 원문은 /mnt/user-data/outputs/fruiting/br/raw/{T}/ 에도 있다.
급변동 목록: /mnt/user-data/outputs/fruiting/br/data/moves.json 의 ["{K}"] → events (일간 급변동. R=당일 수익률(미국 달러 ADR 기준, AXIA3.SA만 헤알 원주), fit=매크로 모델 예측, res=잔차, type=비매크로/혼합/브라질 공통 충격/매크로, filings=±3일 SEC 공시 링크 — doc URL의 마지막 두 부분이 raw_events 파일명의 접수번호·파일명).
SEC 공시 전체 목록: /mnt/user-data/outputs/fruiting/br/data/hk_hist.json 의 ["{K}"].rows

## 할 일
1. filings가 있는 비매크로·혼합 급변동 중 |잔차| 상위 4건은 raw_events의 원문 HTM을 BeautifulSoup으로 문단·표 단위로 읽고(평문 정규식 금지), 무엇을 발표했는지 확인한다. 숫자는 표의 행·열이 분명하거나 한 문장 안에 온전히 있을 때만 인용.
2. 이 회사의 "매크로로 설명되지 않은 가장 중요한 이벤트" 1~2개를 골라라. 기준: |잔차|가 크고 회사의 방향을 바꾼 사건(사고·소송, 실적 쇼크, 정부·규제 개입, 요금·가격 정책, 민영화·지배구조 변경, 인수합병, 주주환원). type이 "브라질 공통 충격"·"매크로"인 날은 제외.
3. filings가 없는 급변동 가운데 |잔차|가 매우 큰 1~2건은 WebSearch로 찾고 WebFetch로 열어 원인을 확인해도 된다. 실제로 열어 본 신뢰할 만한 출처(규제기관·회사 원문, Reuters/Bloomberg/CNBC/FT/AP/Valor 등)의 URL과 짧은 영문 인용(15단어 이내)이 있어야 하고, 날짜가 주가 반응일과 맞아야 한다. 확인 못 하면 "공시 없음·원인 미확인"으로 남겨라. 추정 금지.
4. 나머지 filings 있는 급변동은 others에 한 줄씩.

## 금지
- 원문에 없는 사실을 기억으로 보충하지 마라. 모든 사실은 파일명 또는 URL + 원문 인용(영문 또는 포르투갈어 원문 15단어 이내)으로 뒷받침.
- 날짜·금액이 모호하면 "모호"로 표시. sec.gov는 이 환경에서 접근이 막혀 있으니 WebFetch로 sec.gov를 열지 마라(로컬 파일 사용).

## 출력
`/mnt/user-data/outputs/fruiting/br/events_{T}.json`:
```json
{"ticker":"{T}","top":[{"date":"주가 반응일","filed":"공시일 또는 보도일","title_ko":"짧은 제목","summary_ko":"2~3문장. 무엇이 발표됐고 주가가 어떻게 반응했는지(수익률, 매크로 예측, 잔차를 %로. 변수명 R/fit/res는 쓰지 말 것)","why_important_ko":"","facts":[{"fact_ko":"","quote":"","file":"파일명 또는 URL"}]}],
 "others":[{"date":"","filed":"","title_ko":"","R":0,"res":0,"file":""}],
 "no_filing_moves":[{"date":"","R":0,"res":0,"cause_ko":"확인된 원인 또는 '원인 미확인'","url":""}]}
```
JSON 파싱 확인 후 120단어 이내로 요약 보고(한국어).
