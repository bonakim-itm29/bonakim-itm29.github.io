import json, sys
from cmp import per, norm
T9 = ['VALE','PBR','ITUB','NU','BBD','ABEV','SBS','ERJ','AXIA']
def load(t, r):
    return [dict(i, _k=norm(i['id']), _p=per(i.get('period', ''))) for i in json.load(open(f'extract_{t}_{r}.json'))['items']]
def num(v):
    try: return float(v)
    except: return None
res = {}
for t in T9:
    A, B = load(t, 'A'), load(t, 'B'); used = set(); rows = []
    for a in A:
        va = num(a.get('value'))
        cand = [j for j, b in enumerate(B) if j not in used and b['_p'] == a['_p'] and b['_k'] == a['_k']]
        if not cand and va is not None:
            cand = [j for j, b in enumerate(B) if j not in used and b['_p'] == a['_p'] and num(b.get('value')) is not None and abs(abs(num(b['value'])) - abs(va)) <= max(0.05, abs(va) * 0.002)]
        b = B[cand[0]] if cand else None
        if b is not None: used.add(cand[0])
        vb = num(b.get('value')) if b else None
        if va is None and vb is None: st = 'null'
        elif va is None or vb is None: st = 'single'
        else: st = 'agree' if abs(abs(va) - abs(vb)) <= max(0.05, abs(va) * 0.002) else 'differ'
        amb = a.get('status') == 'ambiguous' or (b is not None and b.get('status') == 'ambiguous')
        rows.append(dict(id=a['id'], period=a['_p'], a=va, b=vb, status=st, amb=amb, src=a.get('source') or {}, note=(a.get('note') or '')[:160], bid=b['id'] if b else None))
    res[t] = rows
    print(t, {s: sum(r['status'] == s for r in rows) for s in ['agree', 'differ', 'single', 'null']}, 'amb', sum(r['amb'] for r in rows))
    if '-v' in sys.argv:
        for r in rows:
            if r['status'] == 'differ': print('  DIFF', r['id'], r['period'], r['a'], r['b'], r['bid'])
json.dump(dict(rows=res), open('data/verification.json', 'w'), ensure_ascii=False, default=str)
