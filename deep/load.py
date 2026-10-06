import json,pandas as pd,numpy as np,io
U='/mnt/user-data/uploads/Downloads/'
def yload(fn):
    d=json.load(open(U+fn)); S={}
    for s,v in d.items():
        idx=pd.to_datetime(pd.Series(v['t']),unit='s').dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.normalize().dt.tz_localize(None)
        col=v['adj'] if v.get('adj') else v['close']
        ser=pd.Series(col,index=idx.values,dtype=float); ser=ser[~ser.index.duplicated(keep='last')]
        S[s]=ser
    return S
Y=yload('yahoo_all_0928.json')
yp=pd.DataFrame(Y).sort_index()
f=json.load(open(U+'fred_long.json')); F={}
for k,t in f.items():
    df=pd.read_csv(io.StringIO(t)); df.columns=['date','v']; df['v']=pd.to_numeric(df.v,errors='coerce')
    F[k]=df.set_index(pd.to_datetime(df.date)).v
fr=pd.DataFrame(F).sort_index()
yp.to_pickle('data/yahoo.pkl'); fr.to_pickle('data/fred.pkl')
print(yp.shape, fr.shape); print(yp[['CRGY','KOS','REI','SM']].describe().T[['count','min','max']])
print(yp[['CRGY','KOS','REI','SM']].tail(3))
import base64
e=json.load(open(U+'eia_weekly.json')); E={}
for k,b in e.items():
    raw=base64.b64decode(b)
    x=pd.read_excel(io.BytesIO(raw),sheet_name='Data 1',skiprows=2)
    x.columns=['date','v']; E[k]=x.set_index(pd.to_datetime(x.date)).v.astype(float)
ew=pd.DataFrame(E).sort_index(); ew.to_pickle('data/eia.pkl'); print(ew.tail(2)); print(ew.index.min())
ev={s:json.load(open(U+'yahoo_all_0928.json'))[s]['events'] for s in ['CRGY','KOS','REI','SM']}
json.dump(ev,open('data/yahoo_events.json','w'))
for s,v in ev.items(): print(s, {k:len(x) for k,x in (v or {}).items()}, (v or {}).get('splits'))
