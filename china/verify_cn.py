import json,re
LAB={'Q1':'분기 매출','Q3':'영업이익','Q4':'조정 영업이익(회사 정의)','Q5':'귀속 순이익(GAAP)','Q6':'Non-GAAP 귀속 순이익','Q7g':'ADS당 희석 EPS(GAAP, RMB)','Q7n':'ADS당 희석 EPS(Non-GAAP, RMB)',
     'Q8':'영업활동 현금흐름','Q9':'회사 제시 FCF','Q10':'설비투자','B1':'현금및현금성자산','B5':'총자산','B6':'총자본','A1':'연간 매출(20-F)','A2':'연간 귀속 순이익(20-F)','A3':'연간 영업현금흐름(20-F)','A4':'연간 설비투자(20-F)','X1':'편의환산 환율(RMB/US$)'}
M={
'BABA':{'Q1':('Q1','Q1'),'Q3':('Q3','Q3'),'Q4':('Q4','Q4'),'Q5':('Q5','Q5'),'Q6':('Q6','Q6b'),'Q7g':('Q7_GAAP_diluted_EPS_per_ADS','Q7_GAAP'),'Q7n':('Q7_NonGAAP_diluted_EPS_per_ADS','Q7_NonGAAP'),'Q8':('Q8','Q8'),'Q9':('Q9','Q9'),'Q10':('Q10','Q10'),'B1':('B1','B1'),'B5':('B5','B5'),'B6':('B6_Total_equity','B6_Total equity'),'A1':('A1','A1'),'A2':('A2','A2'),'A3':('A3','A3'),'A4':('A4','A4'),'X1':('X1','X1')},
'BIDU':{'Q1':('Q1','Q1'),'Q3':('Q3','Q3'),'Q4':('Q4','Q4'),'Q5':('Q5','Q5'),'Q6':('Q6','Q6'),'Q7g':('Q7_GAAP','Q7_GAAP_diluted_EPS_per_ADS'),'Q7n':('Q7_NonGAAP','Q7_NonGAAP_diluted_EPS_per_ADS'),'Q8':('Q8','Q8'),'Q9':('Q9','Q9'),'Q10':('Q10','Q10'),'B1':('B1','B1'),'B5':('B5','B5'),'B6':('B6_Total equity','B6_Total_equity'),'A1':('A1','A1'),'A2':('A2','A2'),'A3':('A3','A3'),'A4':('A4','A4_Acquisition_of_fixed_assets'),'X1':('X1','X1_Q2_2026_release')},
'JD':{'Q1':('Q1','Q1'),'Q3':('Q3','Q3'),'Q4':('Q4','Q4'),'Q5':('Q5','Q5'),'Q6':('Q6','Q6'),'Q7g':('Q7_GAAP_diluted_EPS_per_ADS','Q7_GAAP'),'Q7n':('Q7_NonGAAP_diluted_EPS_per_ADS','Q7_NonGAAP'),'Q8':('Q8','Q8'),'Q9':('Q9','Q9'),'Q10':('Q10','Q10'),'B1':('B1','B1'),'B5':('B5','B5'),'B6':('B6_Total_shareholders_equity','B6_Total_shareholders_equity'),'A1':('A1','A1'),'A2':('A2','A2'),'A3':('A3','A3'),'A4':('A4_Purchase_of_PPE_software_intangibles','A4'),'X1':('X1_QREL','X1')}}
CUR=re.compile(r'2026-06-30|June 30, 2026|Q2 2026|FY2027 Q1|FY20(25|26)|2026-03-31|December 31, 2025|2025-12-31|current|^$')
def get(items,i,metric):
    c=[x for x in items if x['id']==i]
    if metric.startswith('A'): c=[x for x in c if re.search('FY|20-F|year',str(x.get('period')))] or c
    elif metric=='X1': pass
    else: c=[x for x in c if re.search(r'2026-06-30|June 30, 2026|Q2 2026|FY2027 Q1',str(x.get('period')))] or c[:1]
    return c[0] if c else None
XT={'A1':['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax'],'A2':['NetIncomeLossAvailableToCommonStockholdersBasic','NetIncomeLoss'],'A3':['NetCashProvidedByUsedInOperatingActivities'],'A4':['PaymentsToAcquirePropertyPlantAndEquipment','PaymentsToAcquireProductiveAssets']}
FYEND={'BABA':'2026-03-31','BIDU':'2025-12-31','JD':'2025-12-31'}
def xbrl(t,m,target=None):
    F=json.load(open(f'data/xbrl_{t}.json'))['facts'].get('us-gaap',{})
    cands=[]
    for tag in XT.get(m,[])+['PaymentsToAcquirePropertyPlantAndEquipment','PaymentsToAcquireProductiveAssets','PaymentsToAcquireOtherPropertyPlantAndEquipment'] if m=='A4' else XT.get(m,[]):
        if tag not in F: continue
        for u,arr in F[tag]['units'].items():
            if u!='CNY': continue
            for x in arr:
                if x['end']==FYEND[t] and x.get('form','').startswith('20-F') and 'start' in x and x['start'][:4]==str(int(FYEND[t][:4])-1)[:4]+'' if t=='BABA' else (x['end']==FYEND[t] and x.get('form','').startswith('20-F') and x.get('start','')==FYEND[t][:4]+'-01-01'):
                    cands.append((x['val']/1e6,tag,u))
    if not cands: return None
    if target is not None:
        for c in cands:
            if abs(abs(c[0])-abs(target))<=max(0.005*abs(target),0.5): return c
    return cands[0]
res={}
for t in M:
    A=json.load(open(f'extract_{t}_A.json'))['items']; B=json.load(open(f'extract_{t}_B.json'))['items']
    rows=[]
    for m,(ia,ib) in M[t].items():
        a=get(A,ia,m); b=get(B,ib,m)
        va=a and a.get('value'); vb=b and b.get('value')
        xv=xbrl(t,m,va if isinstance(va,(int,float)) else None); x=xv[0] if xv else None
        vals=[v for v in (va,vb) if isinstance(v,(int,float))]
        def close(p,q): return abs(p-q)<=max(0.005*abs(q),0.011)
        if len(vals)==2 and close(va,vb):
            if x is not None:
                ok=close(abs(va),abs(x)); st='✔ XBRL·재추출 일치' if ok else '⚠ XBRL 불일치'
            else: st='✔ 이중 추출 일치'
        elif len(vals)==2: st='⚠ 추출 간 불일치'
        else: st='단일 출처' if vals else '자료 없음'
        rows.append(dict(id=m,label=LAB[m],a=va,b=vb,xbrl=x,xtag=(xv[1] if xv else ''),status=st,period=(a or b or {}).get('period'),unit=(a or b or {}).get('unit'),src=(a or b or {}).get('source',{}),note=((a or {}).get('note') or '')[:160]))
    res[t]=rows
    print('==',t)
    for r in rows: print(f"  {r['id']:4} {str(r['a'])[:12]:>12} {str(r['b'])[:12]:>12} {str(r['xbrl'])[:12]:>12} {r['status']}  {r['xtag']}")
json.dump(res,open('data/verification.json','w'),ensure_ascii=False,indent=1)
