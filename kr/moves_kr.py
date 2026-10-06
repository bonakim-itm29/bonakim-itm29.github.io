import json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
D = 'data/'
y = pd.read_pickle(D + 'prices.pkl'); fr = pd.read_pickle('../deep/data/fred.pkl')
y = y[y.index.dayofweek < 5]
for c in ['DCOILWTICO', 'DCOILBRENTEU', 'DHHNGSP']: fr.loc[fr[c] <= 0, c] = np.nan
START = {'005930.KS': '2004-01-02', '000660.KS': '2004-01-02'}
hist = json.load(open(D + 'kr_hist.json'))
out = {}
for t in START:
    px = y[t].dropna(); px = px[px.index >= START[t]]
    idx = px.index
    # US-session factors: the US close on day t-1 precedes the HK session on day t -> shift by one US trading day
    F = pd.DataFrame({'SPX': np.log(y['^GSPC'].dropna()).diff(), 'USD': np.log(y['DX-Y.NYB'].dropna()).diff(), 'VIX': np.log(y['^VIX'].dropna()).diff(),
                      'COPPER': np.log(y['HG=F'].dropna()).diff()})
    G = pd.DataFrame({'OIL': np.log(fr.DCOILWTICO.dropna()).diff(), 'UST10': fr.DGS10.dropna().diff()})
    US = pd.concat([F, G], axis=1).shift(1)
    US = US.reindex(US.index.union(idx)).ffill(limit=3).reindex(idx)
    CNY = np.log(y['KRW=X'].ffill(limit=3)).diff().reindex(idx)
    X = US.copy(); X['CNY'] = CNY
    r = np.log(px).diff()
    d = pd.concat([r.rename('R'), X], axis=1).dropna()
    cols = ['SPX', 'CNY', 'COPPER', 'UST10', 'USD', 'VIX']
    fit = pd.Series(np.nan, index=d.index); W = 252
    for i in range(W, len(d)):
        A = d.iloc[i - W:i]; Xa = np.column_stack([np.ones(W), A[cols].values])
        b, *_ = np.linalg.lstsq(Xa, A.R.values, rcond=None)
        fit.iloc[i] = b[1:] @ d.iloc[i][cols].values
    d['FIT'] = fit; d['RES'] = d.R - d.FIT
    d = d.dropna()
    thr = max(0.08, d.R.abs().quantile(0.99))
    big = d[d.R.abs() >= thr].copy()
    big['share'] = (big.FIT / big.R).clip(-1, 2)
    big['type'] = np.where(big.share >= 0.5, '매크로', np.where(big.share >= 1/3, '혼합', '비매크로'))
    rows = [f for f in hist[t]['rows'] if f['key']]
    def near(dt): return [f for f in rows if dt - pd.Timedelta(days=3) <= pd.Timestamp(f['filed']) <= dt + pd.Timedelta(days=0)]
    big['_nf'] = [len(near(dt)) for dt in big.index]
    shock = ((big.SPX.abs() >= 0.05) & (np.sign(big.SPX) == np.sign(big.R)))
    big.loc[shock & (big.type != '매크로') & (big._nf == 0), 'type'] = '매크로 충격'
    # Korea market / semiconductor common shock: same-day KOSPI (>=3%) or previous US session SOX (>=5%)
    ks = np.log(y['^KS11']).diff().reindex(big.index)
    sox = np.log(y['^SOX'].dropna()).diff().shift(1)
    sox = sox.reindex(sox.index.union(big.index)).ffill(limit=3).reindex(big.index)
    c1 = (ks.abs() >= 0.03) & (np.sign(ks) == np.sign(big.R)) & (ks.abs() >= 0.5 * big.R.abs())
    c2 = (sox.abs() >= 0.05) & (np.sign(sox) == np.sign(big.R)) & (sox.abs() >= 0.5 * big.R.abs())
    big['CN'] = np.where(sox.abs() > ks.abs(), sox, ks)
    common = (c1.fillna(False) | c2.fillna(False)) & (big.type != '매크로')
    big.loc[common, 'type'] = '시장·업종 공통 충격'
    big = big.sort_index(); keep = []; last = None
    pos = {k: i for i, k in enumerate(d.index)}
    for dt, row in big.iterrows():
        if last is not None and pos[dt] - pos[last] <= 5:
            if abs(row.R) > abs(big.loc[last].R): keep[-1] = dt; last = dt
            continue
        keep.append(dt); last = dt
    big = big.loc[keep]
    evs = []
    for dt, row in big.iterrows():
        evs.append(dict(date=str(dt.date()), R=round(float(np.expm1(row.R)), 4), fit=round(float(row.FIT), 4), res=round(float(row.RES), 4),
                        share=round(float(row.share), 2), type=row.type, oil=round(float(row.CNY), 4), spx=round(float(row.SPX), 4),
                        cn=(None if pd.isna(row.CN) else round(float(row.CN), 4)),
                        filings=[dict(form='KIND', filed=f['filed'], items=f['time'], acc=f['acpt'], doc='', desc=f['title'][:120]) for f in near(dt)]))
    out[t] = dict(threshold=thr, n_days=len(d), events=evs,
                  counts={k: int((big.type == k).sum()) for k in ['매크로', '매크로 충격', '시장·업종 공통 충격', '혼합', '비매크로']},
                  resid_var_share=float(d.RES.var() / d.R.var()), corp=[])
    print('==', t, 'thr %.3f' % thr, out[t]['counts'], 'unexplained var share %.2f' % out[t]['resid_var_share'])
    for e in sorted([e for e in evs if e['type'] in ('혼합', '비매크로')], key=lambda e: -abs(e['res']))[:12]:
        print('  ', e['date'], '%+.1f%%' % (e['R'] * 100), 'fit %+.1f%%' % (e['fit'] * 100), 'hk %s' % e['cn'], e['type'], [(f['filed'], f['desc'][:60]) for f in e['filings']][:3])
    for e in sorted([e for e in evs if e['type'] == '시장·업종 공통 충격'], key=lambda e: -abs(e['R']))[:5]:
        print('   C', e['date'], '%+.1f%%' % (e['R'] * 100), 'hk %+.1f%%' % (e['cn'] * 100))
json.dump(out, open(D + 'moves.json', 'w'), ensure_ascii=False)
