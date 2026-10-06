"""Assemble data/page_data.json for PDD / NTES / TCOM (fields as in ../hk/build_hk.py and ../china page_data)."""
import json, pandas as pd
y = pd.read_pickle('data/prices.pkl'); fr = pd.read_pickle('data/fred.pkl')
ASOF = pd.Timestamp('2026-10-02')
E = json.load(open('data/eda_weekly.json')); M = json.load(open('data/moves.json'))
VF = json.load(open('data/verification.json')); FU = json.load(open('data/fundamentals.json')); VAL = json.load(open('data/val_cn2.json'))
CN = json.load(open('../china/data/page_data.json'))
peers = {k: v['score']['total'] for k, v in json.load(open('../china/data/val_cn.json')).items()}
peers.update({k: v['score']['total'] for k, v in json.load(open('../hk/data/val_hk.json')).items()})
peers.update({k: v['score']['total'] for k, v in VAL.items()})
UNIT = {'S1': 'shares', 'R2': 'US$ per ADS', 'X1': 'RMB per US$1'}
SH_NOTE = {'PDD': '보통주 수 ÷4(ADS 1주 = 보통주 4주)로 환산했습니다. 2018년 7월 상장 전후로 우선주 전환이 반영돼 크게 늘었습니다. 일부 연도는 XBRL에 천 주 단위로 태그돼 있어 ×1,000으로 맞췄습니다.',
           'NTES': '보통주 수 ÷5(현재 ADS 1주 = 보통주 5주)로 환산했습니다. 과거 ADS 비율이 달랐던 기간도 현재 비율로 맞춘 값입니다.',
           'TCOM': '2021년 보통주 1:8 분할 이후 ADS 1주 = 보통주 1주입니다. 2018년 이전 값은 분할 전 보통주라 ×8로 맞췄습니다(2019·2020년은 이후 20-F에서 분할 반영해 재작성된 값).'}
