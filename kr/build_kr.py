import json, numpy as np, pandas as pd
y = pd.read_pickle('data/prices.pkl')
E = json.load(open('data/eda_weekly.json')); M = json.load(open('data/moves.json'))
VF = json.load(open('data/verification.json')); VAL = json.load(open('data/val_kr.json'))
CN = json.load(open('../china/data/page_data.json'))
PFX = {'005930.KS': 'SEC', '000660.KS': 'SKH'}
ALLVAL = {}

def row(t, i, p, label, unit='RMB millions'):
    for r in VF['rows'][PFX[t]]:
        if r['id'] == i and r['period'] == p:
            st = {'agree': '✔ 이중 추출 일치', 'single': '단일 출처', 'null': '자료 없음', 'differ': '⚠ 불일치'}[r['status']]
            src = r['src'] or {}
            note = f"{src.get('file','')} p.{src.get('page','')} · {src.get('row','')}".strip(' ·') + (f" · {r['note']}" if r['note'] else '')
            return dict(id=f'{i} {p}', label=label, blind=r['b'], prior=r['a'], xbrl=None, status=st, unit=unit, note=note[:220])
    return dict(id=f'{i} {p}', label=label, blind=None, prior=None, xbrl=None, status='자료 없음', unit=unit, note='')

ROWS = {
 '005930.KS': [('Q1', '2026Q2', '2분기 매출', 'KRW millions'), ('Q3', '2026Q2', '2분기 영업이익', 'KRW millions'), ('Q5', '2026Q2', '2분기 지배순이익', 'KRW millions'),
               ('Q2_DS부문_매출', '2026Q2', 'DS(반도체) 부문 매출', 'KRW millions'), ('Q2_DS부문_영업이익', '2026Q2', 'DS 부문 영업이익', 'KRW millions'), ('Q2_DX부문_영업이익', '2026Q2', 'DX(세트) 부문 영업이익', 'KRW millions'),
               ('Q7_diluted', '2026Q2', '2분기 희석 EPS', 'KRW'), ('H1_영업활동현금흐름', '2026H1', '상반기 영업현금흐름', 'KRW millions'), ('H1_유형자산취득', '2026H1', '상반기 유형자산 취득', 'KRW millions'),
               ('H1_자기주식취득', '2026H1', '상반기 자기주식 취득(현금흐름)', 'KRW millions'), ('B1', '2026-06-30', '현금및현금성자산', 'KRW millions'), ('B2_단기금융상품', '2026-06-30', '단기금융상품', 'KRW millions'),
               ('B3_단기차입금', '2026-06-30', '단기차입금', 'KRW millions'), ('B3_장기차입금', '2026-06-30', '장기차입금', 'KRW millions'), ('S1_유통주식수_보통주', '2026-06-30', '유통 보통주', 'shares'),
               ('S1_유통주식수_우선주', '2026-06-30', '유통 우선주', 'shares'), ('R2_주당배당_보통주', '2026H1', '상반기 누적 주당배당(보통주)', 'KRW'), ('A1_2025', 'FY2025', '2025년 매출', 'KRW millions'), ('A3_2025', 'FY2025', '2025년 지배순이익', 'KRW millions')],
 '000660.KS': [('Q1', '2026Q2', '2분기 매출', 'KRW millions'), ('Q3', '2026Q2', '2분기 영업이익', 'KRW millions'), ('Q5', '2026Q2', '2분기 지배순이익', 'KRW millions'),
               ('Q2_DRAM_매출', '2026Q2', 'DRAM 매출(품목)', 'KRW millions'), ('Q2_NAND Flash_매출', '2026Q2', 'NAND 매출(품목)', 'KRW millions'), ('Q7_희석', '2026Q2', '2분기 희석 EPS', 'KRW'),
               ('H1_영업활동현금흐름', '2026H1', '상반기 영업현금흐름', 'KRW millions'), ('H1_유형자산취득', '2026H1', '상반기 유형자산 취득', 'KRW millions'), ('B1', '2026-06-30', '현금및현금성자산', 'KRW millions'),
               ('B2_단기금융상품', '2026-06-30', '단기금융상품', 'KRW millions'), ('B2_단기투자자산', '2026-06-30', '단기투자자산', 'KRW millions'), ('B3_합계', '2026-06-30', '차입금·사채 합계', 'KRW millions'),
               ('S1_유통주식수_보통주', '2026-06-30', '유통주식', 'shares'), ('R1_자기주식소각수량', '2026H1', '상반기 자사주 소각', 'shares'), ('R2_보통주_당기누적주당현금배당', '2026H1', '상반기 누적 주당배당', 'KRW'),
               ('A1_2025', 'FY2025', '2025년 매출', 'KRW millions'), ('A3_2025', 'FY2025', '2025년 지배순이익', 'KRW millions')],
}
# fix period keys for annual rows (verify stores FY20xx)
def g(t, i, p):
    for r in VF['rows'][PFX[t]]:
        if r['id'] == i and r['period'] == p: return r['a'] if r['a'] is not None else r['b']

