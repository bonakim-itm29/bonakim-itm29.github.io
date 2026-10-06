# 주가 급변동 이벤트 확인 지침

대상 {TICKER}. SEC 원본 HTML: /mnt/user-data/outputs/fruiting/china2/raw_events/ 및 /mnt/user-data/outputs/fruiting/china2/raw/ 의 `{TICKER}__*` 파일 .
급변동 목록: /mnt/user-data/outputs/fruiting/china2/data/moves.json 의 [{TICKER}] → events(일간 급변동; type=비매크로/혼합이 매크로로 설명되지 않은 것) 와 corp(중요 8-K 공시일의 주가 반응; R=당일 수익률, fit=매크로 모델 예측, res=잔차).

## 할 일
1. raw_events의 각 공시가 무엇을 발표했는지 확인한다. 6-K 표지 + Ex.99 보도자료·공시 첫 부분(헤드라인·요약 bullet)을 BeautifulSoup으로 문단 단위로 읽어라. 표의 숫자는 tr/td 구조로, 문장의 숫자는 한 문단(<p>/<div>) 안에 온전히 있을 때만 인용.
2. 각 공시를 moves.json의 해당 날짜 주가 반응(R, fit, res)과 짝지어라.
3. 이 회사의 "매크로로 설명되지 않은 가장 중요한 이벤트" 1~2개를 골라라. 기준: |잔차|가 크고, 회사의 방향을 바꾼 사건(규제 조사, 구조조정·분사, 증자, 실적 쇼크, 상장 구조 변경 등). type이 "중국 공통 충격"인 날은 회사 고유 사건이 아니므로 top에서 제외. 선정 이유를 한 줄로.
4. 공시가 없는 큰 급변동(filings 빈 목록)은 원인을 추정하지 말고 "공시 없음"으로 남겨라.

## 금지
- 원문에 없는 사실을 기억으로 보충하지 마라. 모든 사실은 파일명 + 원문 인용(영문 15단어 이내)으로 뒷받침.
- 날짜·금액이 모호하면 "모호"로 표시.

## 출력
`/mnt/user-data/outputs/fruiting/china2/events_{TICKER}.json`:
```json
{"ticker":"","top":[{"date":"주가 반응일","filed":"","title_ko":"짧은 제목","summary_ko":"2~3문장. 무엇을 발표했고 주가가 어떻게 반응했는지(R, 매크로 예측 fit, 잔차 res를 % 로)","why_important_ko":"","facts":[{"fact_ko":"","quote":"","file":""}]}],
 "others":[{"date":"","filed":"","title_ko":"","R":0,"res":0,"file":""}],
 "no_filing_moves":[{"date":"","R":0,"res":0}]}
```
JSON 파싱 확인 후 120단어 이내로 요약 보고(한국어).
