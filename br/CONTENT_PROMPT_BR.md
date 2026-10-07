# 브라질 ADR 기업 페이지 서술 작성 지침 (그룹 {G}: {LIST})

목표: `/mnt/user-data/outputs/fruiting/br/content_br_{g}.py` 파일 하나를 만든다. 이 파일은 `C = {}` 딕셔너리에 담당 종목별 서술을 넣는다. 형식은 `/mnt/user-data/outputs/fruiting/hk3/content_hk3.py`(홍콩 3종목 예시)와 같고, 아래 키를 추가로 넣는다.

## 입력 데이터(이것만 사실 근거로 쓴다)
- `/mnt/user-data/outputs/fruiting/br/data/page_data.json` → ["data"][키]: stats(장기 수익률·최대낙폭·최고가, xle_cagr = 같은 기간 EWZ 연평균), eda(full.r2, full.shapley = 설명력 몫, full.beta_cny = USD/BRL 1% 상승(헤알 약세) 때 주가 % 반응, full.beta_spx, periods), moves, events(top/others/no_filing_moves), verify.rows, cnval(가치평가 값과 라벨), scen, score(점수 항목), fund(연간 XBRL), peers.
- `/mnt/user-data/outputs/fruiting/br/data/rr_beta.json` (slug별 실질금리 베타: beta_simple = 1%p 상승 시 월간 수익률, beta = S&P 500 통제 후).
- `/mnt/user-data/outputs/fruiting/br/data/verification.json` ["rows"][원천 티커] — 두 추출이 일치한 값(a/b). 원천 티커: VALE, PBR, ITUB, NU, BBD, ABEV, SBS, ERJ(=EMBJ), AXIA(=AXIA3.SA). 2025Q2 등 전년 동기 값도 있다(전년비 계산에 사용).
- `/mnt/user-data/outputs/fruiting/br/extract_SBS_IMG.json` (Sabesp 이미지 확인값).
- `/mnt/user-data/outputs/fruiting/br/events_{원천 티커}.json` (이벤트 원문 확인 결과).
- `/mnt/user-data/outputs/fruiting/br/data/ix20f.json` (20-F 인라인 XBRL 연간 값).
- 원문이 필요하면 `/mnt/user-data/outputs/fruiting/br/raw/{원천 티커}/`의 SEC 6-K HTML을 BeautifulSoup으로 표 구조를 유지해 읽는다(평문 정규식 금지).

## 각 종목 딕셔너리 키
slug, name(영문 회사명), exch('NYSE' 등. AXIA는 'B3 (NYSE 상장폐지)'), tdisp(표시 티커, 예: 'VALE', 'EMBJ', 'AXIA3'), cur('US$' 또는 'R$'),
lead(2~3문장: 무슨 회사인지 + 최근 분기 핵심 숫자 + 핵심 쟁점),
thesis(3개: ①장기 주가(stats: 시작일 이후 연평균, 같은 기간 EWZ 연평균, 최대낙폭 시점, 최고가) ②매크로 설명력(R², Shapley 상위 2~3개 지표 몫 %, 헤알 베타) ③최근 실적 핵심),
elements(정확히 8개 튜플 (제목, [불릿 2개])): 사업 구조·성장 / 수익성 / 현금흐름·투자 / 재무구조 / 주주환원 / 경쟁·이벤트(events top 1~2개를 날짜·수익률·잔차와 함께) / 가치평가(cnval 값) / 리스크. 은행·핀테크는 제목을 '자산건전성·자본' 등으로 바꿔도 된다.
heads(8개 짧은 요약, elements 순서대로),
macro_read(3~5문장: 설명력 1~2위 지표, 헤알 1% 강세 시 주가 반응(= −beta_cny × 1%), 실질금리 베타, 저자 판단과의 관계),
monitor(4개 (지표, 이유) 튜플),
frame(dict: read(저자 프레임워크로 읽은 해석 3~4문장. 저자는 이 회사를 직접 거명하지 않았다(0.25점). 저자는 신흥국 강세·원자재와 연결된 브라질 선호·달러 약세·미국 실질금리 하락 시 브라질 수혜·미국 주식 약세를 본다), up(2개), down(2개)),
vnote(HTML 문자열: `<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ①… ②…</div>` — 모호 값, 단일 출처, 계산 방식의 한계, 주식 수 가정, 연환산의 계절성 등. 확인할 것이 없으면 `<div class="callout"><b>데이터 메모.</b> …</div>`),
start_note(분석 시작일 설명 1문장: 예 '2000년 8월부터(EWZ 상장 직후) Yahoo 수정주가로 분석했습니다.'),
deep('기준: 2026년 2분기 실적(SEC 6-K), 연간은 2025년 20-F, 주가는 10/5 종가(달러 ADR). 금액은 US$.' 식),
fundnote(연간 차트 설명: 출처 20-F XBRL, 단위, 빠진 연도),
finsrc('재무: SEC 원본 6-K HTML(…), 20-F. 표 구조와 열(기간)을 유지해 읽었고, 서로 다른 두 에이전트가 따로 추출해 대조했습니다. …' 식, 환율 사용 시 'USD/BRL 5.00(2026-10-06)').

## 규칙
1. 모든 숫자는 위 데이터에서 온 것이어야 한다. 직접 계산한 값(전년비 %, 비율, 합계)은 문장 안에 "(계산)"을 붙인다. 기억으로 사실을 보충하지 마라(회사 역사·시장점유율·인물·정책 등 데이터에 없는 사실 금지). 데이터에 없는 일반 설명은 "~로 알려진" 같은 표현 없이 아예 쓰지 않는다.
2. status가 ambiguous였던 값은 쓰지 않거나 "⚠ 모호"로 표시한다. ABEV Q6은 extract A(지배주주 귀속 정상화 순이익)를 쓴다.
3. 금액 표기: US$는 'US$37.6억', 헤알은 'R$154억', 큰 값은 조 단위 'R$2.2조' 가능. 백분율은 소수 1자리. 배수 '4.9배'.
4. 투자 권유·목표주가·매수/매도 표현 금지. 이선철 대표를 1인칭으로 쓰지 마라("저자는 ~로 봅니다"). 칼럼 제목·번호·직접 인용 금지(결론만 요약).
5. 쉬운 한국어, 존댓말 평서문('~입니다'). 문장은 짧게. 변수명(R, fit, res, beta_cny) 노출 금지.
6. AXIA: NYSE에서 2026년 6월 상장폐지(Form 25, 2026-06-10/06-11), 15F로 SEC 등록 해지 신청(2026-06-22, 08-07)한 사실을 lead 또는 vnote에 넣는다(출처 hk_hist.json의 SEC 공시 목록, 근거로 쓸 때 '(SEC 공시 목록)'). 주가는 B3 보통주 AXIA3(헤알)로 분석.
7. 작성 후 `python3 -c "import sys; sys.path.insert(0,'/mnt/user-data/outputs/fruiting/br'); import content_br_{g} as m; print({k:(len(v['elements']),len(v['heads']),len(v['thesis']),len(v['monitor'])) for k,v in m.C.items()})"`로 확인(각 8,8,3,4).
8. 마지막에 120단어 이내 한국어 보고: 작성 종목, 확인이 필요해 vnote에 넣은 항목.

담당: {LIST} (C의 키는 page_data의 키: VALE, PBR, ITUB, NU, BBD, ABEV, SBS, EMBJ, AXIA3.SA)
slug: VALE→vale, PBR→petrobras, ITUB→itau, NU→nu, BBD→bradesco, ABEV→ambev, SBS→sabesp, EMBJ→embraer, AXIA3.SA→axia
