import re, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
D = 'data/'
y = pd.read_pickle(D + 'prices.pkl'); fr = pd.read_pickle('../deep/data/fred.pkl')
y = y[y.index.dayofweek < 5]
for c in ['DCOILWTICO', 'DCOILBRENTEU', 'DHHNGSP']: fr.loc[fr[c] <= 0, c] = np.nan
START = {'BABA': '2014-09-19', 'BIDU': '2005-08-05', 'JD': '2014-05-22'}
hist = json.load(open(D + 'sec_hist.json'))
out = {}
for t in START:
    oil = 'DCOILWTICO'
    px = y[t].dropna(); px = px[px.index >= START[t]]
    idx = px.index
    F = pd.DataFrame({'SPX': np.log(y['^GSPC']).diff(), 'USD': np.log(y['DX-Y.NYB']).diff(), 'VIX': np.log(y['^VIX']).diff(), 'CNY': np.log(y['CNY=X'].ffill(limit=3)).diff(), 'COPPER': np.log(y['HG=F'].ffill(limit=3)).diff()})
    G = pd.DataFrame({'OIL': np.log(fr[oil].ffill(limit=3)).diff(), 'UST10': fr.DGS10.ffill(limit=3).diff()})
    X = pd.concat([F, G], axis=1).reindex(idx)
    r = np.log(px).diff()
    d = pd.concat([r.rename('R'), X], axis=1).dropna()
    cols = ['SPX', 'CNY', 'COPPER', 'UST10', 'USD', 'VIX']
    fit = pd.Series(np.nan, index=d.index)
    V = d.values; W = 252
    for i in range(W, len(d)):
        A = d.iloc[i - W:i]; Xa = np.column_stack([np.ones(W), A[cols].values])
        b, *_ = np.linalg.lstsq(Xa, A.R.values, rcond=None)
        fit.iloc[i] = b[1:] @ d.iloc[i][cols].values          # exclude alpha
    d['FIT'] = fit; d['RES'] = d.R - d.FIT
    d = d.dropna()
    thr = max(0.08, d.R.abs().quantile(0.99))
    big = d[d.R.abs() >= thr].copy()
    big['share'] = (big.FIT / big.R).clip(-1, 2)
    big['type'] = np.where(big.share >= 0.5, '매크로', np.where(big.share >= 1/3, '혼합', '비매크로'))
    shock = ((big.SPX.abs() >= 0.05) & (np.sign(big.SPX) == np.sign(big.R)))
    big['_nf'] = [sum(1 for f in hist[t]['rows'] if f['form'] in ('6-K','6-K/A','F-1','424B4','SC 13D') and dt - pd.Timedelta(days=3) <= pd.Timestamp(f['filed']) <= dt + pd.Timedelta(days=1)) for dt in big.index]
    big.loc[shock & (big.type != '매크로') & (big._nf == 0), 'type'] = '매크로 충격'
    cn = np.log(y['KWEB'].where(y.index >= '2013-08-01').combine_first(y['FXI'])).diff().reindex(big.index)
    big['CN'] = cn
    common = (cn.abs() >= 0.05) & (np.sign(cn) == np.sign(big.R)) & (cn.abs() >= 0.5 * big.R.abs()) & (big.type != '매크로')
    big.loc[common, 'type'] = '중국 공통 충격'
    # merge episodes within 5 trading days: keep largest |R|
    big = big.sort_index(); keep = []; last = None
    pos = {k: i for i, k in enumerate(d.index)}
    for dt, row in big.iterrows():
        if last is not None and pos[dt] - pos[last] <= 5:
            if abs(row.R) > abs(big.loc[last].R): keep[-1] = dt; last = dt
            continue
        keep.append(dt); last = dt
    big = big.loc[keep]
    rows = hist[t]['rows']
    evs = []
    for dt, row in big.iterrows():
        near = [f for f in rows if f['form'] in ('6-K', '6-K/A', 'F-1', '424B4')
                and pd.Timestamp(dt) - pd.Timedelta(days=3) <= pd.Timestamp(f['filed']) <= pd.Timestamp(dt) + pd.Timedelta(days=1)]
        evs.append(dict(date=str(dt.date()), R=round(float(np.expm1(row.R)), 4), fit=round(float(row.FIT), 4), res=round(float(row.RES), 4),
                        share=round(float(row.share), 2), type=row.type,
                        oil=round(float(row.CNY), 4), spx=round(float(row.SPX), 4), cn=(None if pd.isna(row.CN) else round(float(row.CN), 4)),
                        filings=[dict(form=f['form'], filed=f['filed'], items=f.get('items',''), acc=f['acc'], doc=f['doc'], desc=f['desc']) for f in near]))
    corp = []
    for f in rows:
        if True: continue
        fd = pd.Timestamp(f['filed'])
        w = d[(d.index >= fd - pd.Timedelta(days=1)) & (d.index <= fd + pd.Timedelta(days=3))]
        if len(w)==0: continue
        k = w.R.abs().idxmax(); row = w.loc[k]
        corp.append(dict(filed=f['filed'], form=f['form'], items=f.get('items',''), doc=f['doc'], acc=f['acc'], day=str(k.date()), R=round(float(np.expm1(row.R)),4), fit=round(float(row.FIT),4), res=round(float(row.RES),4)))
    # also cumulative residual (macro-unexplained) drift — 1y rolling
    out[t] = dict(threshold=thr, n_days=len(d), events=evs,
                  counts={k: int((big.type == k).sum()) for k in ['매크로', '매크로 충격', '중국 공통 충격', '혼합', '비매크로']},
                  resid_var_share=float(d.RES.var() / d.R.var()), corp=corp)
    print('==', t, 'thr %.3f' % thr, out[t]['counts'], 'unexplained var share %.2f' % out[t]['resid_var_share'])
    for e in sorted([e for e in evs if e['type'] in ('혼합','비매크로')], key=lambda e: -abs(e['res']))[:10]:
        print('  ', e['date'], '%+.1f%%' % (e['R'] * 100), 'fit %+.1f%%' % (e['fit'] * 100), e['type'], [(f['form'], f['filed'], f['items'], f['doc']) for f in e['filings']][:3])
    for e in sorted([e for e in evs if e['type'] == '매크로'], key=lambda e: -abs(e['R']))[:4]:
        print('   M', e['date'], '%+.1f%%' % (e['R'] * 100), 'fit %+.1f%%' % (e['fit'] * 100))
json.dump(out, open(D + 'moves.json', 'w'), ensure_ascii=False)

for t in out:
    c=sorted({(x['day']):x for x in out[t]['corp'] if x['form']=='8-K'}.values(), key=lambda x:-abs(x['res']))[:8]
    print('== corp',t)
    for x in c: print('  ',x['day'],x['filed'],x['items'],'%+.1f%% res %+.1f%%'%(x['R']*100,x['res']*100),x['doc'])
