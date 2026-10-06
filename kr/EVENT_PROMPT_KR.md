# 주가 급변동 이벤트 확인 지침 (한국 상장)

대상 {NAME} ({TK}). 급변동 목록: /mnt/user-data/outputs/fruiting/kr/data/moves.json 의 ["{TK}"] → events (일간 급변동. R=당일 수익률, fit=매크로 모델 예측(미국 지표는 전날 미국장 기준), res=잔차, type=비매크로/혼합/시장·업종 공통 충격/매크로 충격, filings=±3일 KRX KIND 공시 제목과 접수번호 acc).
전체 공시 제목 목록: /mnt/user-data/outputs/fruiting/kr/data/kr_hist.json 의 ["{TK}"].rows (filed, time, title, acpt).

## 할 일
1. type이 비매크로/혼합인 급변동 중 |잔차|가 큰 것부터, 원인을 확인한다.
   - 공시가 있으면 공시 원문을 확인한다. 원문은 DART 공시뷰어(https://dart.fss.or.kr/dsaf001/main.do?rcpNo=<acpt>; KIND 접수번호와 DART 접수번호가 다를 수 있음) 또는 KIND(https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=<acpt>)를 WebFetch로 열어 본다. 열리지 않으면 공시 제목·일시(목록에 있는 1차 자료)만 인용하고 내용은 신뢰할 만한 언론 보도(연합뉴스, 한국경제, 매일경제, 조선비즈, Reuters, Bloomberg, CNBC 등)를 WebFetch로 실제로 열어 확인한다.
   - 공시가 없으면 같은 날짜(또는 전날 저녁) 보도를 WebSearch → WebFetch로 확인한다. 확인 못 하면 "원인 미확인".
2. 이 회사의 "매크로로 설명되지 않은 가장 중요한 이벤트" 1~2개를 top으로 고른다(|잔차|, 회사 방향을 바꾼 사건 우선). type이 "시장·업종 공통 충격"인 날은 top에서 제외하되, 2026년 7월 28일~31일처럼 극단적인 공통 충격이 있었다면 그 원인도 한 줄로 확인해 common_2026에 적는다.
3. 나머지 확인된 것은 others, 원인 미확인은 no_filing_moves.

## 금지
- 기억으로 사실을 보충하지 마라. 모든 사실에 출처(공시 제목+접수번호, 또는 실제로 연 URL)와 짧은 인용(15단어 이내)을 붙인다.
- 날짜가 주가 반응일과 맞는지 확인한다(장 마감 후 공시는 다음 거래일 반응). 모호하면 "모호".

## 출력
`/mnt/user-data/outputs/fruiting/kr/events_{PREFIX}.json`:
{"ticker":"{TK}","top":[{"date":"","filed":"","title_ko":"","summary_ko":"2~3문장, 합니다체. 수익률·매크로 예측·잔차를 %로(변수명 R/fit/res 쓰지 말 것)","why_important_ko":"","facts":[{"fact_ko":"","quote":"","file":"URL 또는 'KIND 공시 제목 (접수번호)'"}]}],
 "others":[{"date":"","filed":"","title_ko":"","R":0,"res":0,"file":""}],
 "no_filing_moves":[{"date":"","R":0,"res":0,"note":""}],
 "common_2026":[{"date":"","R":0,"note":"","source":""}]}
임시 파일은 /tmp/ev_{PREFIX}/ 에만. JSON 파싱 확인 후 120단어 이내 한국어 보고.
