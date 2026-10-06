import json, re

def per(p):
    p = str(p)
    m = re.search(r'(20\d\d)\s*Q([1-4])', p)
    if m: return f'{m.group(1)}Q{m.group(2)}'
    m = re.search(r'(20\d\d)\s*H1|H1\s*(20\d\d)', p)
    if m: return f'{m.group(1) or m.group(2)}H1'
    m = re.search(r'(20\d\d-\d\d-\d\d)', p)
    if m: return m.group(1)
    m = re.search(r'FY\s*(20\d\d)|^(20\d\d)$', p)
    if m: return f'FY{m.group(1) or m.group(2)}'
    return p

ALIAS = {'Q2_DS 부문_매출': 'Q2_DS부문_매출', 'Q2_DS 부문_영업이익': 'Q2_DS부문_영업이익', 'Q2_DX 부문_매출': 'Q2_DX부문_매출', 'Q2_DX 부문_영업이익': 'Q2_DX부문_영업이익',
         'Q2_내부거래조정_매출': 'Q2_내부거래조정등_매출', 'Q2_내부거래조정_영업이익': 'Q2_내부거래조정등_영업이익',
         'B3_소계, 비유동': 'B3_차입금(비유동)', 'B3_소계, 유동': 'B3_차입금(유동)', 'B3_합계(주석14)': 'B3_합계',
         'S1_보통주_발행주식총수': 'S1_발행주식총수_보통주', 'S1_보통주_유통주식수': 'S1_유통주식수_보통주', 'S1_보통주_자기주식수': 'S1_자기주식수_보통주', 'S1_자기주식_보통주': 'S1_자기주식수_보통주',
         'R1_소각금액_2026H1': 'R1_자기주식소각금액', 'R1_소각수량_2026H1': 'R1_자기주식소각수량', 'R1_처분수량_2026H1': 'R1_자기주식처분수량', 'R1_취득수량_2026H1': 'R1_자기주식취득수량_기타취득',
         'R2_1분기배당_보통주': 'R2_보통주_2026Q1_분기배당', 'R2_2분기배당_보통주': 'R2_보통주_2026Q2_분기배당', 'R2_주당배당_보통주_2026H1누계': 'R2_보통주_당기누적주당현금배당',
         'R1_보통주_소각금액': 'R1_소각금액_보통주', 'R1_보통주_소각수량': 'R1_소각수량_보통주', 'R1_우선주_소각금액': 'R1_소각금액_우선주', 'R1_우선주_소각수량': 'R1_소각수량_우선주',
         'R1_보통주_취득수량': 'R1_취득수량_보통주', 'R2_2026H1누적_보통주': 'R2_주당배당_보통주'}

def load(t, r):
    out = {}
    for i in json.load(open(f'extract_{t}_{r}.json'))['items']:
        k = ALIAS.get(i['id'], i['id']); p = per(i.get('period', ''))
        if k.startswith('R1_소각') or k.startswith('R1_자기주식소각'): p = '2026H1'
        if k == 'R2_주당배당_보통주' and t == 'SEC' and r == 'B': continue
        out[(k, p)] = dict(v=i.get('value'), src=i.get('source', {}), note=i.get('note', ''))
    return out

res = {}
for t in ['SEC', 'SKH']:
    A, B = load(t, 'A'), load(t, 'B')
    rows = []
    for k in sorted(set(A) | set(B)):
        a, b = A.get(k, {}).get('v'), B.get(k, {}).get('v')
        if a is None and b is None: st = 'null'
        elif a is None or b is None: st = 'single'
        else:
            try: st = 'agree' if abs(float(a) - float(b)) <= max(0.5, abs(float(a)) * 0.001) else 'differ'
            except Exception: st = 'agree' if a == b else 'differ'
        src = (A.get(k) or B.get(k))
        rows.append(dict(id=k[0], period=k[1], a=a, b=b, status=st, src=src['src'], note=str(src['note'])[:160]))
    res[t] = rows
    print(t, {s: sum(1 for r in rows if r['status'] == s) for s in ['agree', 'differ', 'single', 'null']})
    for r in rows:
        if r['status'] == 'differ': print('   DIFF', r['id'], r['period'], r['a'], r['b'])

def g(t, i, p):
    for r in res[t]:
        if r['id'] == i and r['period'] == p: return r['a'] if r['a'] is not None else r['b']
    raise KeyError((t, i, p))

C = {}
t = 'SEC'
C[t] = [dict(k='1분기 + 2분기 매출 = 반기', a=g(t, 'Q1', '2026Q1') + g(t, 'Q1', '2026Q2'), b=g(t, 'H1_매출', '2026H1')),
        dict(k='1분기 + 2분기 영업이익 = 반기', a=g(t, 'Q3', '2026Q1') + g(t, 'Q3', '2026Q2'), b=g(t, 'H1_영업이익', '2026H1')),
        dict(k='1분기 + 2분기 지배순이익 = 반기', a=g(t, 'Q5', '2026Q1') + g(t, 'Q5', '2026Q2'), b=g(t, 'H1_지배순이익', '2026H1')),
        dict(k='부문 매출 합계(내부거래 조정 포함) = 총매출 (2분기)', a=sum(g(t, s, '2026Q2') for s in ['Q2_DS부문_매출', 'Q2_DX부문_매출', 'Q2_SDC_매출', 'Q2_Haman_매출', 'Q2_내부거래조정등_매출']), b=g(t, 'Q1', '2026Q2')),
        dict(k='발행주식 − 자기주식 = 유통주식 (보통주)', a=g(t, 'S1_발행주식총수_보통주', '2026-06-30') - g(t, 'S1_자기주식수_보통주', '2026-06-30'), b=g(t, 'S1_유통주식수_보통주', '2026-06-30'))]
t = 'SKH'
C[t] = [dict(k='1분기 + 2분기 매출 = 반기', a=g(t, 'Q1', '2026Q1') + g(t, 'Q1', '2026Q2'), b=g(t, 'H1_매출', '2026H1')),
        dict(k='1분기 + 2분기 영업이익 = 반기', a=g(t, 'Q3', '2026Q1') + g(t, 'Q3', '2026Q2'), b=g(t, 'H1_영업이익', '2026H1')),
        dict(k='1분기 + 2분기 지배순이익 = 반기', a=g(t, 'Q5', '2026Q1') + g(t, 'Q5', '2026Q2'), b=g(t, 'H1_지배순이익', '2026H1')),
        dict(k='DRAM + NAND + 기타 = 총매출 (2분기)', a=sum(g(t, s, '2026Q2') for s in ['Q2_DRAM_매출', 'Q2_NAND Flash_매출', 'Q2_기타_매출']), b=g(t, 'Q1', '2026Q2')),
        dict(k='차입 항목 합계 = 주석 합계', a=sum(g(t, s, '2026-06-30') for s in ['B3_단기차입금', 'B3_유동성장기차입금', 'B3_유동성사채', 'B3_장기차입금', 'B3_사채']), b=g(t, 'B3_합계', '2026-06-30')),
        dict(k='발행주식 − 자기주식 = 유통주식', a=g(t, 'S1_발행주식총수_보통주', '2026-06-30') - g(t, 'S1_자기주식수_보통주', '2026-06-30'), b=g(t, 'S1_유통주식수_보통주', '2026-06-30'))]
for t in C:
    for c in C[t]:
        c['ok'] = abs(c['a'] - c['b']) <= max(1, abs(c['b']) * 0.001)
        print(t, c['k'], c['a'], c['b'], c['ok'])
json.dump(dict(rows=res, checks=C), open('data/verification.json', 'w'), ensure_ascii=False, default=str)
