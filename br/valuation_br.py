import json, sys, pandas as pd, numpy as np
sys.path.insert(0, '.')
from framework_br import items as fw_items, SLUG
clip = lambda x: max(0.0, min(1.0, x))
y = pd.read_pickle('data/prices.pkl')
ASOF = '2026-10-06'
BRL = float(y['BRL=X'].dropna().loc[:ASOF].iloc[-1])
VF = json.load(open('data/verification.json'))['rows']
IMG = {(i['id'], i['period']): i['value'] for i in json.load(open('extract_SBS_IMG.json'))['items']}
def g(t, i, p):
    for r in VF[t]:
        if r['id'] == i and r['period'] == p:
            v = r['a'] if r['a'] is not None else r['b']
            if v is None: raise KeyError((t, i, p))
            return v
    raise KeyError((t, i, p))
def px(s): return float(y[s].dropna().loc[:ASOF].iloc[-1])
EX = 'ERJ'
# 시가총액(보고통화 백만): ADR 가격 ÷ ADR 비율 × 주식 수. BRL 보고 기업은 USD/BRL로 환산.
NF = {  # 비금융
 'VALE': dict(src='VALE', cur='USD', pxcur='US$', mcap=lambda: px('VALE') * 4255.762783, sh=4255.762783, adr=1,
     sh_note='유통 보통주 4,255.8M주(2026-06-30, 자기주식 제외, 2분기 재무제표). 1 ADR = 보통주 1주. 황금주 12주는 정부 보유',
     nd=g('VALE', 'B4', '2026-06-30'), nd_label='회사 제시 순부채(총차입 − 현금·단기투자, 리스 제외) US$131.7억. 확장 순부채(리스·브루마지뉴 배상 등 포함)는 US$166.8억',
     ebitda=g('VALE', 'Q3', '2026H1') * 2, eb_label='조정 EBITDA(상반기 × 2)',
     ni=g('VALE', 'Q6', '2026H1') * 2, ni_label='조정 순이익(상반기 × 2)',
     fcf=g('VALE', 'Q10', '2026H1') * 2, cf_label='FCF 수익률(회사 제시 FCF, 상반기 × 2)',
     extra=('2025년 연간 귀속 순이익(XBRL)', 2352.0)),
 'PBR': dict(src='PBR', cur='USD', pxcur='US$', mcap=lambda: px('PBR') / 2 * 7442.231382 + px('PBR-A') / 2 * 5446.501379, sh=12888.732761, adr=2,
     sh_note='보통주 7,442.2M주 + 우선주 5,446.5M주(2026-06-30, 2분기 재무제표 주석 26). 1 ADR(PBR) = 보통주 2주, PBR.A = 우선주 2주. 시가총액 = 보통주 ADR 가격 × 보통주 + 우선주 ADR 가격 × 우선주(각 ÷ 2). 시점 유통주식 수가 따로 없어 가중평균 유통주식 수와 같은 값을 썼습니다(⚠)',
     nd=g('PBR', 'B4', '2026-06-30'), nd_label='회사 제시 순부채(리스 포함 총부채 US$708.1억 − 현금·금융투자) US$603.9억',
     ebitda=g('PBR', 'Q3_Adjusted EBITDA', '2026H1') * 2, eb_label='조정 EBITDA(상반기 × 2)',
     ni=g('PBR', 'Q5', '2026H1') * 2, ni_label='귀속 순이익(상반기 × 2)',
     fcf=g('PBR', 'Q10', '2026H1') * 2, cf_label='FCF 수익률(회사 제시 FCF, 상반기 × 2)',
     extra=('2024년 연간 귀속 순이익(XBRL)', 7528.0)),
 'ABEV': dict(src='ABEV', cur='BRL', pxcur='US$', mcap=lambda: px('ABEV') * BRL * (15763.665 - 310.870), sh=15763.665 - 310.870, adr=1,
     sh_note='발행 보통주 15,763.7M주 − 자기주식 310.9M주 = 15,452.8M주(2026-06-30, 계산). 1 ADR = 보통주 1주',
     nd=g('ABEV', 'B4', '2026-06-30'), nd_label='회사 제시 순현금 R$154.0억(현금·투자증권 − 차입·리스)',
     ebitda=g('ABEV', 'Q3', '2026H1') * 2, eb_label='정상화 EBITDA(상반기 × 2, 4분기 성수기 미반영)',
     ni=g('ABEV', 'Q6', '2026H1') * 2, ni_label='정상화 귀속 순이익(상반기 × 2)',
     fcf=24450.0 - 4590.0, cf_label='FCF 수익률(2025년 연간 영업CF − 설비투자, XBRL)',
     extra=('2025년 연간 귀속 순이익(XBRL)', 15503.0)),
 'SBS': dict(src='SBS', cur='BRL', pxcur='US$', mcap=lambda: px('SBS') * BRL * 3524.534025, sh=3524.534025, adr=1,
     sh_note='발행 보통주 3,524.5M주(2026-06-30, 2026년 5월 1:5 분할 후). 자기주식은 금액(R$4.7억)만 공시돼 빼지 않았습니다(⚠). 1 ADR = 보통주 1주',
     nd=g('SBS', 'B4', '2026-06-30'), nd_label='회사 제시 순부채(차입·사채 − 현금 − 금융투자) R$342.2억',
     ebitda=(g('SBS', 'Q3', '2026Q2') + g('SBS', 'Q3', '2026Q1')) * 2, eb_label='조정 EBITDA(1·2분기 합 × 2)',
     ni=(g('SBS', 'Q6', '2026Q2') + g('SBS', 'Q6', '2026Q1')) * 2, ni_label='조정 순이익(1·2분기 합 × 2)',
     fcf=(IMG[('Q8', '2026H1')] + IMG[('Q9_CF', '2026H1')]) * 2, cf_label='FCF 수익률(상반기 영업CF − 설비·계약자산 투자, × 2)',
     extra=('2분기 조정 순이익 × 4', g('SBS', 'Q6', '2026Q2') * 4)),
 'EMBJ': dict(src='ERJ', cur='USD', pxcur='US$', mcap=lambda: px('EMBJ') / 4 * 722.766139, sh=722.766139, adr=4,
     sh_note='보통주 722.8M주(2025-12-31, 20-F). 1 ADS = 보통주 4주',
     nd=-g('ERJ', 'B4_Embraer & Eve net cash', '2026-06-30'), nd_label='회사 제시 연결 순부채(Eve 포함) US$1.24억 = 현금·금융투자 − 차입. Eve를 뺀 엠브라에르 단독 순부채는 US$2.15억',
     ebitda=607.6 + 259.5, eb_label='EBITDA(2025년 연간 영업이익 + 감가상각, XBRL, 계산)',
     ni=351.9, ni_label='귀속 순이익(2025년 연간, XBRL)',
     fcf=870.0 - 187.2 - 296.7, cf_label='FCF 수익률(2025년 연간 영업CF − 유형·무형자산 투자, XBRL)',
     extra=('조정 순이익 상반기 × 2(계절성 큼)', g('ERJ', 'Q6', '2026H1') * 2)),
 'AXIA3.SA': dict(src='AXIA', cur='BRL', pxcur='R$', mcap=lambda: px('AXIA3.SA') * 2831.259688, sh=2831.259688, adr=1,
     sh_note='보통주 1,975.4M + PNA1 0.1M + PNB1 266.5M + PNC 589.3M = 2,831.3M주(2025-12-31, 20-F). 모든 주식에 B3 보통주(AXIA3) 가격을 적용했습니다. PNA1·PNB1은 노부 메르카도 이전 때 1.1주로 바뀝니다',
     nd=g('AXIA', 'B4_Net_Debt', '2026-06-30'), nd_label='회사 제시 순부채 R$454.6억',
     ebitda=g('AXIA', 'Q3_Adjusted_EBITDA', '2026H1') * 2, eb_label='조정 EBITDA(상반기 × 2)',
     ni=g('AXIA', 'Q6_Adjusted_Net_Income', '2026H1') * 2, ni_label='조정 순이익(상반기 × 2)',
     fcf=(g('AXIA', 'Q10_Free_Cash_Flow', '2026Q2') + g('AXIA', 'Q10_Free_Cash_Flow', '2026Q1')) * 2, cf_label='FCF 수익률(회사 제시 FCF, 1·2분기 합 × 2)',
     extra=('귀속 순이익 상반기 × 2', g('AXIA', 'Q5', '2026H1') * 2)),
}
BK = {
 'ITUB': dict(src='ITUB', cur='BRL', pxcur='US$', mcap=lambda: px('ITUB') * BRL * 11021.872542, sh=11021.872542,
     sh_note='보통주 5,617.7M + 우선주 5,404.1M = 11,021.9M주(2026-06-30, 자기주식 제외). 1 ADR = 우선주 1주. 보통주에도 ADR 가격을 적용했습니다',
     eq=g('ITUB', 'B4', '2026-06-30'), ni=g('ITUB', 'Q2', '2026H1') * 2, ni_label='경상 순이익(상반기 × 2)',
     roe=g('ITUB', 'Q3', '2026Q2') / 100, roe_label='경상 ROE(2분기, 회사 제시)',
     ret=g('ITUB', 'R1_total_declared', '2026H1') * 2 + g('ITUB', 'R2', '2026H1') * 2, ret_label='주주환원수익률(상반기 선언 배당·JCP R$90.4억 + 자사주 R$17.6억, × 2)',
     cet1=g('ITUB', 'B5', '2026-06-30')),
 'BBD': dict(src='BBD', cur='BRL', pxcur='US$', mcap=lambda: px('BBD') * BRL * 10570.712028, sh=10570.712028,
     sh_note='보통주·우선주 합계 10,570.7M주(2026-06-30, 자기주식 제외). 1 ADR = 우선주 1주. 보통주(ADR BBDO)는 우선주보다 싸게 거래되지만 같은 가격을 적용했습니다',
     eq=g('BBD', 'B4', '2026-06-30'), ni=g('BBD', 'Q2', '2026H1') * 2, ni_label='경상 순이익(상반기 × 2)',
     roe=g('BBD', 'Q3', '2026Q2') / 100, roe_label='경상 ROE(2분기, 회사 제시)',
     ret=g('BBD', 'R1_1H26 total accrued (gross)', '2026H1') * 2, ret_label='주주환원수익률(상반기 배당·JCP 세전 R$79.7억 × 2, 자사주 금액 미공시)',
     cet1=g('BBD', 'B5', '2026-06-30')),
 'NU': dict(src='NU', cur='USD', pxcur='US$', mcap=lambda: px('NU') * (3808.087961 + 1022.600698), sh=3808.087961 + 1022.600698,
     sh_note='Class A 3,808.1M + Class B 1,022.6M = 4,830.7M주(2026-06-30). Class A는 자사주 40.7M주를 뺀 값인지 표 라벨이 모호합니다(⚠, 차이 약 0.8%)',
     eq=g('NU', 'B4', '2026-06-30'), ni=g('NU', 'Q1', '2026H1') * 2, ni_label='귀속 순이익(상반기 × 2)',
     roe=g('NU', 'Q3', '2026Q2') / 100, roe_label='ROE(2분기 연율, 회사 제시)',
     ret=abs(g('NU', 'R2', '2026H1')) * 2, ret_label='주주환원수익률(상반기 자사주 매입 US$5.0억 × 2, 배당 없음)',
     cet1=g('NU', 'B5', '2026-06-30')),
}
E = json.load(open('data/eda_weekly.json'))['res']; M = json.load(open('data/moves.json'))
def hist_items(t):
    e = E[t]['full']; bs = e['beta_spx']; r2 = e['r2']; rv = M[t]['resid_var_share']; cq = E[t]['corr_q']['OIL']
    return [dict(k='미국 주식 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 저자는 미국 주식 약세를 봄'),
            dict(k='브라질 지수 연동성(EWZ 분기 상관)', val=f'{cq:.2f}', pts=round(clip(cq / 0.7), 2), max=1.0, rule='저자는 신흥국·브라질 강세를 봄. 0.7 이상 만점(EWZ에 이 종목이 포함돼 상관이 부풀 수 있음)'),
            dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {min(rv,1)*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달될수록 높음')], e['beta_cny']
FWA = lambda: [dict(k='신흥국(브라질) 강세 신호', val='강세 · 신뢰도 높음(80% vs 66%)', pts=1.5, max=1.5, rule='프레임워크의 신흥국 입장(브라질 관심 종목 공통). 저자는 원자재와 연결된 브라질을 신흥국 가운데 가장 선호'),
               dict(k='저자의 종목 거명', val='직접 거명 없음(EWZ로 언급)', pts=0.25, max=0.5, rule='칼럼에서 투자 대상으로 거명되면 0.5, 아니면 0.25')]
out = {}
def fin(t, v, A, B, met, scen):
    C, bc = hist_items(t); A = A + fw_items(bc, SLUG[t])
    sA, sB, sC = (round(sum(x['pts'] for x in L), 2) for L in (A, B, C))
    score = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    out[t] = dict(val=met, scen=scen, score=score)
    print(t, 'score', score['total'], sA, sB, sC); [print('    ', i['k'], i['val'], i['pts']) for P in score['pillars'] for i in P['items']]
for t, v in NF.items():
    price = px(t); mc_u = v['mcap']()  # USD M (AXIA: BRL M)
    fxr = 1.0 if v['cur'] == 'USD' or t == 'AXIA3.SA' else BRL       # 보고통화 per 가격통화
    mc = mc_u * fxr if t != 'AXIA3.SA' else mc_u                       # 보고통화 백만
    if v['cur'] == 'BRL' and t != 'AXIA3.SA': mc = mc_u                # 이미 BRL로 계산됨
    ev = mc + v['nd']; eve = ev / v['ebitda']; pe = mc / v['ni'] if v['ni'] > 0 else None; fy = v['fcf'] / mc; lev = v['nd'] / v['ebitda']
    cs = 'US$' if v['cur'] == 'USD' else 'R$'
    per_adr = (v['adr'] / v['sh']) / (BRL if (v['cur'] == 'BRL' and t != 'AXIA3.SA') else 1)  # 보고통화 백만 → 가격통화 주당
    eps = v['ni'] * per_adr; eps2 = v['extra'][1] * per_adr
    met = dict(kind='br', price=price, asof=str(y[t].dropna().loc[:ASOF].index[-1].date()), cur=v['cur'], cs=cs, pxcur=v['pxcur'], usdbrl=BRL, mcap_b=mc / 1e3, mcap_usd_b=(mc / (BRL if v['cur'] == 'BRL' else 1)) / 1e3,
               netcash_b=-v['nd'] / 1e3, ev_b=ev / 1e3, ev_op=eve, pe=pe, fcf_yield=fy, nd_ebitda=lev, nc_share=-v['nd'] / mc, ads_m=v['sh'], adr=v['adr'],
               eb_label=v['eb_label'], ni_label=v['ni_label'], cf_label=v['cf_label'], nd_label=v['nd_label'], ads_note=v['sh_note'], ebitda=v['ebitda'], ni=v['ni'], fcf=v['fcf'], nd=v['nd'])
    B = [dict(k='EV/' + v['eb_label'].split('(')[0], val=f'{eve:.1f}배', pts=round(clip((10 - eve) / 6), 2), max=1.0, rule='4배 이하 만점, 10배 이상 0점(브라질 기준)', x=eve, move='ev', rule_id='br_ev'),
         dict(k='PER(' + v['ni_label'].split('(')[0] + ')', val=f'{pe:.1f}배' if pe else '적자', pts=round(clip((20 - pe) / 12), 2) if pe else 0.0, max=1.0, rule='8배 이하 만점, 20배 이상 0점', x=pe, move='price', rule_id='br_pe'),
         dict(k=v['cf_label'].split('(')[0], val=f'{fy*100:.1f}%', pts=round(clip(fy / 0.10), 2), max=1.0, rule='10% 이상 만점, 0% 이하 0점', x=fy, move='inv', rule_id='cn_yield'),
         dict(k='순부채/EBITDA', val=f'{lev:.1f}배', pts=round(clip((3 - lev) / 2), 2), max=1.0, rule='1배 이하 만점, 3배 이상 0점(순현금이면 만점)', x=lev, move='fixed', rule_id=None)]
    rows = [dict(label=v['ni_label'], eps=round(eps, 2), vals=[round(m * eps, 2) if eps > 0 else None for m in (6, 9, 12)]),
            dict(label=v['extra'][0], eps=round(eps2, 2), vals=[round(m * eps2, 2) if eps2 > 0 else None for m in (6, 9, 12)])]
    scen = dict(kind='pe', rows=rows, implied=price / eps if eps > 0 else None, mults=[6, 9, 12])
    fin(t, v, FWA(), B, met, scen)
for t, v in BK.items():
    price = px(t); mc = v['mcap']()
    cs = 'US$' if v['cur'] == 'USD' else 'R$'
    pb = mc / v['eq']; pe = mc / v['ni']; ry = v['ret'] / mc; roe = v['roe']
    per = 1 / v['sh'] / (BRL if v['cur'] == 'BRL' else 1)
    bvps = v['eq'] * per; eps = v['ni'] * per
    met = dict(kind='bank', price=price, asof=str(y[t].dropna().loc[:ASOF].index[-1].date()), cur=v['cur'], cs=cs, pxcur=v['pxcur'], usdbrl=BRL, mcap_b=mc / 1e3, mcap_usd_b=(mc / (BRL if v['cur'] == 'BRL' else 1)) / 1e3,
               pb=pb, pe=pe, ret_yield=ry, roe=roe, cet1=v['cet1'], eq=v['eq'], ni=v['ni'], ret=v['ret'], ads_m=v['sh'], adr=1, bvps=bvps, eps=eps,
               ni_label=v['ni_label'], roe_label=v['roe_label'], ret_label=v['ret_label'], ads_note=v['sh_note'])
    B = [dict(k='P/B(주가순자산비율)', val=f'{pb:.2f}배', pts=round(clip((2.5 - pb) / 1.5), 2), max=1.0, rule='1배 이하 만점, 2.5배 이상 0점', x=pb, move='price', rule_id='pb'),
         dict(k='PER(' + v['ni_label'].split('(')[0] + ')', val=f'{pe:.1f}배', pts=round(clip((15 - pe) / 9), 2), max=1.0, rule='6배 이하 만점, 15배 이상 0점(은행 기준)', x=pe, move='price', rule_id='bk_pe'),
         dict(k=v['ret_label'].split('(')[0], val=f'{ry*100:.1f}%', pts=round(clip(ry / 0.08), 2), max=1.0, rule='8% 이상 만점, 0% 0점', x=ry, move='inv', rule_id='bk_yield'),
         dict(k='ROE(' + v['roe_label'].split('(')[0] + ')', val=f'{roe*100:.1f}%', pts=round(clip((roe - 0.08) / 0.12), 2), max=1.0, rule='20% 이상 만점, 8% 이하 0점', x=roe, move='fixed', rule_id=None)]
    rows = [dict(label='주당 순자산(BVPS)', eps=round(bvps, 2), vals=[round(m * bvps, 2) for m in (1.0, 1.5, 2.0)])]
    scen = dict(kind='pb', rows=rows, implied=price / bvps, mults=[1.0, 1.5, 2.0], eps=round(eps, 2), implied_pe=pe)
    fin(t, v, FWA(), B, met, scen)
json.dump(out, open('data/val_br.json', 'w'), ensure_ascii=False)
print('USD/BRL', BRL)
