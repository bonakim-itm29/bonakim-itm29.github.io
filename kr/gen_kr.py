import json, html, os, math
from content_kr import C
D = json.load(open('data/page_data.json'))
T = open('template_kr.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
VNOTE = {
 '005930.KS': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 부문 영업이익 합계가 연결 영업이익보다 0.02조 원 적습니다(회사가 "기타"를 따로 표시하지 않음). ② 2분기 주당배당 374원은 배당 주석의 배당률(액면 100원 기준 3.74)과 배당총액으로 확인했습니다. ③ 시가총액은 6월 말 유통주식 수 기준이라 8월 21일 결정한 자사주 취득은 반영되지 않았습니다. ④ 원문 부문명 "Haman"은 Harman의 오기로 보입니다.</div>',
 '000660.KS': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 단일 영업부문이라 부문별 영업이익이 없습니다. DRAM·NAND는 품목별 매출입니다. ② 순이익에 금융상품 평가이익(2분기 53.2조 원)이 커서, PER은 영업이익 기반 "핵심 이익"으로 따로 계산했습니다. ③ 시가총액은 7월 ADR 발행 신주 17.79M주를 더한 728.9M주, 순현금은 ADR 발행총액 39.9조 원(수수료 차감 전)을 더한 값입니다. 8월 19일 발표한 약 40조 원 자사주 매입·소각은 반영 전입니다.</div>'}
START_NOTE = {'005930.KS': '1975년 상장. 원/달러 환율 자료가 있는 2004년부터 분석(2018년 50:1 액면분할 반영).', '000660.KS': '1996년 상장. 2004년부터 분석(2003년 21:1 감자 반영).'}
COMMON = '''<div class="panel"><h3><span class="pill p-neu">시장 공통</span>2026년 7월 말 급락과 급반등</h3>
<div class="tbl"><table><tr><th>날짜</th><th class="num">삼성전자</th><th class="num">SK하이닉스</th><th class="num">코스피</th><th>무슨 일이 있었나</th></tr>
<tr><td>2026-07-28</td><td class="num">−13.4%</td><td class="num">−14.6%</td><td class="num">−10.8%</td><td>전날 상하이에 상장한 중국 메모리 업체 CXMT의 첫날 급등과 중국 공급 확대 우려로 반도체 중심 외국인 매도가 쏟아졌습니다. <a href="https://www.mt.co.kr/stock/2026/07/28/2026072816223678548">머니투데이</a></td></tr>
<tr><td>2026-07-31</td><td class="num">+26.8%</td><td class="num">+30.0%</td><td class="num">+17.9%</td><td>미국 빅테크 호실적으로 AI 투자심리가 회복되고 급락 후 반발 매수가 몰려 코스피가 역대 최대폭으로 올랐습니다. SK하이닉스는 상한가였습니다. <a href="https://www.fnnews.com/news/202607311547599134">파이낸셜뉴스</a></td></tr></table></div>
<p class="small">이런 날은 회사 공시로 설명되지 않습니다. 코스피나 전날 미국 반도체지수가 함께 크게 움직인 날은 "시장·업종 공통 충격"으로 따로 분류했습니다. 저자가 7월 29일 칼럼에서 짚은 CXMT 상장과 같은 시점입니다.</p></div>'''
for t, c in C.items():
    d = D['data'][t]
    for e in d['moves']['events']:
        if e.get('cn') is not None: e['cn'] = round(math.expm1(e['cn']), 4)
    d['extraEvent'] = COMMON
    import re as _re
    ev = d['events']
    ev['unread'] = [o for o in ev['others'] if '미확보' in o['title_ko']]
    ev['others'] = [o for o in ev['others'] if '미확보' not in o['title_ko']]
    def _clean(s):
        s = _re.sub(r'(?:매크로 (?:모델 )?예측 )?fit ([+\-−]?\d)', r'매크로 예측 \1', s)
        s = _re.sub(r'(?:잔차 )?res ([+\-−]?\d)', r'잔차 \1', s)
        s = _re.sub(r'(?:수익률 |주가 )?\bR ([+\-−]?\d)', r'수익률 \1', s)
        return s
    for e in ev['top']:
        for k, v in list(e.items()):
            if isinstance(v, str): e[k] = _clean(v)
    els = ''.join(f'<details class="acc"><summary><span class="n">{i+1}</span><b>{html.escape(h)}</b><span class="chev"></span><span class="hl">{html.escape(c["heads"][i])}</span></summary><ul class="tight">' + ''.join(f'<li>{html.escape(b)}</li>' for b in bl) + '</ul></details>' for i, (h, bl) in enumerate(c['elements']))
    mon = ''.join(f'<div><b>{html.escape(a)}</b>{html.escape(b)}</div>' for a, b in c['monitor'])
    fr = c['frame']
    s = (T.replace('__NAME__', c['name']).replace('__T__', t).replace('__EXCH__', c['exch']).replace('__LEAD__', html.escape(c['lead']))
          .replace('__THESIS__', ''.join(f'<li>{html.escape(x)}</li>' for x in c['thesis'])).replace('__ELEMENTS__', els)
          .replace('__MACROREAD__', html.escape(c['macro_read'])).replace('__MONITOR__', mon).replace('__VNOTE__', VNOTE[t])
          .replace('__FRAMEREAD__', html.escape(fr['read'])).replace('__UP__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['up'])).replace('__DOWN__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['down']))
          .replace('__START__', d['stats']['start']).replace('__STARTNOTE__', START_NOTE[t])
          .replace('__LABELS__', json.dumps(D['labels'], ensure_ascii=False))
          .replace('__DATA__', json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))
    s = s.replace('기준: 2026년 2분기(10-Q), 매장량은 2025년 말(10-K), 주가는 9/25 종가.', '기준: 2026년 반기보고서(연결), 연간은 사업보고서, 주가는 9/23 종가(추석 연휴 전 마지막 거래일).')
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    print(t, c['slug'], len(s), '__' in s.split('<script>')[0] and [x for x in ['__NAME__','__T__','__LEAD__','__VNOTE__'] if x in s])
