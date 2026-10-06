import json, numpy as np, pandas as pd
D = 'data/'
y = pd.read_pickle(D + 'yahoo.pkl'); fr = pd.read_pickle(D + 'fred.pkl')
y = y[y.index.dayofweek < 5]
E = json.load(open(D + 'eda_weekly.json')); M = json.load(open(D + 'moves.json'))
V = json.load(open(D + 'verification.json')); FUND = json.load(open(D + 'fundamentals.json'))
VAL = json.load(open('../valuation/valuation_metrics.json'))
START = {'CRGY': '2021-12-08', 'KOS': '2011-05-11', 'REI': '2012-07-02', 'SM': '1993-01-04'}

def stats(t):
    p = y[t].dropna(); p = p[p.index >= START[t]]
    yrs = (p.index[-1] - p.index[0]).days / 365.25
    dd = p / p.cummax() - 1
    x = y['XLE'].dropna(); c0 = max(p.index[0], x.index[0])
    pc = p[p.index >= c0]; xc = x[x.index >= c0]; yc = (pc.index[-1] - pc.index[0]).days / 365.25
    return dict(start=str(p.index[0].date()), p0=round(float(p.iloc[0]), 2), p1=round(float(p.iloc[-1]), 2), last=str(p.index[-1].date()),
                tr=float(p.iloc[-1] / p.iloc[0] - 1), cagr=float((p.iloc[-1] / p.iloc[0]) ** (1 / yrs) - 1),
                mdd=float(dd.min()), mdd_date=str(dd.idxmin().date()), peak=round(float(p.max()), 2), peak_date=str(p.idxmax().date()),
                cmp_start=str(c0.date()), cagr_c=float((pc.iloc[-1] / pc.iloc[0]) ** (1 / yc) - 1), xle_cagr=float((xc.iloc[-1] / xc.iloc[0]) ** (1 / yc) - 1))

snap_f = fr[['DCOILWTICO', 'DCOILBRENTEU', 'DHHNGSP', 'DGS10', 'BAA10Y', 'VIXCLS', 'T10YIE']].ffill()
def snap():
    last = snap_f.iloc[-1]; yago = snap_f.loc[:snap_f.index[-1] - pd.Timedelta(days=365)].iloc[-1]
    dx = y['DX-Y.NYB'].dropna(); spx = y['^GSPC'].dropna()
    return dict(date=str(snap_f.index[-1].date()),
                WTI=[float(last.DCOILWTICO), float(yago.DCOILWTICO)], BRENT=[float(last.DCOILBRENTEU), float(yago.DCOILBRENTEU)],
                HH=[float(last.DHHNGSP), float(yago.DHHNGSP)], UST10=[float(last.DGS10), float(yago.DGS10)],
                CREDIT=[float(last.BAA10Y), float(yago.BAA10Y)], VIX=[float(last.VIXCLS), float(yago.VIXCLS)], BEI=[float(last.T10YIE), float(yago.T10YIE)],
                USD=[float(dx.iloc[-1]), float(dx.loc[:dx.index[-1] - pd.Timedelta(days=365)].iloc[-1])],
                SPX=[float(spx.iloc[-1]), float(spx.loc[:spx.index[-1] - pd.Timedelta(days=365)].iloc[-1])])

EV = {t: json.load(open(f'events_{t}.json')) for t in START}
out = {}
for t in START:
    e = E['res'][t]
    moves = M[t]
    # attach event numbers for chart markers: top events
    tops = EV[t]['top']
    out[t] = dict(ticker=t, eda=e, moves=dict(threshold=moves['threshold'], counts=moves['counts'], resid_var_share=moves['resid_var_share'],
                                              events=[{k: v for k, v in ev.items() if k != 'filings'} | {'nf': len(ev['filings']), 'fil': [f['form'] + ' ' + f['filed'] + ' (' + (f['items'] or '') + ')' for f in ev['filings']][:2]} for ev in moves['events']]),
                  events=EV[t], verify=V[t], fund=FUND[t], val=VAL[t], stats=stats(t), snap=snap())
json.dump(dict(data=out, labels=E['labels']), open(D + 'page_data.json', 'w'), ensure_ascii=False, default=float)
for t in out: print(t, out[t]['stats'])