out = {}
peers = {k: v['score']['total'] for k, v in ALLVAL.items()}
peers.update({{'005930.KS':'삼성전자','000660.KS':'SK하이닉스'}[k]: v['score']['total'] for k, v in VAL.items()})
for t in ['005930.KS', '000660.KS']:
    P = PFX[t]
    vrows = [row(t, *x) for x in ROWS[t]]
    for r in vrows:
        if r['unit'] == 'HK$' and r['prior'] and abs(r['prior']) > 1e6:
            r['prior'] /= 1e6; r['blind'] = r['blind'] / 1e6 if r['blind'] else r['blind']; r['unit'] = 'HK$ millions'
    chk = [dict(name=c['k'], lhs=round(c['a'], 1), rhs=round(c['b'], 1), ok=c['ok']) for c in VF['checks'][P]]
    rev = g(t, 'Q1', '2026Q2'); op = g(t, 'Q3', '2026Q2'); adj = g(t, 'Q5', '2026Q2')
    V = VAL[t]['val']
    sanity = [dict(name='영업이익률(최근 분기)', val=op / rev, ok=-0.3 < op / rev < 0.85), dict(name='지배순이익/매출(최근 분기)', val=adj / rev, ok=-0.3 < adj / rev < 1.3),
              dict(name='상반기 실효세율', val=V['etr'], ok=0.1 < V['etr'] < 0.35)]
    yrs = [2020, 2021, 2022, 2023, 2024, 2025]
    fund = dict(years=yrs, tbl=dict(rev={str(yy): g(t, f'A1_{yy}', f'FY{yy}') for yy in yrs}, ocf={str(yy): g(t, f'A2_{yy}', f'FY{yy}') for yy in yrs},
                                    ni={str(yy): g(t, f'A3_{yy}', f'FY{yy}') for yy in yrs}), tags={}, shares=[],
                sh_note='연도별 주식 수 시계열은 만들지 않았습니다. 최근 유통주식 수는 위 시가총액 타일과 검증 표를 참고하세요.')
    # moves
    evs = []
    for e in M[t]['events']:
        evs.append(dict(date=e['date'], R=e['R'], fit=e['fit'], res=e['res'], share=e['share'], type=e['type'], oil=e['oil'], spx=e['spx'], cn=e['cn'],
                        nf=len(e['filings']), fil=[f"KIND {f['filed']} {f['desc'][:48]}" for f in e['filings']][:3]))
    mv = dict(threshold=M[t]['threshold'], counts=M[t]['counts'], resid_var_share=M[t]['resid_var_share'], events=evs)
    ev = json.load(open(f'events_{P}.json'))
    # stats
    px = y[t].dropna(); px = px[px.index >= E['res'][t]['start']]
    hsi = y['^KS11'].dropna()
    yrs_n = (px.index[-1] - px.index[0]).days / 365.25
    dd = px / px.cummax() - 1
    h0 = hsi.loc[:px.index[0]].iloc[-1]; h1 = hsi.iloc[-1]
    stats = dict(start=str(px.index[0].date()), p0=round(float(px.iloc[0]), 2), p1=round(float(px.iloc[-1]), 2), last=str(px.index[-1].date()), tr=float(px.iloc[-1] / px.iloc[0] - 1),
                 cagr=float((px.iloc[-1] / px.iloc[0]) ** (1 / yrs_n) - 1), mdd=float(dd.min()), mdd_date=str(dd.idxmin().date()), peak=round(float(px.max()), 2), peak_date=str(px.idxmax().date()),
                 cmp_start=str(px.index[0].date()), cagr_c=float((px.iloc[-1] / px.iloc[0]) ** (1 / yrs_n) - 1), xle_cagr=float((h1 / h0) ** (1 / yrs_n) - 1))
    snap = CN['data']['JD']['snap']
    val = dict(mktcap_m=V['mcap_b'] * 1000, shares_m=V['ads_m'])
    out[t] = dict(ticker=t, eda=E['res'][t], moves=mv, events=ev, verify=dict(rows=vrows, checks=chk, sanity=sanity), fund=fund, val=val, cnval=V,
                  scen=VAL[t]['scen'], score=VAL[t]['score'], stats=stats, snap=snap, peers=peers)
    print(t, stats, V['mcap_b'])
json.dump(dict(data=out, labels=CN['labels']), open('data/page_data.json', 'w'), ensure_ascii=False, default=float)
print(peers)
