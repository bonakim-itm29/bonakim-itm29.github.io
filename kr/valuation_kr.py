import json, pandas as pd
clip = lambda x, a=0.0, b=1.0: max(a, min(b, x))
y = pd.read_pickle('data/prices.pkl')
D0 = '2026-09-23'   # 추석 연휴(9/24~26) 전 마지막 거래일
px = lambda t: float(y[t].dropna().loc[:D0].iloc[-1])
KRW = float(y['KRW=X'].dropna().loc[:D0].iloc[-1])
T = 1e6   # 백만원 → 조원
V = {
 '005930.KS': dict(price=px('005930.KS'), pref=px('005935.KS'), sh_c=5764191903, sh_p=802371203,
                   sh_note='유통주식 보통주 5,764.2M주 + 우선주 802.4M주(2026-06-30, 반기보고서 "주식의 총수 등"). 시가총액은 보통주·우선주 각각의 종가로 계산',
                   liq=92916382 + 97036646 + 46000, liq_label='현금및현금성자산 + 단기금융상품 + 단기 당기손익-공정가치 금융자산',
                   debt=13710121 + 1205829 + 7668 + 7485103, op=(89492412, 57232797), etr=34418506 / 153268239,
                   ni=(71269468, 47101190), fcf=145355192 - 31234818 - 1725464, fy=('2025년 연간 지배순이익', 44260956), author=0.25,
                   author_val='2024.11 "45,000원 부근 적극 매수"·장기 성장성 신뢰, 2026년 메모리 버블 경계'),
 '000660.KS': dict(price=px('000660.KS'), pref=None, sh_c=711075500 + 17790000, sh_p=0,
                   sh_note='유통주식 711.1M주(2026-06-30) + 7월 ADR 발행 신주 17.79M주 = 728.9M주(반기보고서 보고기간 후 사건). 8/19 결정한 자사주 매입·소각은 반영 전',
                   liq=26835986 + 22397559 + 38724378 + 39890535, liq_label='현금및현금성자산 + 단기금융상품 + 단기투자자산(6월 말) + 7월 ADR 발행총액 39.9조 원(수수료 차감 전)',
                   debt=18586634, op=(60542608, 37610283), etr=40056711 / 174325213,
                   ni=(93820236, 40330176), fcf=91742501 - 18328836 - 665180, fy=('2025년 연간 지배순이익', 42919287), author=0.0,
                   author_val='직접 매수 의견 없음, 2026년 메모리 버블 경계'),
}
E = json.load(open('data/eda_weekly.json'))['res']; M = json.load(open('data/moves.json'))
out = {}
for t, v in V.items():
    mc = (v['price'] * v['sh_c'] + (v['pref'] or 0) * v['sh_p']) / 1e12          # 조원
    shs = v['sh_c'] + v['sh_p']
    nc = (v['liq'] - v['debt']) / T; ev = mc - nc
    op = sum(v['op']) * 2 / T; op_q = v['op'][0] * 4 / T
    core = op * (1 - v['etr']); core_q = op_q * (1 - v['etr'])
    ni = sum(v['ni']) * 2 / T; ni_q = v['ni'][0] * 4 / T
    fcf = v['fcf'] * 2 / T
    eps = core / shs * 1e12; eps_q = core_q / shs * 1e12; ncps = nc / shs * 1e12; eps_fy = v['fy'][1] / T / shs * 1e12
    met = dict(price=v['price'], ads_m=shs / 1e6, mcap_b=mc, mcap_usd_b=mc * 1e12 / KRW / 1e9, netcash_b=nc, ev_b=ev, ev_op=ev / op, ev_op_q=ev / op_q,
               pe=mc / core, pe_q=mc / core_q, pe_rep=mc / ni, pe_rep_q=mc / ni_q, pe_excash=(mc - nc) / core, fcf_yield=fcf / mc, nc_share=nc / mc,
               eps_h1=eps, eps_q=eps_q, ncps=ncps, etr=v['etr'], krw=KRW, debt_rmb=v['debt'], liq_rmb=v['liq'], liq_label=v['liq_label'],
               op_label='영업이익', ni_label='핵심 이익(영업이익 × (1 − 상반기 실효세율))', ads_note=v['sh_note'], cf_label='FCF 수익률', pe_fy=mc * 1e12 / (v['fy'][1] * 1e6))
    rows = [dict(label=lab, eps=round(e), vals=[round(ncps + m * e) for m in (8, 12, 16)]) for lab, e in
            [('최근 2개 분기 연환산', eps), ('최근 분기 × 4', eps_q), (v['fy'][0] + '(사이클 이전)', eps_fy)]]
    implied_pe = (v['price'] - ncps) / eps
    e = E[t]['full']; bk = e['beta_cny']; bs = e['beta_spx']; r2 = e['r2']; rv = M[t]['resid_var_share']; cq = E[t]['corr_q']['OIL']
    A = [dict(k='한국 주식 신호', val='장기 강세(87% vs 59%) · 2026년 FOMO 경계', pts=0.5, max=1.5, rule='장기 강세 판단의 신뢰도는 높지만 2026년에는 코스피·반도체 과열을 경계. 강세 1.5, 중립 0.75, 경계 0.5, 약세 0'),
         dict(k='저자의 종목 평가', val=v['author_val'], pts=v['author'], max=0.5, rule='직접 매수 의견 0.5, 조건부·과거 긍정 0.25, 없음·경계 0'),
         dict(k='달러 약세·원화 강세 수혜(원화 베타)', val=f'{bk:.2f}', pts=round(clip(-bk / 3), 2), max=1.0, rule='저자는 달러 약세를 전망. 원화 1% 강세 시 주가 반응이 클수록 높음(−3 이하 만점)')]
    B = [dict(k='EV/영업이익', val=f'{ev/op:.1f}배', pts=round(clip((25 - ev / op) / 20), 2), max=1.0, rule='5배 이하 만점, 25배 이상 0점(최근 2개 분기 연환산)'),
         dict(k='PER(핵심 이익)', val=f'{mc/core:.1f}배', pts=round(clip((25 - mc / core) / 17), 2), max=1.0, rule='8배 이하 만점, 25배 이상 0점'),
         dict(k='FCF 수익률', val=f'{fcf/mc*100:.1f}%', pts=round(clip(fcf / mc / 0.10), 2), max=1.0, rule='10% 이상 만점, 0% 이하 0점'),
         dict(k='순현금/시가총액', val=f'{nc/mc*100:.0f}%', pts=round(clip(nc / mc / 0.5), 2), max=1.0, rule='50% 이상 만점')]
    C = [dict(k='미국 주식 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 저자는 미국 주식 약세를 봄'),
         dict(k='코스피 연동성(분기 상관)', val=f'{cq:.2f}', pts=round(clip(cq / 0.7) * 0.5, 2), max=1.0, rule='저자가 2026년 코스피를 경계하므로 절반만 인정. 코스피에 이 종목 비중이 커 상관이 부풀려짐'),
         dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {min(rv,1)*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달될수록 높음. 미국 지표를 하루 늦춰 맞춰 비매크로 몫이 구조적으로 큼')]
    sA, sB, sC = (round(sum(x['pts'] for x in L), 2) for L in (A, B, C))
    score = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    out[t] = dict(val=met, scen=dict(rows=rows, implied_pe=implied_pe, ncps=ncps, mults=[8, 12, 16]), score=score)
    print(t, {k: (round(x, 2) if isinstance(x, float) else x) for k, x in met.items() if not isinstance(x, str)}, 'implied %.1f' % implied_pe, 'score', score['total'], sA, sB, sC)
    for r in rows: print('   ', r)
json.dump(out, open('data/val_kr.json', 'w'), ensure_ascii=False)
