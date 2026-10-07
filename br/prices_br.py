import pandas as pd, glob, os
def rd(f, col):
    d = pd.read_csv(f); d['date'] = pd.to_datetime(d['date']); s = pd.to_numeric(d.set_index('date')[col], errors='coerce'); return s[~s.index.duplicated(keep='last')]
Y = {}
EQ = {'VALE', 'PBR', 'ITUB', 'NU', 'BBD', 'ABEV', 'SBS', 'EWZ', 'EEM', 'EMBJ', 'AXIA3.SA', 'EMBJ3.SA', 'ITUB4.SA', 'PBR-A'}
for f in glob.glob('br9_prices/yahoo/*.csv') + glob.glob('br9_extra/yahoo/*.csv'):
    s = os.path.basename(f)[:-4].replace('_GSPC', '^GSPC').replace('_VIX', '^VIX').replace('_BVSP', '^BVSP').replace('BRL_X', 'BRL=X').replace('HG_F', 'HG=F').replace('CL_F', 'CL=F').replace('BZ_F', 'BZ=F')
    if s == 'AXIA': continue
    Y[s] = rd(f, 'adjclose' if s in EQ else 'close')
y = pd.DataFrame(Y).sort_index()
# 미국 상장 시세는 10/6 장중 값 제외
for c in y.columns:
    if not c.endswith('.SA') and c not in ('BRL=X',): y.loc[y.index >= '2026-10-06', c] = float('nan')
y.to_pickle('data/prices.pkl')
F = {}
for f in glob.glob('br9_prices/fred/*.csv'):
    d = pd.read_csv(f); d.columns = ['date', 'v']; d['date'] = pd.to_datetime(d['date']); F[os.path.basename(f)[:-4]] = pd.to_numeric(d.set_index('date')['v'], errors='coerce')
fr = pd.DataFrame(F); fr.to_pickle('data/fred.pkl')
print(y.shape, list(y.columns)); print(y[['VALE', 'EMBJ', 'AXIA3.SA', 'BRL=X', 'EWZ']].dropna(how='all').tail(3)); print(fr.tail(2))
