import json, re
from cmp import per, norm
def load(t, r):
    return [dict(i, _k=norm(i['id']), _p=per(i.get('period', ''))) for i in json.load(open(f'extract_{t}_{r}.json'))['items']]
def num(v):
    try: return float(v)
    except: return None
res = {}
for t in ['LENOVO', 'XIAOMI', 'BYD']:
    A, B = load(t, 'A'), load(t, 'B'); used = set(); rows = []
    for a in A:
        va = num(a.get('value'))
        cand = [j for j, b in enumerate(B) if j not in used and b['_p'] == a['_p'] and b['_k'] == a['_k']]
        if not cand and va is not None:
            cand = [j for j, b in enumerate(B) if j not in used and b['_p'] == a['_p'] and num(b.get('value')) is not None and abs(abs(num(b['value'])) - abs(va)) <= max(0.5, abs(va) * 0.002)]
        b = B[cand[0]] if cand else None
        if b is not None: used.add(cand[0])
        vb = num(b.get('value')) if b else None
        if va is None and vb is None: st = 'null'
        elif va is None or vb is None: st = 'single'
        else:
            st = 'agree' if abs(abs(va) - abs(vb)) <= max(0.5, abs(va) * 0.002) else ('agree' if abs(va * 1000 - vb) < 1 or abs(vb * 1000 - va) < 1 else 'differ')
        rows.append(dict(id=a['id'], period=a['_p'], a=va, b=vb, status=st, src=a.get('source') or {}, note=(a.get('note') or '')[:160]))
    res[t] = rows
    print(t, {s: sum(r['status'] == s for r in rows) for s in ['agree', 'differ', 'single', 'null']})
    for r in rows:
        if r['status'] == 'differ': print('  DIFF', r['id'], r['period'], r['a'], r['b'])
def g(t, i, p):
    for r in res[t]:
        if r['id'] == i and r['period'] == p: return r['a'] if r['a'] is not None else r['b']
    raise KeyError((t, i, p))
checks = {
 'LENOVO': [dict(k='부문 매출 합계 − 내부거래 = 총매출 (2026Q2)', a=sum(g('LENOVO', 'Q2_' + s, '2026Q2') for s in ['IDG', 'ISG', 'SSG', 'Eliminations']), b=g('LENOVO', 'Q1', '2026Q2')),
            dict(k='현금 + 은행예금 − 총차입 = 회사 제시 순부채', a=g('LENOVO', 'B1', '2026-06-30') + g('LENOVO', 'B2_Bank deposits', '2026-06-30') - g('LENOVO', 'B3_Total borrowings', '2026-06-30'), b=g('LENOVO', 'B4_Net (debt)/cash position', '2026-06-30')),
            dict(k='차입 항목 합계 = 총차입', a=sum(g('LENOVO', 'B3_' + s, '2026-06-30') for s in ['Short-term loans (current)', 'Convertible bonds (current)', 'Notes (non-current)', 'Convertible bonds (non-current)']), b=g('LENOVO', 'B3_Total borrowings', '2026-06-30'))],
 'XIAOMI': [dict(k='부문 매출 합계 = 총매출 (2026Q2)', a=g('XIAOMI', 'Q2_Smartphone × AIoT (Subtotal)', '2026Q2') + g('XIAOMI', 'Q2_Smart EV, AI and other new initiatives', '2026Q2'), b=g('XIAOMI', 'Q1', '2026Q2')),
            dict(k='1분기 + 2분기 매출 = 반기', a=g('XIAOMI', 'Q1', '2026Q1') + g('XIAOMI', 'Q1', '2026Q2'), b=g('XIAOMI', 'H1_매출', '2026H1')),
            dict(k='1분기 + 2분기 귀속순이익 = 반기', a=g('XIAOMI', 'Q5', '2026Q1') + g('XIAOMI', 'Q5', '2026Q2'), b=g('XIAOMI', 'H1_귀속순이익', '2026H1')),
            dict(k='1분기 + 2분기 영업현금흐름 = 반기', a=g('XIAOMI', 'Q8', '2026Q1') + g('XIAOMI', 'Q8', '2026Q2'), b=g('XIAOMI', 'Q8_H1', '2026H1')),
            dict(k='1분기 + 2분기 조정순이익 = 반기', a=g('XIAOMI', 'Q6', '2026Q1') + g('XIAOMI', 'Q6', '2026Q2'), b=g('XIAOMI', 'H1_조정순이익', '2026H1'))],
 'BYD': [dict(k='부문 매출 합계 = 반기 매출', a=sum(g('BYD', 'Q2_' + s, '2026H1') for s in ['Automobiles and related products, and other products', 'Electronics and other products', 'Adjustments and eliminations']), b=g('BYD', 'Q1', '2026H1'))],
}
for t in checks:
    for c in checks[t]:
        c['ok'] = abs(c['a'] - c['b']) <= max(1, abs(c['b']) * 0.001); print(t, c['k'], round(c['a'], 1), round(c['b'], 1), c['ok'])
json.dump(dict(rows=res, checks=checks), open('data/verification.json', 'w'), ensure_ascii=False, default=str)
