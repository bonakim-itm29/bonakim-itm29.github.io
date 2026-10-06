import json, numpy as np, pandas as pd
y = pd.read_pickle('data/prices.pkl'); fr = pd.read_pickle('data/fred.pkl')
E = json.load(open('data/eda_weekly.json')); M = json.load(open('data/moves.json'))
VF = json.load(open('data/verification.json')); VAL = json.load(open('data/val_hk3.json'))
CN = json.load(open('../china/data/page_data.json'))
PFX = {'0992.HK': 'LENOVO', '1810.HK': 'XIAOMI', '1211.HK': 'BYD'}
CS = {'0992.HK': 'US$', '1810.HK': '¥', '1211.HK': '¥'}
UNIT = {'0992.HK': 'US$ millions', '1810.HK': 'RMB millions', '1211.HK': 'RMB millions'}
def row(t, i, p, label, unit=None):
    unit = unit or UNIT[t]
    for r in VF['rows'][PFX[t]]:
        if r['id'] == i and r['period'] == p:
            st = {'agree': '✔ 이중 추출 일치', 'single': '단일 출처', 'null': '자료 없음', 'differ': '⚠ 불일치'}[r['status']]
            src = r['src'] or {}
            note = f"{src.get('file','')} p.{src.get('page','')} · {src.get('row','')}".strip(' ·') + (f" · {r['note']}" if r['note'] else '')
            return dict(id=f'{i} {p}', label=label, blind=r['b'], prior=r['a'], xbrl=None, status=st, unit=unit, note=note[:220])
    raise KeyError((t, i, p))
def g(t, i, p):
    for r in VF['rows'][PFX[t]]:
        if r['id'] == i and r['period'] == p: return r['a'] if r['a'] is not None else r['b']
ROWS = {
 '0992.HK': [('Q1', '2026Q2', '분기 매출(4~6월)'), ('Q2_IDG', '2026Q2', 'IDG(PC·기기) 매출'), ('Q2_ISG', '2026Q2', 'ISG(서버·인프라) 매출'), ('Q2_SSG', '2026Q2', 'SSG(솔루션·서비스) 매출'),
             ('Q3', '2026Q2', '영업이익(HKFRS)'), ('Q6', '2026Q2', '귀속 순이익(HKFRS)'), ('Q7', '2026Q2', 'Non-HKFRS 귀속 순이익'), ('Q7', '2026Q1', 'Non-HKFRS 귀속 순이익(직전 분기)'),
             ('Q9', '2026Q2', '영업현금흐름'), ('B1', '2026-06-30', '현금및현금성자산'), ('B2_Bank deposits', '2026-06-30', '은행예금'), ('B3_Total borrowings', '2026-06-30', '총차입(전환사채 포함)'),
             ('B4_Net (debt)/cash position', '2026-06-30', '순부채(회사 제시)'), ('S1', '2026-09-30', '발행주식 수', 'shares'), ('S3_Warrants', '2026-09-30', '미행사 워런트(주식 환산)', 'shares'),
             ('A1_2026', 'FY2026', 'FY2025/26 매출'), ('A3_2026', 'FY2026', 'FY2025/26 영업현금흐름'), ('A5_2026', 'FY2026', 'FY2025/26 Non-HKFRS 순이익')],
 '1810.HK': [('Q1', '2026Q2', '분기 매출'), ('Q2_Smartphone × AIoT (Subtotal)', '2026Q2', '스마트폰×AIoT 매출'), ('Q2_Smart EV, AI and other new initiatives', '2026Q2', '스마트 EV·AI 등 신사업 매출'),
             ('Q3', '2026Q2', '영업이익(IFRS)'), ('Q5', '2026Q2', '귀속 순이익(IFRS)'), ('Q6', '2026Q2', '조정 순이익'), ('Q8', '2026Q2', '영업현금흐름'), ('Q9', '2026Q2', '설비투자'),
             ('B1', '2026-06-30', '현금및현금성자산'), ('B4_cash resources', '2026-06-30', '현금 자원(회사 제시)'), ('B3_Borrowings (current)', '2026-06-30', '단기 차입'), ('B3_Borrowings (non-current)', '2026-06-30', '장기 차입'),
             ('S1_Total', '2026-08-31', '발행주식 수(A+B)', 'shares'), ('A1_2025', 'FY2025', '2025년 매출'), ('A2_2025', 'FY2025', '2025년 귀속 순이익'), ('A5_2025', 'FY2025', '2025년 조정 순이익')],
 '1211.HK': [('Q1', '2026H1', '반기 매출'), ('Q1', '2026Q1', '1분기 매출'), ('Q2_Automobiles and related products, and other products', '2026H1', '자동차 및 관련 제품 매출'), ('Q2_Electronics and other products', '2026H1', '전자제품 등 매출'),
             ('Q3', '2026H1', '반기 영업이익'), ('Q5', '2026H1', '반기 귀속 순이익'), ('Q5', '2026Q1', '1분기 귀속 순이익'), ('Q8', '2026H1', '반기 영업현금흐름'), ('Q9', '2026H1', '반기 설비투자'),
             ('B1_Monetary funds', '2026-06-30', '화폐성 자금'), ('B2_Financial assets held for trading', '2026-06-30', '단기매매 금융자산'), ('B4_Total borrowings (MD&A)', '2026-06-30', '총차입(회사 제시)'),
             ('B7_Trade payables', '2026-06-30', '매입채무'), ('S1_total', '2026-09-30', '발행주식 수(A+H)', 'shares'), ('A1_2025', 'FY2025', '2025년 매출'), ('A2_2025', 'FY2025', '2025년 귀속 순이익')],
}
FUND = {'0992.HK': (['FY2022', 'FY2023', 'FY2024', 'FY2025', 'FY2026'], 'A5', ['Non-HKFRS 순이익', '귀속 순이익']),
        '1810.HK': (['FY2021', 'FY2022', 'FY2023', 'FY2024', 'FY2025'], 'A5', ['조정 순이익', '귀속 순이익']),
        '1211.HK': (['FY2021', 'FY2022', 'FY2023', 'FY2024', 'FY2025'], 'A3', ['영업현금흐름(2024~25년만 공시)', '귀속 순이익'])}
