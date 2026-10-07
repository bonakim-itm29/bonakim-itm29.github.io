import json, re, sys
def per(p):
    p=str(p)
    for pat,f in [(r'(20\d\d)\s*Q([1-4])',lambda m:f'{m[1]}Q{m[2]}'),(r'(20\d\d)\s*H1|H1\s*(20\d\d)',lambda m:f'{m[1] or m[2]}H1'),(r'FY\s*(20\d\d)',lambda m:f'FY{m[1]}'),(r'(20\d\d-\d\d-\d\d)',lambda m:m[1])]:
        m=re.search(pat,p)
        if m: return f(m)
    return p
def norm(i): return re.sub(r'[\s()/&,\-]+','_',i.lower()).strip('_')
def load(t,r):
    out={}
    for i in json.load(open(f'extract_{t}_{r}.json'))['items']:
        out[(norm(i['id']),per(i.get('period','')))]=i
    return out
if __name__=='__main__':
    t=sys.argv[1]; A,B=load(t,'A'),load(t,'B')
    ag=df=0
    for k in sorted(set(A)|set(B)):
        a,b=A.get(k),B.get(k); va=a and a.get('value'); vb=b and b.get('value')
        if a and b and va is not None and vb is not None:
            try: ok=abs(float(va)-float(vb))<=max(0.5,abs(float(va))*0.002)
            except: ok=va==vb
            if ok: ag+=1; continue
            df+=1; print('DIFF',k,va,vb,'|',(a.get('note') or '')[:80],'|',(b.get('note') or '')[:80])
        else:
            print('ONLY','A' if a else 'B',k,va if a else vb)
    print(t,'agree',ag,'diff',df)
