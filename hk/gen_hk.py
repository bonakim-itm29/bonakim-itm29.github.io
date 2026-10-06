import json, html, os, math
from content_hk import C
D = json.load(open('data/page_data.json'))
T = open('template_hk.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
VNOTE = {
 '0700.HK': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 2분기 영업현금흐름(¥527억)과 FCF(−¥138억)는 표가 아니라 본문의 억 단위 수치입니다(상반기 표 ¥1,540.6억 − 1분기 ¥1,013.5억 = ¥527.1억으로 정합). ② 자사주 매입 잔여 한도는 공시되지 않았습니다. ③ 2021~2023년 영업현금흐름·설비투자는 5개년 요약표에 없어 장기 차트에서 뺐습니다. ④ 순현금에는 상장·비상장 지분투자가 들어 있지 않습니다.</div>',
 '3690.HK': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 메이퇀은 분기(3개월) 귀속 순이익·EPS·설비투자·FCF를 공시하지 않습니다(반기만). ② 순현금은 회사 제시값이 아니라 현금 + 단기 금융투자 − 차입 − 사채로 직접 계산했습니다. ③ 2025년 설비투자(¥132.7억)는 한 번의 추출에서만 확인됐습니다.</div>'}
START_NOTE = {'0700.HK': '2004년 6월 홍콩 상장(2014년 1:5 액면분할 반영).', '3690.HK': '2018년 9월 홍콩 상장.'}
COMMON = '''<div class="panel"><h3><span class="pill p-neu">업종 공통</span>중국 공통 충격 중 가장 컸던 두 날</h3>
<div class="tbl"><table><tr><th>날짜</th><th class="num">텐센트</th><th class="num">메이퇀</th><th>무슨 일이 있었나</th></tr>
<tr><td>2022-03-16</td><td class="num">+23.2%</td><td class="num">+32.1%</td><td>국무원 금융안정발전위원회가 플랫폼 정비를 "가능한 한 빨리" 마무리하고, 해외 상장 기업을 계속 지원하며, 시장에 영향을 주는 정책은 사전 조율하겠다고 발표했습니다. <a href="https://english.www.gov.cn/statecouncil/liuhe/202203/16/content_WS6231ba2bc6d02e5335327d8d.html">중국 정부 발표</a></td></tr>
<tr><td>2022-10-24</td><td class="num">−11.4%</td><td class="num">−14.8%</td><td>시진핑 주석이 10/23 3연임을 확정한 뒤(당대회 폐막 10/22) 첫 거래일입니다. 민간기업보다 국유기업을 우선할 것이라는 우려로 중국 기술주가 급락했습니다. <a href="https://www.forbes.com/sites/qai/2022/11/20/why-did-chinese-stocks-drop-some-13-in-october-2022/">Forbes</a></td></tr></table></div>
<p class="small">이런 날은 회사 공시로는 설명되지 않습니다. 매크로 모델에 중국 정책 변수가 없어 "비매크로"로 잡히는 것을 막으려고, 항셍지수·KWEB의 동반 급변 여부로 따로 분류했습니다.</p></div>'''
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
    s = s.replace('기준: 2026년 2분기(10-Q), 매장량은 2025년 말(10-K), 주가는 9/25 종가.', '기준: 2026년 2분기 실적발표(HKEX), 연간은 2025년 연차보고서, 주가는 9/25 종가(홍콩달러).')
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    print(t, c['slug'], len(s), '__' in s.split('<script>')[0] and [x for x in ['__NAME__','__T__','__LEAD__','__VNOTE__'] if x in s])
