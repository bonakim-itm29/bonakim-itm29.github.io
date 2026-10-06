import json, pandas as pd, numpy as np
clip = lambda x, a=0.0, b=1.0: max(a, min(b, x))
y = pd.read_pickle('data/prices.pkl')
FX = float(y['CNY=X'].dropna().iloc[-1])   # RMB per USD, 2026-09-25
V = {
 'BABA': dict(price=float(y.BABA.dropna().iloc[-1]), ads=19884.988918 / 8, ads_note='발행주식 19,885.0M주(8/26 신주 배정 완료 공시, 6-K Ex.99.2), ADS 1 = 8주(계산)',
              debt=30614 + 56007 + 115716 + 54905 + 9288, liq=474505, liq_label='회사 제시 "현금 및 기타 유동투자"',
              op=(27329, 5102), op_label='조정 EBITA', ni=(20715, 86), ni_label='Non-GAAP 순이익(비지배 포함)', fcf=(-44670, -17300), capexq=-67660, ni_q_attr=20583),
 'BIDU': dict(price=float(y.BIDU.dropna().iloc[-1]), ads=2713.49225 / 8, ads_note='발행주식 2,713.5M주(2026-07-14 기준, EGM 통지문), ADS 1 = 8주',
              debt=26311 + 2027 + 1 + 2038 + 20779 + 46089 + 6615, liq=283100, liq_label='회사 제시 "현금 및 투자 합계"(장기 정기예금·만기보유 포함)',
              op=(3785, 3807), op_label='Non-GAAP 영업이익', ni=(2573, 4332), ni_label='Non-GAAP 귀속 순이익', fcf=(-7954, -3246), capexq=-11390),
 'JD':   dict(price=float(y.JD.dropna().iloc[-1]), ads=2688 / 2, ads_note='발행주식 2,688M주(2026-06-30), ADS 1 = 2주',
              debt=3534 + 13555 + 16607 + 36196, liq=235100, liq_label='회사 제시 "현금·제한현금·단기투자 합계"',
              op=(5483, 5628), op_label='Non-GAAP 영업이익', ni=(8930, 7379), ni_label='Non-GAAP 귀속 순이익', fcf=(31835, -6481), capexq=-5520),
}
E = json.load(open('data/eda_weekly.json'))['res']; M = json.load(open('data/moves.json'))
FW = {'BABA': 0.5, 'BIDU': 0.25, 'JD': 0.5}   # 저자가 최근 플랫폼 thesis에서 직접 거명(26.07.07: Tencent·JD·BABA·Meituan)
out = {}
for t, v in V.items():
    mc = v['price'] * v['ads'] / 1e3                       # $B
    nc = (v['liq'] - v['debt']) / FX / 1e3                 # $B
    ev = mc - nc
    op = sum(v['op']) * 2 / FX / 1e3; op_q = v['op'][0] * 4 / FX / 1e3
    ni = sum(v['ni']) * 2 / FX / 1e3; ni_q = v['ni'][0] * 4 / FX / 1e3
    fcf = sum(v['fcf']) * 2 / FX / 1e3
    eps = ni / v['ads'] * 1e3; eps_q = ni_q / v['ads'] * 1e3; ncps = nc / v['ads'] * 1e3
    met = dict(price=v['price'], ads_m=v['ads'], mcap_b=mc, netcash_b=nc, ev_b=ev, ev_op=ev / op, ev_op_q=ev / op_q, pe=mc / ni, pe_q=mc / ni_q,
               pe_excash=(mc - nc) / ni, fcf_yield=fcf / mc, nc_share=nc / mc, eps_h1=eps, eps_q=eps_q, ncps=ncps, fx=FX,
               debt_rmb=v['debt'], liq_rmb=v['liq'], liq_label=v['liq_label'], op_label=v['op_label'], ni_label=v['ni_label'], ads_note=v['ads_note'])
    # 밸류에이션 시나리오: 순현금/ADS + PER m × EPS
    rows = []
    for lab, e in [('최근 2개 분기 연환산', eps), ('최근 분기 × 4', eps_q)]:
        rows.append(dict(label=lab, eps=round(e, 2), vals=[round(ncps + m * e, 2) for m in (8, 12, 16)]))
    implied_pe = (v['price'] - ncps) / eps
    # 점수
    e = E[t]['full']; bc = e['beta_cny']; bs = e['beta_spx']; r2 = e['r2']; rv = M[t]['resid_var_share']; cq = E[t]['corr_q']['OIL']
    A = [dict(k='중국/홍콩 주식 강세 신호', val='강세 · 신뢰도 높음(69% vs 49%)', pts=1.5, max=1.5, rule='프레임워크의 중국/홍콩 입장(관심 종목 공통)'),
         dict(k='저자의 종목 거명', val=('플랫폼 thesis에 직접 거명' if FW[t] == 0.5 else '직접 거명 없음'), pts=FW[t], max=0.5, rule='26.07.07 "버려진 현금흐름 자산" 칼럼에서 거명되면 0.5, 아니면 0.25'),
         dict(k='달러 약세·위안화 강세 수혜(위안화 베타)', val=f'{bc:.2f}', pts=round(clip(-bc / 3), 2), max=1.0, rule='저자는 달러 약세를 전망. 위안화 1% 강세 시 주가 반응이 클수록 높음(−3 이하 만점)')]
    B = [dict(k='EV/조정 영업이익', val=f'{ev/op:.1f}배', pts=round(clip((25 - ev / op) / 20), 2), max=1.0, rule='5배 이하 만점, 25배 이상 0점'),
         dict(k='PER(Non-GAAP)', val=f'{mc/ni:.1f}배', pts=round(clip((25 - mc / ni) / 17), 2), max=1.0, rule='8배 이하 만점, 25배 이상 0점'),
         dict(k='FCF 수익률', val=f'{fcf/mc*100:.1f}%', pts=round(clip(fcf / mc / 0.10), 2), max=1.0, rule='10% 이상 만점, 0% 이하 0점'),
         dict(k='순현금/시가총액', val=f'{nc/mc*100:.0f}%', pts=round(clip(nc / mc / 0.5), 2), max=1.0, rule='50% 이상 만점')]
    C = [dict(k='미국 주식 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 저자는 미국 주식 약세를 봄'),
         dict(k='항셍 연동성(분기 상관)', val=f'{cq:.2f}', pts=round(clip(cq / 0.7), 2), max=1.0, rule='저자는 홍콩 주식 강세를 봄. 0.7 이상 만점'),
         dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {rv*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달될수록 높음')]
    sA, sB, sC = (round(sum(x['pts'] for x in L), 2) for L in (A, B, C))
    score = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    out[t] = dict(val=met, scen=dict(rows=rows, implied_pe=implied_pe, ncps=ncps, mults=[8, 12, 16]), score=score)
    print(t, {k: (round(v2, 2) if isinstance(v2, float) else v2) for k, v2 in met.items() if not isinstance(v2, str)}, 'implied PE %.1f' % implied_pe, 'score', score['total'], sA, sB, sC)
    for r in rows: print('   ', r)
json.dump(out, open('data/val_cn.json', 'w'), ensure_ascii=False)
