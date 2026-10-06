import json, html, os
from content import C, HEADS, FRAME
SC = json.load(open('data/scores.json'))
NAVS = json.load(open('data/nav_scen.json'))
D = json.load(open('data/page_data.json'))
T = open('template.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
# valuation overrides (updated after REI Q2 release; SM post-merger NAV)
OVR = {'REI': dict(net_debt_m=361.58, ev_m=715.9, ev_ebitdax_q2ann=715.9 / (54.482 * 4), ev_ebitdax_h1ann=715.9 / ((38.31 + 54.482) * 2),
                   nd_ebitdax_h1ann=361.58 / ((38.31 + 54.482) * 2), fcf_yield_h1ann=(0.237 + 4.375) * 2 / 354.33, nav_pv10_ps=3.67, nav_stdm_ps=2.92)}
VNOTE = {
 'CRGY': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> 하반기 원유 헤지(O8): 10-Q 헤지 표의 기간이 "2026"으로만 적혀 있어 7~12월 물량으로 확정할 수 없고, 칼라를 총량에 넣을지도 표에서 정해지지 않습니다. 원문 표를 확인해 주시면 반영하겠습니다. LOE(O4)는 재추출에서 모호로 분류됐지만, 10-Q MD&amp;A 한 문단에 "$6.80 per Boe"가 명시돼 있어 확정했습니다.</div>',
 'KOS': '<div class="callout warn"><b>⚠ 회사가 공시하지 않아 비워 둔 항목.</b> 회사 전체 원유 일평균 생산량(O2), 전체 PV-10(R4), 매장량 평가에 쓴 SEC 가격 수치(R5), 재무상태표의 총부채 합계 행(F7). 추정하지 않았습니다. 2분기 매출은 "Oil and gas revenue" $607.3M 기준이며, 기타수익을 포함한 "Total revenues and other income"은 $617.0M입니다.</div>',
 'REI': '<div class="callout warn"><b>⚠ 계산값 표시.</b> 회사는 "순부채"를 제시하지 않습니다(O7). 이 페이지의 순부채 $361.6M은 실적발표문의 약정 기준 Consolidated Total Debt $362.7M에서 현금 $1.1M을 뺀 값입니다. 하반기 헤지 총량 1,724,085 Bbl과 스왑 가중평균은 10-Q 헤지 표를 합산한 계산값입니다.</div>',
 'SM': '<div class="callout"><b>✔ 해소된 확인 요청.</b> 앞서 매각 자산 명칭이 합산 재무제표 서술문("Maverick Basin Divestiture")과 10-Q("South Texas Divestiture")에서 달라 NAV를 잠정치로 두었습니다. 10-Q가 "South Texas Divestiture"를 "southern Maverick Basin position"(약 61,000 순에이커, 매수자 Caturus) 매각으로 정의하고 있어, 같은 자산임을 원문으로 확인했습니다. 합산 NAV $28.01은 확정입니다. 재무상태표에는 총부채 합계 행이 없고(F7), 매장량(R1~R5)은 합병 전 SM 단독 기준입니다.</div>'}
START_NOTE = {
 'CRGY': '2021년 12월 상장(옛 이름 IE PubCo).',
 'KOS': '2011년 5월 NYSE 상장.',
 'REI': '2012년 7월 이전은 주가가 수년간 $4.00로 고정된 사실상 휴면기라 제외했습니다(2008년 1:18 주식병합 반영).',
 'SM': '1992년 12월 상장. Yahoo 가격은 1993년부터이고, 다변량 회귀는 BEI가 있는 2003년부터입니다(상관과 주가 차트는 1993년부터).'}
EXTRA = {'KOS': '<div class="panel"><h3><span class="pill p-good">보완 확인</span>최종 증자 규모 (10-Q)</h3><p>424B5(3/11 밤)는 9,750만 주와 초과배정 옵션을 적었고, 3/11 옵션 전량 행사 후 최종 결과는 2분기 10-Q에 있습니다. 1.121억 주, 순조달 약 $206.4M, 3월 12일 종결입니다.</p><blockquote>“112.1 million shares of common stock … net proceeds to Kosmos of approximately $ 206.4 million” — kos-20260630.htm</blockquote></div>', 'REI': '<div class="panel"><h3><span class="pill p-good">보완 확인</span>2026년 5월 유상증자 조건 (10-Q)</h3><p>8-K에는 공모가가 없어 재추출에서 "모호"로 표시됐지만, 2분기 10-Q의 한 문단에서 확인했습니다. 5월 14일 44,444,445주를 주당 $1.35에 발행했고(총 $60.0M), 6월 12일 추가 6,666,666주 옵션이 행사됐습니다. 합계 총 $69.0M, 순 $64.5M입니다. 공모가는 발표 전 거래일(5/12) 종가 $1.78보다 24% 낮습니다(계산).</p><blockquote>“at a public offering price of $ 1.35 per share and gross proceeds of $ 60.0 million” — rei-20260630.htm</blockquote></div>'}
ACTIVE = ['CRGY', 'KOS', 'SM']
for t, c in C.items():
    if t not in ACTIVE: continue
    d = D['data'][t]
    if t in OVR: d['val'].update(OVR[t])
    d['extraEvent'] = EXTRA.get(t, '')
    els = ''.join(f'<details class="acc"><summary><span class="n">{i+1}</span><b>{html.escape(h)}</b><span class="chev"></span><span class="hl">{html.escape(HEADS[t][i])}</span></summary><ul class="tight">' + ''.join(f'<li>{html.escape(b)}</li>' for b in bl) + '</ul></details>' for i, (h, bl) in enumerate(c['elements']))
    d['nav'] = NAVS['res'][t]; d['mult'] = NAVS.get('mult', {}).get(t); d['score'] = SC[t]; d['peers'] = {k: v['total'] for k, v in SC.items() if k in ACTIVE}
    fr = FRAME[t]
    mon = ''.join(f'<div><b>{html.escape(a)}</b>{html.escape(b)}</div>' for a, b in c['monitor'])
    s = (T.replace('__NAME__', c['name']).replace('__T__', t).replace('__EXCH__', c['exch']).replace('__LEAD__', html.escape(c['lead']))
          .replace('__THESIS__', ''.join(f'<li>{html.escape(x)}</li>' for x in c['thesis'])).replace('__ELEMENTS__', els)
          .replace('__MACROREAD__', html.escape(c['macro_read'])).replace('__FRAMEREAD__', html.escape(fr['read'])).replace('__UP__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['up'])).replace('__DOWN__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['down'])).replace('__MONITOR__', mon).replace('__VNOTE__', VNOTE[t])
          .replace('__START__', d['stats']['start']).replace('__STARTNOTE__', START_NOTE[t])
          .replace('__LABELS__', json.dumps(D['labels'], ensure_ascii=False))
          .replace('__DATA__', json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    print(t, c['slug'], len(s))
