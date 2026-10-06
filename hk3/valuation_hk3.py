import json, sys, pandas as pd, numpy as np
sys.path.insert(0, '.')
from framework_v11 import items as fw_items
clip = lambda x, a=0.0, b=1.0: max(a, min(b, x))
y = pd.read_pickle('data/prices.pkl')
ASOF = '2026-10-06'
CNY = float(y['CNY=X'].dropna().loc[:ASOF].iloc[-1]); HKD = float(y['HKD=X'].dropna().loc[:ASOF].iloc[-1])
FXR = {'USD': 1 / HKD, 'RMB': CNY / HKD}   # 보고통화 per HK$1
SLUG = {'0992.HK': 'lenovo', '1810.HK': 'xiaomi', '1211.HK': 'byd'}
V = {
 '0992.HK': dict(cur='USD', sh=12826.044682, sh_note='발행주식 12,826.0M주(2026-09-30, HKEX 월간 보고, 9월 2029년 만기 전환사채 전액 전환 반영)',
     debt=6260.099 - 402.033, liq=5907.477 + 173.304, liq_label='현금및현금성자산 + 은행예금(6월 말). 차입에서는 9월에 주식으로 전환된 2029년 만기 전환사채(장부가 US$4.02억)를 뺐습니다. 빼지 않으면 회사 제시 순부채 −US$1.79억',
     op=(1522.683,), op_label='Non-HKFRS 영업이익(회사 제시, 최근 분기 ×4)',
     ni=(1074.717, 558.740), ni_label='Non-HKFRS 귀속 순이익',
     cf_ann=4023.705 - 1859.0, cf_label='FCF 수익률(FY2025/26 연간: 영업CF − 설비투자)', extra=('FY2025/26 연간 Non-HKFRS 순이익', 2048.739)),
 '1810.HK': dict(cur='RMB', sh=25759.183087, sh_note='발행주식 25,759.2M주(Class A 4,429.2M + Class B 21,329.9M, 2026-08-31 HKEX 월간 보고)',
     debt=9706.402 + 29570.36, liq=219300.0, liq_label='회사 제시 현금 자원(cash resources) ¥2,193억(재무상태표 항목 합과 약 ¥82억 차이, 보수적으로 회사 값 사용)',
     op=(10870.168, 5312.645), op_label='영업이익(IFRS)', ni=(6219.073, 6072.135), ni_label='조정 순이익',
     cf=(3842.2 - 3620.5, -1792.0 - 3274.1), cf_label='FCF 수익률(영업CF − 설비투자, 최근 2개 분기 연환산)', extra=('2025년 연간 조정 순이익', 39166.303)),
 '1211.HK': dict(cur='RMB', sh=9117.197565, sh_note='발행주식 9,117.2M주(A주 5,433.8M + H주 3,683.4M, 2026-09-30 HKEX 월간 보고). 시가총액은 H주 가격 × 전체 주식 수로 계산',
     debt=120055.0, liq=58737.867 + 69940.449, liq_label='화폐성 자금 + 단기매매 금융자산(회사 제시 "현금 보유" ¥1,674억보다 보수적인 재무상태표 기준)',
     op=(14743.578 - 4695.889, 4695.889), op_label='영업이익(2분기 = 반기 − 1분기, 계산)', ni=(12325.408 - 4084.551, 4084.551), ni_label='귀속 순이익',
     cf=((37334.744 - 2790.305) - (44703.066 - 22062.59), 2790.305 - 22062.59), cf_label='FCF 수익률(영업CF − 설비투자, 최근 2개 분기 연환산)', extra=('2025년 연간 귀속 순이익', 32619.022)),
}
E = json.load(open('data/eda_weekly.json'))['res']; M = json.load(open('data/moves.json'))
out = {}
for t, v in V.items():
    fx = FXR[v['cur']]; price = float(y[t].dropna().loc[:ASOF].iloc[-1])
    mc = price * v['sh'] / 1e3                               # HK$ B
    nc = (v['liq'] - v['debt']) / fx / 1e3; ev = mc - nc
    op = (sum(v['op']) * 2 if len(v['op']) == 2 else v['op'][0] * 4) / fx / 1e3; op_q = v['op'][0] * 4 / fx / 1e3
    ni = sum(v['ni']) * 2 / fx / 1e3; ni_q = v['ni'][0] * 4 / fx / 1e3
    cf = (v['cf_ann'] if 'cf_ann' in v else sum(v['cf']) * 2) / fx / 1e3
    eps = ni / v['sh'] * 1e3; eps_q = ni_q / v['sh'] * 1e3; ncps = nc / v['sh'] * 1e3
    pos = lambda a, b: (a / b) if b > 0 else None
    met = dict(price=price, asof=ASOF, cur=v['cur'], ads_m=v['sh'], mcap_b=mc, mcap_usd_b=mc / HKD, netcash_b=nc, ev_b=ev, ev_op=pos(ev, op), ev_op_q=pos(ev, op_q),
               pe=pos(mc, ni), pe_q=pos(mc, ni_q), pe_excash=pos(mc - nc, ni), fcf_yield=cf / mc, nc_share=nc / mc, eps_h1=eps, eps_q=eps_q, ncps=ncps, fx=fx, usdcny=CNY, usdhkd=HKD,
               debt_rep=v['debt'], liq_rep=v['liq'], liq_label=v['liq_label'], op_label=v['op_label'], ni_label=v['ni_label'], ads_note=v['sh_note'], cf_label=v['cf_label'])
    rows = []
    L = [('최근 2개 분기 연환산', eps), ('최근 분기 × 4', eps_q)]
    e2 = v['extra'][1] / fx / v['sh']; L.append((v['extra'][0], e2)); met['eps_extra'] = e2; met['pe_extra'] = price / e2
    for lab, e in L:
        rows.append(dict(label=lab, eps=round(e, 2), vals=[round(m * e, 2) if e > 0 else None for m in (8, 12, 16)]))
    base = eps if eps > 0 else eps_q
    implied_pe = price / base
    e = E[t]['full']; bc = e['beta_cny']; bs = e['beta_spx']; r2 = e['r2']; rv = M[t]['resid_var_share']; cq = E[t]['corr_q']['OIL']
    A = [dict(k='중국/홍콩 주식 강세 신호', val='강세 · 신뢰도 높음(69% vs 49%)', pts=1.5, max=1.5, rule='프레임워크의 중국/홍콩 입장(관심 종목 공통)'),
         dict(k='저자의 종목 거명', val='직접 거명 없음', pts=0.25, max=0.5, rule='26.07.07 "버려진 현금흐름 자산" 칼럼에서 거명되면 0.5, 아니면 0.25')] + fw_items(bc, SLUG[t])
    evop = met['ev_op'] or met['ev_op_q']; pe = met['pe'] or met['pe_q']
    B = [dict(k='EV/' + v['op_label'].split('(')[0], val=f'{evop:.1f}배', pts=round(clip((25 - evop) / 20), 2), max=1.0, rule='5배 이하 만점, 25배 이상 0점'),
         dict(k='PER(' + v['ni_label'].split('(')[0] + ')', val=f'{pe:.1f}배', pts=round(clip((25 - pe) / 17), 2), max=1.0, rule='8배 이하 만점, 25배 이상 0점'),
         dict(k=v['cf_label'].split('(')[0], val=f'{cf/mc*100:.1f}%', pts=round(clip(cf / mc / 0.10), 2), max=1.0, rule='10% 이상 만점, 0% 이하 0점'),
         dict(k='순현금/시가총액', val=f'{nc/mc*100:.0f}%', pts=round(clip(nc / mc / 0.5), 2), max=1.0, rule='50% 이상 만점')]
    C = [dict(k='미국 주식 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 저자는 미국 주식 약세를 봄'),
         dict(k='항셍 연동성(분기 상관)', val=f'{cq:.2f}', pts=round(clip(cq / 0.7), 2), max=1.0, rule='저자는 홍콩 주식 강세를 봄. 0.7 이상 만점(항셍지수에 이 종목이 포함돼 상관이 부풀 수 있음)'),
         dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {min(rv,1)*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달될수록 높음. 홍콩 종목은 미국 지표를 하루 늦춰 맞춰 비매크로 몫이 구조적으로 큼')]
    sA, sB, sC = (round(sum(x['pts'] for x in L2), 2) for L2 in (A, B, C))
    score = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    out[t] = dict(val=met, scen=dict(rows=rows, implied_pe=implied_pe, ncps=ncps, mults=[8, 12, 16]), score=score)
    print(t, 'price', price, 'mcap HK$B %.1f nc %.1f ev %.1f' % (mc, nc, ev), 'EV/op %s PE %s PEq %s fcf %.3f nc %.3f' % (met['ev_op'] and round(met['ev_op'], 1), met['pe'] and round(met['pe'], 1), met['pe_q'] and round(met['pe_q'], 1), cf / mc, nc / mc), 'score', score['total'], sA, sB, sC)
    for P in score['pillars']:
        for i in P['items']: print('     ', i['k'], i['val'], i['pts'])
json.dump(out, open('data/val_hk3.json', 'w'), ensure_ascii=False)
