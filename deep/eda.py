import json, itertools, numpy as np, pandas as pd
D = 'data/'
y = pd.read_pickle(D + 'yahoo.pkl'); fr = pd.read_pickle(D + 'fred.pkl'); eia = pd.read_pickle(D + 'eia.pkl')
y = y[y.index.dayofweek < 5]
fr = fr.copy()
for c in ['DCOILWTICO', 'DCOILBRENTEU', 'DHHNGSP']:
    fr.loc[fr[c] <= 0, c] = np.nan
START = {'CRGY': '2021-12-08', 'KOS': '2011-05-11', 'REI': '2012-07-02', 'SM': '1993-01-04'}
NAME = {'CRGY': 'Crescent Energy', 'KOS': 'Kosmos Energy', 'REI': 'Ring Energy', 'SM': 'SM Energy'}
FL = {'SPX': 'S&P 500', 'OIL': '원유(WTI)', 'HH': '천연가스(Henry Hub)', 'UST10': '미 10년 금리', 'CREDIT': '신용스프레드(Baa−10년)',
      'USD': '달러지수', 'BEI': '기대인플레(10년 BEI)', 'VIX': 'VIX', 'INV': '미 원유재고(EIA)'}

def weekly_levels():
    L = pd.DataFrame({
        'SPX': y['^GSPC'], 'USD': y['DX-Y.NYB'], 'VIX': y['^VIX'],
        'WTI': fr.DCOILWTICO, 'BRENT': fr.DCOILBRENTEU, 'HH': fr.DHHNGSP,
        'UST10': fr.DGS10, 'CREDIT': fr.BAA10Y, 'BEI': fr.T10YIE})
    W = L.resample('W-FRI').last()
    W['INV'] = eia.WCESTUS1.resample('W-FRI').last()
    return W

WL = weekly_levels()
def factor_changes(W, oil):
    X = pd.DataFrame(index=W.index)
    for c in ['SPX', 'USD', 'HH', 'VIX']: X[c] = np.log(W[c]).diff()
    X['OIL'] = np.log(W[oil]).diff()
    for c in ['UST10', 'CREDIT', 'BEI']: X[c] = W[c].diff()
    X['INV'] = np.log(W['INV']).diff()
    return X[['SPX', 'OIL', 'HH', 'UST10', 'CREDIT', 'USD', 'BEI', 'VIX', 'INV']]

def r2(Xa, yv):
    Xa = np.column_stack([np.ones(len(yv)), Xa]); b, *_ = np.linalg.lstsq(Xa, yv, rcond=None)
    e = yv - Xa @ b; return 1 - e.var() / yv.var(), b

def shapley(X, yv):
    cols = list(X.columns); k = len(cols); cache = {}
    def R(S):
        if not S: return 0.0
        if S not in cache: cache[S] = r2(X[list(S)].values, yv)[0]
        return cache[S]
    from math import factorial
    out = {}
    for c in cols:
        others = [o for o in cols if o != c]; s = 0
        for m in range(k):
            for S in itertools.combinations(others, m):
                w = factorial(m) * factorial(k - m - 1) / factorial(k)
                s += w * (R(tuple(sorted(S + (c,)))) - R(tuple(sorted(S))))
        out[c] = s
    return out

def std_betas(X, yv):
    Z = (X - X.mean()) / X.std(); _, b = r2(Z.values, (yv - yv.mean()) / yv.std()); return dict(zip(X.columns, b[1:]))

def periods(t, idx0):
    P = [('1993-01-01', '2002-12-31', '1993–2002'), ('2003-01-01', '2008-12-31', '2003–2008 슈퍼사이클·금융위기'),
         ('2009-01-01', '2014-06-30', '2009–2014 셰일 붐'), ('2014-07-01', '2019-12-31', '2014–2019 유가 붕괴·저유가'),
         ('2020-01-01', '2021-12-31', '2020–2021 코로나·회복'), ('2022-01-01', '2026-12-31', '2022–2026 긴축·지정학')]
    return [(a, b, l) for a, b, l in P if pd.Timestamp(b) > pd.Timestamp(idx0) + pd.Timedelta(days=200)]

