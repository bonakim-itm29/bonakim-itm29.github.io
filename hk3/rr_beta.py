import pandas as pd, numpy as np, json
def rd(f,col):
    d=pd.read_csv(f); d['date']=pd.to_datetime(d['date']); return pd.to_numeric(d.set_index('date')[col],errors='coerce')
y=pd.read_pickle('data/prices.pkl')
P={s:rd(f'src/realrate/yahoo/{s}.csv','adjclose') for s in ['PDD','NTES','TCOM','BABA','BIDU','JD','KWEB']}
for s in ['0700.HK','3690.HK','0992.HK','1810.HK','1211.HK','^GSPC']: P[s]=y[s]
f=pd.read_csv('src/realrate/fred/DFII10.csv'); f.columns=['date','v']; f['date']=pd.to_datetime(f['date'])
D=pd.DataFrame(P); D['RR']=pd.to_numeric(f.set_index('date')['v'],errors='coerce')
W=D.ffill(limit=3).resample('W-FRI').last(); W=W[W.index<='2026-10-02']
NAMES={'BABA':'alibaba','BIDU':'baidu','JD':'jd','PDD':'pdd','NTES':'netease','TCOM':'trip-com','0700.HK':'tencent','3690.HK':'meituan','0992.HK':'lenovo','1810.HK':'xiaomi','1211.HK':'byd','KWEB':'KWEB'}
def run(start, h):
    out={}
    for s,n in NAMES.items():
        w=W[W.index>=start]
        r=np.log(w[s]).diff(h); x=w.RR.diff(h); m=np.log(w['^GSPC']).diff(h)
        d=pd.concat([r.rename('R'),x.rename('RR'),m.rename('SPX')],axis=1).iloc[::h].dropna()
        b=np.linalg.lstsq(np.column_stack([np.ones(len(d)),d.RR,d.SPX]),d.R,rcond=None)[0]
        out[n]=dict(beta=float(b[1]),beta_simple=float(np.polyfit(d.RR,d.R,1)[0]),corr=float(d.R.corr(d.RR)),n=len(d),start=str(d.index[0].date()))
    return out
if __name__=='__main__':
    for st in ['2015-01-01','2021-01-01']:
        for h in [4,13]:
            o=run(st,h); print('==',st,h)
            for n,v in o.items(): print(f"  {n:9s} b|spx {v['beta']:+.3f} simple {v['beta_simple']:+.3f} corr {v['corr']:+.2f} n {v['n']}")
