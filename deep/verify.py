import json,pandas as pd,numpy as np
V='../valuation/'
# prior extraction (first pass, table-based) mapped to blind ids, USD millions
P={'CRGY':{'F4':1115.979,'F5':264.882,'F9':5166.022,'F10':330403696,'O1':335,'O2':140,'O3':96.61,'O4':6.8,'O5':797.94,'O6':417.678,'O7':4901,'R1':975.518,'R2':776.346,'R3':7756,'R4':8633,'R5':65.34},
 'KOS':{'F1':607.253,'F2':184.775,'F3':-40.799,'F4':281.566,'F5':102.137,'F10':595487651,'O1':71400,'O3':108.57,'O8':3250000,'R1':249,'R2':138,'O4':25.61,'O5':311.656,'O6':88.891,'O7':2563.445,'R3':1890},
 'REI':{'F1':104.681489,'F2':64.79331,'F4':66.683994,'F5':1.13741,'F8':753.423762,'F9':360.0,'F10':260539607,'O1':1819076/91,'O2':1154147/91,'O3':95.45,'O4':10.12,'O5':54.48,'O6':4.375,'R1':153.277821,'R2':103.798946,'R5':61.82,'R3':1123.493,'R4':1318.208},
 'SM':{'F2':1071,'F3':736,'F4':1743,'F5':620,'F6':18858,'F8':7813,'F10':237854068,'O1':439.7,'O2':229.8,'O3':96.85,'O4':6.71,'O5':1406,'O6':467,'O7':6253,'R1':673.0,'R2':412.3,'R3':5956,'R4':6847,'R5':65.34}}
LAB={'F1':'2분기 매출','F2':'2분기 순이익','F3':'상반기 순이익','F4':'상반기 영업현금흐름','F5':'현금(6/30)','F6':'총자산','F7':'총부채','F8':'자본총계','F9':'장기부채 장부가','F10':'발행주식 수(표지)','O1':'2분기 생산량','O2':'2분기 원유 생산','O3':'원유 실현가(헤지 전)','O4':'LOE/Boe','O5':'조정 EBITDA(X)','O6':'회사 제시 FCF','O7':'순부채(회사 제시)','O8':'하반기 원유 헤지','R1':'증명매장량','R2':'증명개발','R3':'Std. Measure','R4':'PV-10','R5':'SEC 가격'}
def cf(t):
    return json.load(open(V+f'xbrl_{t}.json'))['facts']
def fact(F,tag,end,start=None,form=None):
    ns,name=tag.split(':') if ':' in tag else ('us-gaap',tag)
    ns={'us-gaap':'us-gaap','dei':'dei','srt':'srt'}.get(ns,ns)
    if ns not in F or name not in F[ns]: return None
    out=[]
    for u,arr in F[ns][name]['units'].items():
        for x in arr:
            if x['end']==end and (x.get('start')==start):
                out.append((x['filed'],x['val'],u,x.get('form'),x.get('fp')))
    if not out: return None
    out.sort(); return out[-1]
Q2=('2026-06-30','2026-04-01'); H1=('2026-06-30','2026-01-01'); Q1=('2026-03-31','2026-01-01'); BS=('2026-06-30',None)
PER={'F1':Q2,'F2':Q2,'F3':H1,'F4':H1,'F5':BS,'F6':BS,'F7':BS,'F8':BS,'F9':BS}
def num(v):
    if isinstance(v,dict):
        for k in ('pd_mmboe','oil_usd_per_bbl','total_equity_incl_nci','total_equity_incl_NCI','total_equity','total_oil_hedged_bbl','total_oil_hedge_bbl'):
            if isinstance(v.get(k),(int,float)): return v[k]
        for k in v:
            if isinstance(v[k],(int,float)): return v[k]
        return None
    return v