res = {}
for t in ['CRGY', 'KOS', 'REI', 'SM']:
    oil = 'BRENT' if t == 'KOS' else 'WTI'
    px = y[t].dropna(); px = px[px.index >= START[t]]
    pw = px.resample('W-FRI').last().dropna()
    X = factor_changes(WL, oil)
    ry = np.log(pw).diff().rename('R')
    df = pd.concat([ry, X], axis=1).loc[pw.index].dropna(subset=['R'])
    # univariate correlations (weekly), full period, each factor its own availability
    corr = {c: dict(r=float(df[['R', c]].dropna().corr().iloc[0, 1]), n=int(df[['R', c]].dropna().shape[0])) for c in X.columns}
    # 13-week (quarterly) returns correlation with oil & spx
    q = pd.concat([np.log(pw), np.log(WL[oil]), np.log(WL['SPX'])], axis=1).loc[pw.index].diff(13).iloc[::13].dropna()
    q.columns = ['R', 'OIL', 'SPX']
    corr_q = {'OIL': float(q.corr().iloc[0, 1]), 'SPX': float(q.corr().iloc[0, 2]), 'n': len(q)}
    # multivariate + shapley (common sample)
    dm = df.dropna()
    R2, b = r2(dm[X.columns].values, dm.R.values)
    sh = shapley(dm[X.columns], dm.R.values)
    sb = std_betas(dm[X.columns], dm.R.values)
    # raw oil beta controlling SPX
    _, bb = r2(dm[['SPX', 'OIL']].values, dm.R.values)
    full = dict(start=str(dm.index[0].date()), end=str(dm.index[-1].date()), n=len(dm), r2=float(R2),
                shapley={k: float(v) for k, v in sh.items()}, std_beta={k: float(v) for k, v in sb.items()},
                beta_spx=float(bb[1]), beta_oil=float(bb[2]))
    # by period (shapley)
    per = []
    for a, bnd, lab in periods(t, px.index[0]):
        d = dm[(dm.index >= a) & (dm.index <= bnd)]
        if len(d) < 60: continue
        s = shapley(d[X.columns], d.R.values); rr = r2(d[X.columns].values, d.R.values)[0]
        _, b2 = r2(d[['SPX', 'OIL']].values, d.R.values)
        per.append(dict(label=lab, start=str(d.index[0].date()), end=str(d.index[-1].date()), n=len(d), r2=float(rr),
                        shapley={k: float(v) for k, v in s.items()}, beta_oil=float(b2[2]), beta_spx=float(b2[1]),
                        corr_oil=float(d[['R', 'OIL']].corr().iloc[0, 1])))
    # rolling 52w correlations and 104w oil beta
    roll = pd.DataFrame({'c_oil': df.R.rolling(52).corr(df.OIL), 'c_spx': df.R.rolling(52).corr(df.SPX),
                         'c_ust10': df.R.rolling(52).corr(df.UST10), 'c_credit': df.R.rolling(52).corr(df.CREDIT)})
    # yearly returns
    yr = pd.DataFrame({'R': pw.resample('YE').last(), 'OIL': WL[oil].resample('YE').last(), 'SPX': WL['SPX'].resample('YE').last()})
    first = pd.Series({'R': pw.iloc[0], 'OIL': WL[oil].loc[:pw.index[0]].dropna().iloc[-1], 'SPX': WL['SPX'].loc[:pw.index[0]].dropna().iloc[-1]})
    yr = pd.concat([first.to_frame(pw.index[0]).T, yr]).pct_change().dropna()
    yr.index = [str(i.year) for i in yr.index]
    # series for charts (weekly)
    ser = pd.DataFrame({'p': pw, 'oil': WL[oil].reindex(pw.index).ffill(), 'spx': WL['SPX'].reindex(pw.index).ffill()})
    res[t] = dict(name=NAME[t], oil=oil, start=str(px.index[0].date()), corr=corr, corr_q=corr_q, full=full, periods=per,
                  roll=dict(d=[str(i.date()) for i in roll.index], **{k: [None if np.isnan(v) else round(float(v), 3) for v in roll[k]] for k in roll}),
                  yearly=dict(y=list(yr.index), R=[round(float(v), 4) for v in yr.R], OIL=[round(float(v), 4) for v in yr.OIL], SPX=[round(float(v), 4) for v in yr.SPX]),
                  series=dict(d=[str(i.date()) for i in ser.index], p=[round(float(v), 4) for v in ser.p], oil=[None if np.isnan(v) else round(float(v), 2) for v in ser.oil], spx=[round(float(v), 2) for v in ser.spx]))
    top = sorted(full['shapley'].items(), key=lambda kv: -kv[1])[:3]
    print(t, 'n', full['n'], 'R2 %.3f' % full['r2'], [(FL[k], round(v / full['r2'] * 100)) for k, v in top], 'beta_oil %.2f beta_spx %.2f' % (full['beta_oil'], full['beta_spx']))
    for p in per: print('   ', p['label'], p['n'], 'R2 %.2f' % p['r2'], 'oil β %.2f corr %.2f' % (p['beta_oil'], p['corr_oil']), max(p['shapley'], key=p['shapley'].get))
    print('   corr', {k: round(v['r'], 2) for k, v in corr.items()}, 'q', {k: round(v, 2) if isinstance(v, float) else v for k, v in corr_q.items()})
json.dump(dict(res=res, labels=FL), open(D + 'eda_weekly.json', 'w'), ensure_ascii=False)
