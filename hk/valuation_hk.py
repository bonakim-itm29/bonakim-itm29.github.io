import json, pandas as pd, numpy as np
clip = lambda x, a=0.0, b=1.0: max(a, min(b, x))
y = pd.read_pickle('data/prices.pkl')
CNY = float(y['CNY=X'].dropna().loc[:'2026-09-25'].iloc[-1]); HKD = float(y['HKD=X'].dropna().loc[:'2026-09-25'].iloc[-1])
FX = CNY / HKD            # RMB per HKD
V = {
 '0700.HK': dict(price=float(y['0700.HK'].dropna().iloc[-1]), sh=9103.150424, sh_note='발행주식 9,103.2M주(2026-08-31, HKEX 월간 주식변동 보고)',
                 debt=86292 + 212650 + 0 + 154021, liq=206930 + 304224, liq_label='현금및현금성자산 + 정기예금 등(회사 제시 순현금과 같은 정의)',
                 op=(75636, 75627), op_label='Non-IFRS 영업이익', ni=(68415, 67905), ni_label='Non-IFRS 귀속 순이익',
                 cf=(-13800, 56700), cf_label='FCF 수익률', extra=None),
 '3690.HK': dict(price=float(y['3690.HK'].dropna().iloc[-1]), sh=6175.4848, sh_note='발행주식 6,175.5M주(Class A 579.2M + Class B 5,596.3M, 2026-08-31 HKEX 월간 주식변동 보고)',
                 debt=6833.774 + 35304.527 + 502.943 + 46060.011, liq=104716.797 + 63597.373, liq_label='현금및현금성자산 + 단기 금융투자(제한현금 제외, 회사는 순현금을 제시하지 않음)',
                 op=(4098.05, -3049.429), op_label='조정 EBITDA', ni=(2523.716, -4967.986), ni_label='조정 순이익',
                 cf=(9733.444, -7014.359), cf_label='영업현금흐름 수익률(FCF 미공시)', extra=('2024년 조정 순이익(가격 전쟁 전)', 43772.449)),
}
E = json.load(open('data/eda_weekly.json'))['res']; M = json.load(open('data/moves.json'))
out = {}
for t, v in V.items():
    mc = v['price'] * v['sh'] / 1e3                       # HK$ B
    nc = (v['liq'] - v['debt']) / FX / 1e3                 # HK$ B
    ev = mc - nc
    op = sum(v['op']) * 2 / FX / 1e3; op_q = v['op'][0] * 4 / FX / 1e3
    ni = sum(v['ni']) * 2 / FX / 1e3; ni_q = v['ni'][0] * 4 / FX / 1e3
    cf = sum(v['cf']) * 2 / FX / 1e3
    eps = ni / v['sh'] * 1e3; eps_q = ni_q / v['sh'] * 1e3; ncps = nc / v['sh'] * 1e3
    pos = lambda a, b: (a / b) if b > 0 else None
    met = dict(price=v['price'], ads_m=v['sh'], mcap_b=mc, mcap_usd_b=mc / HKD, netcash_b=nc, ev_b=ev, ev_op=pos(ev, op), ev_op_q=pos(ev, op_q), pe=pos(mc, ni), pe_q=pos(mc, ni_q),
               pe_excash=pos(mc - nc, ni), fcf_yield=cf / mc, nc_share=nc / mc, eps_h1=eps, eps_q=eps_q, ncps=ncps, fx=FX, usdcny=CNY, usdhkd=HKD,
               debt_rmb=v['debt'], liq_rmb=v['liq'], liq_label=v['liq_label'], op_label=v['op_label'], ni_label=v['ni_label'], ads_note=v['sh_note'], cf_label=v['cf_label'])
    rows = []
    L = [('최근 2개 분기 연환산', eps), ('최근 분기 × 4', eps_q)]
    if v['extra']:
        e2 = v['extra'][1] / FX / v['sh']; L.append((v['extra'][0], e2)); met['eps_extra'] = e2; met['pe_extra'] = v['price'] / e2
    for lab, e in L:
        rows.append(dict(label=lab, eps=round(e, 2), vals=[round(ncps + m * e, 2) if e > 0 else None for m in (8, 12, 16)]))
    base = eps if eps > 0 else eps_q
    implied_pe = (v['price'] - ncps) / base
    e = E[t]['full']; bc = e['beta_cny']; bs = e['beta_spx']; r2 = e['r2']; rv = M[t]['resid_var_share']; cq = E[t]['corr_q']['OIL']
    A = [dict(k='중국/홍콩 주식 강세 신호', val='강세 · 신뢰도 높음(69% vs 49%)', pts=1.5, max=1.5, rule='프레임워크의 중국/홍콩 입장(관심 종목 공통)'),
         dict(k='저자의 종목 거명', val='플랫폼 thesis에 직접 거명', pts=0.5, max=0.5, rule='26.07.07 "버려진 현금흐름 자산" 칼럼에서 거명되면 0.5, 아니면 0.25'),
         dict(k='달러 약세·위안화 강세 수혜(위안화 베타)', val=f'{bc:.2f}', pts=round(clip(-bc / 3), 2), max=1.0, rule='저자는 달러 약세를 전망. 위안화 1% 강세 시 주가 반응이 클수록 높음(−3 이하 만점)')]
    evop = met['ev_op'] if met['ev_op'] else met['ev_op_q']; pe = met['pe'] if met['pe'] else met['pe_q']
    lab_op = '' if met['ev_op'] else ' (최근 분기×4, 반기 합계 적자)'
    B = [dict(k='EV/조정 영업이익', val=f'{evop:.1f}배{lab_op}', pts=round(clip((25 - evop) / 20), 2), max=1.0, rule='5배 이하 만점, 25배 이상 0점'),
         dict(k='PER(조정 이익)', val=f'{pe:.1f}배{"" if met["pe"] else " (최근 분기×4, 반기 합계 적자)"}', pts=round(clip((25 - pe) / 17), 2), max=1.0, rule='8배 이하 만점, 25배 이상 0점'),
         dict(k=v['cf_label'], val=f'{cf/mc*100:.1f}%', pts=round(clip(cf / mc / 0.10), 2), max=1.0, rule='10% 이상 만점, 0% 이하 0점'),
         dict(k='순현금/시가총액', val=f'{nc/mc*100:.0f}%', pts=round(clip(nc / mc / 0.5), 2), max=1.0, rule='50% 이상 만점')]
    C = [dict(k='미국 주식 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 저자는 미국 주식 약세를 봄'),
         dict(k='항셍 연동성(분기 상관)', val=f'{cq:.2f}', pts=round(clip(cq / 0.7), 2), max=1.0, rule='저자는 홍콩 주식 강세를 봄. 0.7 이상 만점(항셍지수에 이 종목이 포함돼 상관이 부풀 수 있음)'),
         dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {min(rv,1)*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달될수록 높음. 홍콩 종목은 미국 지표를 하루 늦춰 맞춰 비매크로 몫이 구조적으로 큼')]
    sA, sB, sC = (round(sum(x['pts'] for x in L2), 2) for L2 in (A, B, C))
    score = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    out[t] = dict(val=met, scen=dict(rows=rows, implied_pe=implied_pe, ncps=ncps, mults=[8, 12, 16]), score=score)
    print(t, {k: (round(v2, 2) if isinstance(v2, float) else v2) for k, v2 in met.items() if not isinstance(v2, str)}, 'implied PE %.1f' % implied_pe, 'score', score['total'], sA, sB, sC)
    for r in rows: print('   ', r)
    for P in score['pillars']:
        for i in P['items']: print('     ', i['k'], i['val'], i['pts'])
json.dump(out, open('data/val_hk.json', 'w'), ensure_ascii=False)
