import json, re
T = {'TCEHY': 'TCEHY', 'MEITUAN': 'MEITUAN'}

def per(p):
    p = str(p)
    m = re.search(r'(20\d\d)\s*Q([1-4])', p)
    if m: return f'{m.group(1)}Q{m.group(2)}'
    m = re.search(r'H1\s*(20\d\d)|(20\d\d)\s*H1', p)
    if m: return f'{m.group(1) or m.group(2)}H1'
    m = re.search(r'FY\s*(20\d\d)', p)
    if m: return f'FY{m.group(1)}'
    m = re.search(r'(20\d\d-\d\d-\d\d)', p)
    if m: return m.group(1)
    return p

ALIAS = {'Q2_VAS': 'Q2_Value-added Services', 'Q4': 'Q4_Non-IFRS operating profit', 'Q6': 'Q6_Non-IFRS profit attributable to equity holders of the Company',
         'Q7_IFRS_diluted_EPS': 'Q7_IFRS diluted EPS', 'Q7_NonIFRS_diluted_EPS': 'Q7_Non-IFRS diluted EPS', 'R1_amount_HKD': 'R1_amount',
         'B6_Equity attributable to equity holders of the Company': 'B6_Equity attributable to equity holders', 'Q8_H1': 'Q8',
         'Q4_segment operating profit/(loss)_Core Local Commerce': 'Q4_Segment operating profit/(loss)_Core Local Commerce',
         'Q4_segment operating profit/(loss)_New Initiatives': 'Q4_Segment operating profit/(loss)_New Initiatives',
         'Q4_segment operating profit/(loss)_Unallocated items': 'Q4_Segment operating profit/(loss)_Unallocated items',
         'H1_Adjusted net (loss)/profit': 'Q6_Adjusted net profit', 'R2_DPS': 'R2_per_share', 'R2_total_HKD': 'R2_total'}

def load(t, r):
    out = {}
    for i in json.load(open(f'extract_{t}_{r}.json'))['items']:
        k = (ALIAS.get(i['id'], i['id']), per(i.get('period', '')))
        v = i.get('value')
        if k[0] == 'R2_total' and v and v > 1e6: v = v / 1e6   # HKD -> HKD millions
        if k[0].startswith('H1_IFRS diluted EPS'): k = ('Q7_IFRS diluted EPS', k[1])
        out[k] = dict(v=v, src=i.get('source', {}), status=i.get('status'), note=i.get('note', ''))
    return out

res = {}
for t in T:
    A, B = load(t, 'A'), load(t, 'B')
    rows = []
    for k in sorted(set(A) | set(B)):
        a, b = A.get(k, {}).get('v'), B.get(k, {}).get('v')
        if a is None and b is None: st = 'null'
        elif a is None or b is None: st = 'single'
        else:
            try: st = 'agree' if abs(float(a) - float(b)) <= max(0.5, abs(float(a)) * 0.002) else 'differ'
            except Exception: st = 'agree' if a == b else 'differ'
        rows.append(dict(id=k[0], period=k[1], a=a, b=b, status=st, src=(A.get(k) or B.get(k))['src'], note=(A.get(k) or B.get(k))['note'][:160]))
    res[t] = rows
    c = {s: sum(1 for r in rows if r['status'] == s) for s in ['agree', 'differ', 'single', 'null']}
    print(t, c)
    for r in rows:
        if r['status'] == 'differ': print('   DIFF', r['id'], r['period'], r['a'], r['b'])

def g(t, i, p):
    for r in res[t]:
        if r['id'] == i and r['period'] == p: return r['a'] if r['a'] is not None else r['b']

checks = {}
# Tencent
t = 'TCEHY'
seg = sum(g(t, s, '2026Q2') for s in ['Q2_Value-added Services', 'Q2_Marketing Services', 'Q2_FinTech and Business Services', 'Q2_Others'])
checks[t] = [
    dict(k='부문 매출 합계 = 총매출 (2026Q2)', a=seg, b=g(t, 'Q1', '2026Q2')),
    dict(k='1분기 + 2분기 매출 = 반기', a=g(t, 'Q1', '2026Q1') + g(t, 'Q1', '2026Q2'), b=g(t, 'H1_매출', '2026H1')),
    dict(k='1분기 + 2분기 귀속순이익 = 반기', a=g(t, 'Q5', '2026Q1') + g(t, 'Q5', '2026Q2'), b=g(t, 'H1_귀속순이익', '2026H1')),
    dict(k='회사 제시 순현금 = 현금 + 정기예금 등 − 차입 − 사채', a=g(t, 'B1', '2026-06-30') + g(t, 'B2_Term deposits and others', '2026-06-30') - g(t, 'B3_Borrowings (current)', '2026-06-30') - g(t, 'B3_Borrowings (non-current)', '2026-06-30') - g(t, 'B3_Notes payable (current)', '2026-06-30') - g(t, 'B3_Notes payable (non-current)', '2026-06-30'), b=g(t, 'B4', '2026-06-30')),
]
t = 'MEITUAN'
checks[t] = [
    dict(k='부문 매출 합계 = 총매출 (2026Q2)', a=g(t, 'Q2_Core Local Commerce', '2026Q2') + g(t, 'Q2_New Initiatives', '2026Q2'), b=g(t, 'Q1', '2026Q2')),
    dict(k='1분기 + 2분기 매출 = 반기', a=g(t, 'Q1', '2026Q1') + g(t, 'Q1', '2026Q2'), b=g(t, 'H1_매출', '2026H1')),
    dict(k='1분기 + 2분기 영업현금흐름 = 반기', a=g(t, 'Q8', '2026Q1') + g(t, 'Q8', '2026Q2'), b=g(t, 'Q8', '2026H1')),
    dict(k='1분기 + 2분기 조정순이익 = 반기', a=g(t, 'Q6_Adjusted net profit', '2026Q1') + g(t, 'Q6_Adjusted net profit', '2026Q2'), b=g(t, 'Q6_Adjusted net profit', '2026H1')),
    dict(k='부문 영업이익 합계 = 영업이익 (2026Q2)', a=sum(g(t, 'Q4_Segment operating profit/(loss)_' + s, '2026Q2') for s in ['Core Local Commerce', 'New Initiatives', 'Unallocated items']), b=g(t, 'Q3', '2026Q2')),
]
for t in checks:
    for c in checks[t]:
        c['ok'] = abs(c['a'] - c['b']) <= max(1, abs(c['b']) * 0.001)
        print(t, c['k'], round(c['a'], 1), round(c['b'], 1), c['ok'])
json.dump(dict(rows=res, checks=checks), open('data/verification.json', 'w'), ensure_ascii=False, default=str)