def snap(asof):
    def pair(s):
        s = s.dropna().loc[:asof]; a = s.iloc[-1]; b = s.loc[:pd.Timestamp(s.index[-1]) - pd.Timedelta(days=365)].iloc[-1]; return [float(a), float(b)]
    return dict(date=asof, CNY=pair(y['CNY=X']), HSI=pair(y['^HSI']), UST10=pair(fr.DGS10), CREDIT=pair(fr.BAA10Y), VIX=pair(y['^VIX']), USD=pair(y['DX-Y.NYB']), COPPER=pair(y['HG=F']), SPX=pair(y['^GSPC']))
SNAP = snap('2026-10-06')
peers = json.load(open('data/cn_totals_v11.json'))
peers.update({k: v['score']['total'] for k, v in VAL.items()})
out = {}
for t in PFX:
    vrows = [row(t, *x) for x in ROWS[t]]
    chk = [dict(name=c['k'], lhs=round(c['a'], 1), rhs=round(c['b'], 1), ok=c['ok']) for c in VF['checks'][PFX[t]]]
    V = VAL[t]['val']
    sanity = [dict(name='환율(보고통화/HK$)', val=V['fx'], ok=0.05 < V['fx'] < 1.0), dict(name='순현금/시가총액', val=V['nc_share'], ok=-1 < V['nc_share'] < 1),
              dict(name='PER(최근 2개 분기 연환산)', val=V['pe'] or 0, ok=0 < (V['pe'] or 0) < 100)]
    yrs, k3, lab = FUND[t]
    fund = dict(years=[int(x[2:]) for x in yrs], tbl=dict(rev={x[2:]: g(t, f'A1_{x[2:]}', x) for x in yrs}, ocf={x[2:]: g(t, f'{k3}_{x[2:]}', x) for x in yrs},
                ni={x[2:]: g(t, f'A2_{x[2:]}', x) for x in yrs}), tags={}, shares=[], sh_note='홍콩 공시에는 XBRL이 없어 연도별 주식 수 시계열을 만들지 않았습니다. 최근 발행주식 수는 밸류에이션 타일을 참고하세요.')
    evs = [dict(date=e['date'], R=e['R'], fit=e['fit'], res=e['res'], share=e['share'], type=e['type'], oil=e['oil'], spx=e['spx'], cn=e['cn'],
                nf=len(e['filings']), fil=[f"HKEX {f['filed']} {f['desc'][:48]}" for f in e['filings']][:3]) for e in M[t]['events']]
    mv = dict(threshold=M[t]['threshold'], counts=M[t]['counts'], resid_var_share=M[t]['resid_var_share'], events=evs)
    ev = json.load(open(f'events_{PFX[t]}.json'))
    px = y[t].dropna(); px = px[px.index >= E['res'][t]['start']]; hsi = y['^HSI'].dropna()
    yrs_n = (px.index[-1] - px.index[0]).days / 365.25; dd = px / px.cummax() - 1
    h0 = hsi.loc[:px.index[0]].iloc[-1]; h1 = hsi.loc[:px.index[-1]].iloc[-1]
    stats = dict(start=str(px.index[0].date()), p0=round(float(px.iloc[0]), 2), p1=round(float(px.iloc[-1]), 2), last=str(px.index[-1].date()), tr=float(px.iloc[-1] / px.iloc[0] - 1),
                 cagr=float((px.iloc[-1] / px.iloc[0]) ** (1 / yrs_n) - 1), mdd=float(dd.min()), mdd_date=str(dd.idxmin().date()), peak=round(float(px.max()), 2), peak_date=str(px.idxmax().date()),
                 cmp_start=str(px.index[0].date()), cagr_c=float((px.iloc[-1] / px.iloc[0]) ** (1 / yrs_n) - 1), xle_cagr=float((h1 / h0) ** (1 / yrs_n) - 1))
    val = dict(mktcap_m=V['mcap_b'] * 1000, shares_m=V['ads_m'])
    out[t] = dict(ticker=t, cs=CS[t], fundlab=lab, eda=E['res'][t], moves=mv, events=ev, verify=dict(rows=vrows, checks=chk, sanity=sanity), fund=fund, val=val, cnval=V,
                  scen=VAL[t]['scen'], score=VAL[t]['score'], stats=stats, snap=SNAP, peers=peers)
    print(t, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in stats.items()})
json.dump(dict(data=out, labels=CN['labels']), open('data/page_data.json', 'w'), ensure_ascii=False, default=float)
print(peers)
