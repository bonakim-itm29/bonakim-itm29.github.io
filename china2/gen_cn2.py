import json, html, os, math, re, pandas as pd
from content_cn2 import C
D = json.load(open('data/page_data.json'))
T = open('template_cn2.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
VNOTE = {
 'PDD': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 회사 정의 FCF가 없고 분기 설비투자도 공시되지 않아, FCF 수익률은 2025년 20-F 연간 값(영업현금흐름 + 설비투자)으로 계산했습니다. 다른 종목의 "최근 2개 분기 연환산"과 기준 기간이 다릅니다. ② 분기 현금흐름 요약표의 통화 머리행이 US$ 열까지 "RMB"로 표기돼 있어, 본문 문장(RMB25.7bn)과 대조해 RMB 값을 확정했습니다. ③ 실적발표문에 분기 말 주식 수가 없어 2025-12-31 발행주식(20-F 표지)을 썼습니다. ④ 기타 비유동자산 ¥963.8억에 정기예금·채권이 들어 있다고 적혀 있지만 내역이 없어 순현금에서 뺐고, 제한현금 ¥772.7억도 뺐습니다. 리스부채는 금액을 추출하지 않아 차입에 넣지 않았습니다.</div>',
 'NTES': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 2분기 유형자산 취득 ¥18.8M이 1분기(¥312.1M)·전년 2분기(¥189.8M)보다 이례적으로 작습니다. 원문 값을 그대로 썼으며, 그만큼 FCF가 크게 계산됐을 수 있습니다. ② 회사가 조정 영업이익을 내지 않아 EV/영업이익은 GAAP 영업이익 기준입니다(주식보상을 더하지 않아 다른 종목보다 보수적). ③ 자사주 프로그램($50억)의 남은 한도는 공시되지 않았습니다. 누적 사용액으로 역산한 약 $27억은 근거가 분명하지 않아 쓰지 않았습니다. ④ 2분기 자사주 매입액 $1.92억은 월별 표를 더한 값입니다(분기 합계로는 공시되지 않음).</div>',
 'TCOM': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 실적발표문에 현금흐름표가 없어 분기 영업현금흐름·설비투자·FCF는 비워 두었고, FCF 수익률은 2025년 20-F 연간 값으로 계산했습니다. 과징금 ¥51.8억이 현금으로 언제 나갔는지도 확인되지 않습니다. ② 현금및현금성자산이 제한현금과 합산돼서만 공시돼, 순현금에 제한현금이 섞여 있습니다. ③ 발행주식은 2025-12-31(649.6M주)과 2026-03-31(629.7M주) 두 값이 있어 최근 값을 썼습니다. 4월 이후 자사주 매입은 반영되지 않았습니다. ④ 자사주 남은 한도는 1차 추출만 2025년 말 약 $50.7억(20-F)을 기록했고 재추출로 확인되지 않아 쓰지 않았습니다. ⑤ 2분기 GAAP 이익은 일회성 과징금으로 왜곡돼 배수는 회사 조정치(조정 EBITDA, Non-GAAP 순이익)로 계산했습니다. 조정 EBITDA는 감가상각 전 이익이라 다른 종목의 조정 영업이익과 정의가 다릅니다.</div>'}
START_NOTE = {'PDD': '2018년 7월 나스닥 상장.', 'NTES': '2000년 6월 나스닥 상장. 홍콩(9999)에도 상장돼 있습니다.', 'TCOM': '2003년 12월 나스닥 상장(당시 Ctrip). 홍콩(9961)에도 상장돼 있습니다.'}
FUNDNOTE = {'PDD': '회사가 20-F에 XBRL로 태그한 값만 썼습니다(2016년부터). 설비투자는 2021년 이후 태그가 없어 제외했습니다.',
            'NTES': '회사가 20-F에 XBRL로 태그한 값만 썼습니다. 매출 태그(정의)가 일관된 2016년부터 표시합니다.',
            'TCOM': '회사가 20-F에 XBRL로 태그한 값만 썼습니다. 매출 태그(순매출)가 일관된 2017년부터 표시합니다. 순이익은 NetIncomeLoss 태그입니다.'}
# 업종 공통 충격: prices.pkl 일간 종가 대비 변화율(계산)
y = pd.read_pickle('data/prices.pkl')
def r(t, d):
    s = y[t].dropna(); i = s.index.get_loc(pd.Timestamp(d)); return s.iloc[i] / s.iloc[i - 1] - 1
fm = lambda v: ('+' if v > 0 else '−') + f'{abs(v)*100:.1f}%'
R1 = {t: fm(r(t, '2022-03-16')) for t in ['PDD', 'NTES', 'TCOM']}; R2 = {t: fm(r(t, '2022-10-24')) for t in ['PDD', 'NTES', 'TCOM']}
print('common', R1, R2)
COMMON = f'''<div class="panel"><h3><span class="pill p-neu">업종 공통</span>중국 공통 충격 중 가장 컸던 두 날</h3>
<div class="tbl"><table><tr><th>날짜</th><th class="num">PDD</th><th class="num">NTES</th><th class="num">TCOM</th><th>무슨 일이 있었나</th></tr>
<tr><td>2022-03-16</td><td class="num">{R1['PDD']}</td><td class="num">{R1['NTES']}</td><td class="num">{R1['TCOM']}</td><td>국무원 금융안정발전위원회가 플랫폼 정비를 "가능한 한 빨리" 마무리하고, 해외 상장 기업을 계속 지원하며, 시장에 영향을 주는 정책은 사전 조율하겠다고 발표했습니다. <a href="https://english.www.gov.cn/statecouncil/liuhe/202203/16/content_WS6231ba2bc6d02e5335327d8d.html">중국 정부 발표</a></td></tr>
<tr><td>2022-10-24</td><td class="num">{R2['PDD']}</td><td class="num">{R2['NTES']}</td><td class="num">{R2['TCOM']}</td><td>시진핑 주석이 10/23 3연임을 확정한 뒤(당대회 폐막 10/22) 첫 거래일입니다. 민간기업보다 국유기업을 우선할 것이라는 우려로 중국 기술주가 급락했습니다. <a href="https://www.forbes.com/sites/qai/2022/11/20/why-did-chinese-stocks-drop-some-13-in-october-2022/">Forbes</a></td></tr></table></div>
<p class="small">이런 날은 회사 공시로는 설명되지 않습니다. 매크로 모델에 중국 정책 변수가 없어 "비매크로"로 잡히는 것을 막으려고, 업종 ETF(KWEB)의 동반 급변 여부로 따로 분류했습니다. 수익률은 일간 종가 대비 변화율입니다(계산).</p></div>'''
def _clean(s):
    # "(R)", "(fit)", "(res)" 표식만 지움 — 앞의 한국어 라벨(주가·매크로 예측·잔차)은 그대로 둠
    return re.sub(r'\((?:R|fit|res)\)', '', s)
for t, c in C.items():
    d = D['data'][t]
    for e in d['moves']['events']:
        if e.get('cn') is not None: e['cn'] = round(math.expm1(e['cn']), 4)
    d['extraEvent'] = COMMON
    ev = d['events']
    ev['unread'] = [o for o in ev['others'] if '미확보' in o['title_ko']]
    ev['others'] = [o for o in ev['others'] if '미확보' not in o['title_ko']]
    # 표시 잔차 = 단순수익률 R − 매크로 예측 fit (화면의 R·fit과 같은 단위). 분류(share/type)는 그대로.
    FIT = {e['date']: (e['R'], e['fit'], e['res']) for e in d['moves']['events']}
    for e in d['moves']['events']: e['res'] = round(e['R'] - e['fit'], 4)
    for o in ev['others'] + ev.get('unread', []) + ev.get('no_filing_moves', []):
        if o['date'] in FIT: o['res'] = round(FIT[o['date']][0] - FIT[o['date']][1], 4)
    for e in ev['top']:
        R_, f_, r_old = FIT[e['date']]
        old_s, new_s = f'{r_old*100:+.1f}%', f'{(R_-f_)*100:+.1f}%'
        n = 0
        for k, v in list(e.items()):
            if isinstance(v, str):
                n += v.count(old_s); e[k] = _clean(v).replace(old_s, new_s)
        assert n >= 1, (t, e['date'], old_s)
        print('  resid', t, e['date'], old_s, '->', new_s, 'x', n)
    els = ''.join(f'<details class="acc"><summary><span class="n">{i+1}</span><b>{html.escape(h)}</b><span class="chev"></span><span class="hl">{html.escape(c["heads"][i])}</span></summary><ul class="tight">' + ''.join(f'<li>{html.escape(b)}</li>' for b in bl) + '</ul></details>' for i, (h, bl) in enumerate(c['elements']))
    mon = ''.join(f'<div><b>{html.escape(a)}</b>{html.escape(b)}</div>' for a, b in c['monitor'])
    fr = c['frame']; V = d['cnval']
    s = (T.replace('__EXCH__', c['exch']).replace('__NAME__', c['name']).replace('__T__', t).replace('__LEAD__', html.escape(c['lead']))
          .replace('__THESIS__', ''.join(f'<li>{html.escape(x)}</li>' for x in c['thesis'])).replace('__ELEMENTS__', els)
          .replace('__MACROREAD__', html.escape(c['macro_read'])).replace('__MONITOR__', mon).replace('__VNOTE__', VNOTE[t])
          .replace('__FRAMEREAD__', html.escape(fr['read'])).replace('__UP__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['up'])).replace('__DOWN__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['down']))
          .replace('__START__', d['stats']['start']).replace('__STARTNOTE__', START_NOTE[t]).replace('__FUNDNOTE__', FUNDNOTE[t])
          .replace('__NV__', str(len(d['verify']['rows']))).replace('__FXDATE__', V['fx_date']).replace('__FX__', f"{V['fx']:.2f}")
          .replace('__LABELS__', json.dumps(D['labels'], ensure_ascii=False))
          .replace('__DATA__', json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    left = sorted(set(re.findall(r'__[A-Z0-9]+__', s)))
    print(t, c['slug'], len(s), 'leftover placeholders:', left)