out = {}
for t in ['PDD', 'NTES', 'TCOM']:
    vrows = []
    for r in VF[t]:
        st, note = r['status'], r['note']
        if t == 'TCOM' and r['id'] == 'S1':
            st = '⚠ 기준일 다름'
            note = '1차: 2025-12-31 649,583,574주(20-F 표지) / 재추출: 2026-03-31 629,705,222주(20-F Item 6.E, 예탁기관 대량발행분 제외). 둘 다 원문과 일치하며 최근 값을 사용.'
        vrows.append(dict(id=r['id'], label=r['label'], blind=r['b'], prior=r['a'], xbrl=(abs(r['xbrl']) * (1 if (r['a'] or 0) >= 0 else -1) if r['xbrl'] is not None else None),
                          status=st, unit=r['unit'] or UNIT.get(r['id'], ''), note=note))
    g = {r['id']: (r['a'] if r['a'] is not None else r['b']) for r in VF[t]}
    nx = sum(1 for r in VF[t] if r['xbrl'] is not None); nxok = sum(1 for r in VF[t] if r['status'].startswith('✔ XBRL'))
    chk = []
    if t == 'PDD':
        chk.append(dict(name='현금 + 단기투자 = 회사 문장 "RMB456.4bn"', lhs=g['B1'] + g['B2a'], rhs=456400, ok=abs(g['B1'] + g['B2a'] - 456400) <= 50, unit='¥M'))
        chk.append(dict(name='Non-GAAP 영업이익 = 영업이익 + 주식보상(¥1,307M)', lhs=g['Q4'], rhs=g['Q3'] + 1307, ok=g['Q4'] == g['Q3'] + 1307, unit='¥M'))
    if t == 'NTES':
        s = g['B1'] + g['B2a'] + g['B2b'] + g['B2c'] + g['B2d'] + g['B2e'] - g['B3a']
        chk.append(dict(name='순현금 재계산(현금·정기예금·제한현금·단기투자 − 단기차입) = 회사 제시 ¥167.5B', lhs=round(s, 1), rhs=g['B4'], ok=abs(s - g['B4']) <= 50, unit='¥M'))
    if t == 'TCOM':
        chk.append(dict(name='조정 EBITDA = 영업손익 + 주식보상 + 감가상각 + 과징금(−1,462 + 647 + 200 + 5,180)', lhs=g['Q4'], rhs=-1462 + 647 + 200 + 5180, ok=g['Q4'] == -1462 + 647 + 200 + 5180, unit='¥M'))
        chk.append(dict(name='③ 상반기 조정 EBITDA(원문 ¥9,395M) = 1분기 + 2분기', lhs=4830 + g['Q4'], rhs=9395, ok=4830 + g['Q4'] == 9395, unit='¥M'))
        chk.append(dict(name='유동성 합계 = 회사 문장 "RMB100.5bn"', lhs=g['B1'] + g['B2a'] + g['B2f'], rhs=100500, ok=abs(g['B1'] + g['B2a'] + g['B2f'] - 100500) <= 50, unit='¥M'))
    chk.append(dict(name=f'20-F 연간 수치 = XBRL({nx}개 항목)', lhs=nxok, rhs=nx, ok=nxok == nx, unit='개'))
    sanity = [dict(name='영업이익/매출(최근 분기)', val=g['Q3'] / g['Q1'], ok=-0.3 < g['Q3'] / g['Q1'] < 0.6),
              dict(name='Non-GAAP 순이익/매출(최근 분기)', val=g['Q6'] / g['Q1'], ok=-0.3 < g['Q6'] / g['Q1'] < 0.5),
              dict(name='편의환산 환율(RMB/US$)', val=g['X1'], ok=6.0 < g['X1'] < 7.6)]
    F = FU[t]; fund = dict(years=F['years'], tbl=F['tbl'], tags=F['tags'], shares=F['shares'], sh_note=SH_NOTE[t])
    evs = [dict(date=e['date'], R=e['R'], fit=e['fit'], res=e['res'], share=e['share'], type=e['type'], oil=e['oil'], spx=e['spx'], cn=e['cn'],
                nf=len(e['filings']), fil=[f"{f['form']} {f['filed']}" for f in e['filings']][:3]) for e in M[t]['events']]
    mv = dict(threshold=M[t]['threshold'], counts=M[t]['counts'], resid_var_share=M[t]['resid_var_share'], events=evs)
    ev = json.load(open(f'events_{t}.json'))
    px = y[t].dropna().loc[:ASOF]; kw = y['KWEB'].dropna().loc[:ASOF]
    yrs_n = (px.index[-1] - px.index[0]).days / 365.25
    dd = px / px.cummax() - 1
    cs = max(px.index[0], kw.index[0]); pc = px.loc[cs:]; kc = kw.loc[cs:]; yc = (pc.index[-1] - pc.index[0]).days / 365.25
    stats = dict(start=str(px.index[0].date()), p0=round(float(px.iloc[0]), 2), p1=round(float(px.iloc[-1]), 2), last=str(px.index[-1].date()), tr=float(px.iloc[-1] / px.iloc[0] - 1),
                 cagr=float((px.iloc[-1] / px.iloc[0]) ** (1 / yrs_n) - 1), mdd=float(dd.min()), mdd_date=str(dd.idxmin().date()), peak=round(float(px.max()), 2), peak_date=str(px.idxmax().date()),
                 cmp_start=str(pc.index[0].date()), cagr_c=float((pc.iloc[-1] / pc.iloc[0]) ** (1 / yc) - 1), xle_cagr=float((kc.iloc[-1] / kc.iloc[0]) ** (1 / yc) - 1))
    def sv(s):
        s = s.dropna(); return [float(s.loc[:ASOF].iloc[-1]), float(s.loc[:ASOF - pd.Timedelta(days=365)].iloc[-1])]
    snap = dict(date=str(ASOF.date()), CNY=sv(y['CNY=X']), HSI=sv(y['^HSI']), UST10=sv(fr.DGS10), CREDIT=sv(fr.BAA10Y), VIX=sv(y['^VIX']), USD=sv(y['DX-Y.NYB']), COPPER=sv(y['HG=F']), SPX=sv(y['^GSPC']))
    V = VAL[t]['val']
    val = dict(mktcap_m=V['mcap_b'] * 1000, shares_m=V['ads_m'], ev_ebitdax_q2ann=V['ev_op'], nd_ebitdax_h1ann=V['pe'])
    out[t] = dict(ticker=t, eda=E['res'][t], moves=mv, events=ev, verify=dict(rows=vrows, checks=chk, sanity=sanity), fund=fund, val=val, cnval=V,
                  scen=VAL[t]['scen'], score=VAL[t]['score'], stats=stats, snap=snap, peers=peers)
    print(t, stats, '\n  ', snap, '\n  ', chk)
json.dump(dict(data=out, labels=CN['labels']), open('data/page_data.json', 'w'), ensure_ascii=False, default=float)
print(peers)
