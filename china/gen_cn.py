import json, html, os, math
from content_cn import C
D = json.load(open('data/page_data.json'))
T = open('template_cn.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
VNOTE = {
 'BABA': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 6월 분기 말 자사주 잔여 한도는 공시되지 않았습니다(3월 말 $190.5억만 있음). ② 유동자산의 "지분증권 및 기타 투자" 행에 주식과 정기예금이 섞여 있어, 순현금은 회사가 문장으로 제시한 "현금 및 기타 유동투자"를 썼습니다. ③ 3월 분기 Non-GAAP 순이익은 비지배지분 포함 값(¥0.86억)만 확인돼, 최근 2개 분기 PER은 비지배 포함 기준입니다. ④ ADS 수는 20-F의 5/18 발행주식에 8월 신주를 더한 계산값이라, 그사이 자사주 매입은 반영하지 않았습니다.</div>',
 'BIDU': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 2분기 단독 자사주 매입액은 공시되지 않았습니다(1분기 초부터 누적 $2.59억만 있음). ② 분기 말 발행주식 수가 없어 7/14 기준(EGM 통지문) 2,713.5M주를 썼습니다. ③ 회사의 "현금 및 투자 합계"에는 장기 정기예금·만기보유 투자와 아이치이 현금이 들어 있습니다.</div>',
 'JD': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 2분기 단독 자사주 매입액은 공시되지 않았습니다(상반기 $10억, 1분기 $6.31억만 있음). ② 직매입 모델이라 매입채무로 쌓인 현금이 유동성에 포함돼 있어, 순현금의 일부는 영업에 묶인 돈입니다.</div>'}
START_NOTE = {'BABA': '2014년 9월 NYSE 상장.', 'BIDU': '2005년 8월 나스닥 상장(2010년 ADS 비율 변경(1 ADS = 보통주 1/10) 반영).', 'JD': '2014년 5월 나스닥 상장.'}
COMMON = '''<div class="panel"><h3><span class="pill p-neu">업종 공통</span>중국 공통 충격 중 가장 컸던 두 날</h3>
<div class="tbl"><table><tr><th>날짜</th><th class="num">BABA</th><th class="num">BIDU</th><th class="num">JD</th><th>무슨 일이 있었나</th></tr>
<tr><td>2022-03-16</td><td class="num">+36.8%</td><td class="num">+39.2%</td><td class="num">+39.4%</td><td>국무원 금융안정발전위원회가 플랫폼 정비를 "가능한 한 빨리" 마무리하고, 해외 상장 기업을 계속 지원하며, 시장에 영향을 주는 정책은 사전 조율하겠다고 발표했습니다. <a href="https://english.www.gov.cn/statecouncil/liuhe/202203/16/content_WS6231ba2bc6d02e5335327d8d.html">중국 정부 발표</a></td></tr>
<tr><td>2022-10-24</td><td class="num">−12.5%</td><td class="num">−12.6%</td><td class="num">−13.0%</td><td>시진핑 주석이 10/23 3연임을 확정한 뒤(당대회 폐막 10/22) 첫 거래일입니다. 민간기업보다 국유기업을 우선할 것이라는 우려로 중국 기술주가 급락했습니다. <a href="https://www.forbes.com/sites/qai/2022/11/20/why-did-chinese-stocks-drop-some-13-in-october-2022/">Forbes</a></td></tr></table></div>
<p class="small">이런 날은 회사 공시로는 설명되지 않습니다. 매크로 모델에 중국 정책 변수가 없어 "비매크로"로 잡히는 것을 막으려고, 업종 ETF(KWEB)의 동반 급변 여부로 따로 분류했습니다.</p></div>'''
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
    sh = d['fund']['shares']
    if t == 'BABA':
        d['fund']['shares'] = [[a, v/8 if a >= '2018-03-31' else v] for a, v in sh]
        d['fund']['sh_note'] = '2019년 1:8 보통주 분할 이후 값은 ÷8로 ADS(=보통주 8주)로 환산했습니다.'
    elif t == 'JD':
        d['fund']['shares'] = [[a, v/2] for a, v in sh]
        d['fund']['sh_note'] = '보통주 수 ÷2(ADS 1주 = 보통주 2주)로 환산했습니다.'
    else:
        d['fund']['shares'] = []
        d['fund']['sh_note'] = 'Baidu는 2011년 이후 20-F XBRL에 가중평균 주식 수 태그가 없어(2007~2010년만 존재) 차트를 생략했습니다. 최근 ADS 수는 위 시가총액 타일(339M ADS)을 참고하세요.'
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
    s = s.replace('기준: 2026년 2분기(10-Q), 매장량은 2025년 말(10-K), 주가는 9/25 종가.', '기준: 최근 분기 실적발표문(6-K), 연간은 20-F, 주가는 9/25 종가.')
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    print(t, c['slug'], len(s), '__' in s.split('<script>')[0] and [x for x in ['__NAME__','__T__','__LEAD__','__VNOTE__'] if x in s])