res={}; ALL=[]
for t in ['CRGY','KOS','REI','SM']:
    F=cf(t); B={i['id']:i for i in json.load(open(f'blind_{t}.json'))['items']}
    rows=[]
    for id_,it in B.items():
        bv=num(it.get('value')); pv=P[t].get(id_); xv=None; tag=''
        src=it.get('source',{}) or {}
        ixn=(src.get('ix_name') or '').split(' ')[0].split('/')[0].strip()
        ixall=[x.strip() for x in (src.get('ix_name') or '').replace(';','+').split('+')][:2]
        if id_ in PER and ixn:
            fs=[fact(F,x.split(' ')[0],*PER[id_]) for x in ixall]
            if all(fs): xv=sum(f[1] for f in fs)/1e6; tag=' + '.join(ixall)
        if id_=='F10':
            d=F['dei'].get('EntityCommonStockSharesOutstanding',{}).get('units',{}).get('shares',[])
            d=[x for x in d if x.get('form')=='10-Q' and x['filed']>='2026-07-01']
            if d: xv=d[-1]['val']; tag='dei:EntityCommonStockSharesOutstanding'
        vals=[v for v in [bv,pv,xv] if v is not None]
        def close(a,b):
            return abs(a-b)<=max(0.005*abs(b),0.02) 
        if it['status']=='ambiguous':
            st='⚠ 모호(재추출)' + (' · 1차 값 있음' if pv is not None else '')
        elif bv is None:
            st='자료 없음'
        else:
            checks=[]
            if xv is not None: checks.append(close(bv,xv))
            if pv is not None: checks.append(close(bv,pv))
            if not checks: st='단일 출처'
            elif all(checks): st='✔ '+('XBRL·' if xv is not None else '')+('재추출·1차' if pv is not None else '재추출')+' 일치'
            else: st='⚠ 불일치'
        rows.append(dict(id=id_,label=LAB[id_],blind=bv,prior=pv,xbrl=xv,tag=tag,status=st,unit=it.get('unit'),file=src.get('file'),note=(it.get('note') or '')[:200]))
    # footing & quarter checks from companyfacts
    chk=[]
    A=fact(F,'Assets',*BS); LSE=fact(F,'LiabilitiesAndStockholdersEquity',*BS); L=fact(F,'Liabilities',*BS)
    EQ=fact(F,'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',*BS) or fact(F,'StockholdersEquity',*BS)
    if A and LSE: chk.append(('총자산 = 부채와자본 합계', A[1]/1e6, LSE[1]/1e6, abs(A[1]-LSE[1])<1e3))
    if A and L and EQ:
        # mezzanine/temporary equity may exist
        TE=fact(F,'TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests',*BS)
        s=L[1]+EQ[1]+(TE[1] if TE else 0); chk.append(('부채 + 자본 = 총자산', s/1e6, A[1]/1e6, abs(s-A[1])<1e6))
    o=fact(F,'NetCashProvidedByUsedInOperatingActivities',*H1); i=fact(F,'NetCashProvidedByUsedInInvestingActivities',*H1); f_=fact(F,'NetCashProvidedByUsedInFinancingActivities',*H1)
    d=fact(F,'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',*H1) or fact(F,'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect',*H1)
    if o and i and f_ and d:
        s=o[1]+i[1]+f_[1]; chk.append(('영업+투자+재무 현금흐름 = 현금 증감(상반기)', s/1e6, d[1]/1e6, abs(s-d[1])<1.5e6))
    for tag,lab in [('Revenues','매출'),('RevenueFromContractWithCustomerExcludingAssessedTax','고객계약 매출'),('NetIncomeLoss','순이익')]:
        a=fact(F,tag,*Q1); b=fact(F,tag,*Q2); c=fact(F,tag,*H1)
        if a and b and c:
            chk.append((f'{lab}: 1분기 + 2분기 = 상반기', (a[1]+b[1])/1e6, c[1]/1e6, abs(a[1]+b[1]-c[1])<1.5e6))
    res[t]={'rows':rows,'checks':[dict(name=n,lhs=round(x,3),rhs=round(y,3),ok=bool(ok)) for n,x,y,ok in chk]}
# sanity checks
fr=pd.read_pickle('data/fred.pkl')
wti=fr.DCOILWTICO['2026-04-01':'2026-06-30'].mean(); brent=fr.DCOILBRENTEU['2026-04-01':'2026-06-30'].mean()
SAN={}
for t in res:
    R={r['id']:r for r in res[t]['rows']}
    s=[]
    o3=R['O3']['blind']; bench=brent if t=='KOS' else wti
    if o3: s.append((f"원유 실현가 − {'Brent' if t=='KOS' else 'WTI'} 2분기 평균(${bench:.2f})", round(o3-bench,2), -12<=o3-bench<=8))
    o4=R['O4']['blind'] or R['O4']['prior']
    if o4: s.append(('LOE/Boe 범위(3~30달러)',o4,3<=o4<=30))
    o1=R['O1']['blind']; o2=R['O2']['blind']
    if o1 and o2: s.append(('원유 비중(원유/총생산)',round(o2/o1,3),0.2<=o2/o1<=0.9))
    f1=R['F1']['blind']; 
    if f1 and o1:
        boe=o1*(1000 if R['O1']['unit'].startswith('MBoe') else 1)*91
        s.append(('매출/판매량($/Boe)',round(f1*1e6/boe,2),20<=f1*1e6/boe<=110))
    o5=R['O5']['blind']
    if o5 and f1: s.append(('조정 EBITDA(X)/매출',round(o5/f1,3),0.3<=o5/f1<=0.9))
    res[t]['sanity']=[dict(name=n,val=v,ok=bool(ok)) for n,v,ok in s]
res['CRGY']['rows']=[dict(r,status='✔ 원문 문장 확인',note='10-Q MD&A 한 문단에 "…decreased $0.75 per Boe, or 10%, to $6.80 per Boe"로 명시. 재추출은 표에서만 찾아 모호로 분류했고 원문 문단을 다시 확인해 확정') if r['id']=='O4' else r for r in res['CRGY']['rows']]
json.dump(res,open('data/verification.json','w'),ensure_ascii=False,indent=1,default=float)
for t in res:
    print('=====',t)
    for r in res[t]['rows']: print(f"  {r['id']:4}{r['label'][:14]:16}{str(r['blind'])[:12]:>13}{str(r['prior'])[:12]:>13}{str(r['xbrl'])[:12]:>13}  {r['status']}")
    for c in res[t]['checks']: print('  CHK',c)
    for c in res[t]['sanity']: print('  SAN',c)
print('WTI Q2',wti,'Brent Q2',brent)
