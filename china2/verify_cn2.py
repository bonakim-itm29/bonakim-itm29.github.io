"""PDD / NTES / TCOM: A/B extraction cross-check vs XBRL (+ XBRL annual fundamentals)."""
import json, re
LAB = {'Q1': '분기 매출', 'Q3': '영업이익(GAAP)', 'Q4': '조정 영업이익(회사 정의)', 'Q5': '귀속 순이익(GAAP)', 'Q6': 'Non-GAAP 귀속 순이익',
       'Q7g': 'ADS당 희석 EPS(GAAP, RMB)', 'Q7n': 'ADS당 희석 EPS(Non-GAAP, RMB)', 'Q8': '영업활동 현금흐름', 'Q9': '회사 제시 FCF', 'Q10': '설비투자(유형자산 취득)',
       'B1': '현금및현금성자산', 'B2a': '단기투자', 'B2b': '제한현금', 'B2c': '정기예금(유동)', 'B2d': '정기예금(비유동)', 'B2e': '제한현금(비유동)', 'B2f': '만기보유 정기예금·금융상품',
       'B3a': '단기 차입', 'B3b': '장기 차입', 'B4': '순현금(회사 제시)', 'B5': '총자산', 'B6': '총자본',
       'S1': '발행주식 수(최근 공시)', 'R1': '분기 자사주 매입액', 'R2': '배당(ADS당)', 'A1': '연간 매출(20-F)', 'A2': '연간 귀속 순이익(20-F)',
       'A3': '연간 영업현금흐름(20-F)', 'A4': '연간 설비투자(20-F)', 'X1': '편의환산 환율(RMB/US$)'}
CUR = r'2026-06-30|June 30, 2026'
ANN = r'FY2025|2025-12-31|December 31, 2025'
M = {
 'PDD': {'Q1': ('Q1', 'Q1'), 'Q3': ('Q3', 'Q3'), 'Q4': ('Q4', 'Q4'), 'Q5': ('Q5', 'Q5'), 'Q6': ('Q6', 'Q6'),
         'Q7g': ('Q7_GAAP_diluted_EPS_per_ADS', 'Q7_GAAP_diluted_EPS_per_ADS'), 'Q7n': ('Q7_NonGAAP_diluted_EPS_per_ADS', 'Q7_NonGAAP_diluted_EPS_per_ADS'),
         'Q8': ('Q8', 'Q8'), 'Q9': ('Q9', 'Q9'), 'Q10': ('Q10', 'Q10'), 'B1': ('B1', 'B1'), 'B2a': ('B2_Short-term investments', 'B2_Short-term investments'),
         'B2b': ('B2_Restricted cash', 'B2_Restricted cash'), 'B3a': ('B3', 'B3'), 'B4': ('B4', 'B4'), 'B5': ('B5', 'B5'),
         'B6': ('B6_Total Shareholders’ Equity', 'B6_total_equity'), 'S1': ('S1_ordinary_shares_outstanding', 'S1_shares_outstanding', '.'),
         'R1': ('R1', 'R1'), 'R2': ('R2', 'R2', '.'), 'A1': ('A1', 'A1'), 'A2': ('A2', 'A2'), 'A3': ('A3', 'A3'), 'A4': ('A4', 'A4'), 'X1': ('X1', 'X1_quarter')},
 'NTES': {'Q1': ('Q1', 'Q1'), 'Q3': ('Q3', 'Q3'), 'Q4': ('Q4', 'Q4'), 'Q5': ('Q5', 'Q5'), 'Q6': ('Q6', 'Q6'),
          'Q7g': ('Q7_GAAP_diluted_EPS_per_ADS', 'Q7_GAAP_diluted_per_ADS'), 'Q7n': ('Q7_NonGAAP_diluted_EPS_per_ADS', 'Q7_NonGAAP_diluted_per_ADS'),
          'Q8': ('Q8', 'Q8'), 'Q9': ('Q9', 'Q9'), 'Q10': ('Q10', 'Q10'), 'B1': ('B1', 'B1'), 'B2a': ('B2_Short-term investments', 'B2_Short-term investments'),
          'B2c': ('B2_Time deposits (current)', 'B2_Time deposits (current)'), 'B2d': ('B2_Time deposits (non-current)', 'B2_Time deposits (non-current)'),
          'B2b': ('B2_Restricted cash (current)', 'B2_Restricted cash (current)'), 'B2e': ('B2_Restricted cash (non-current)', 'B2_Restricted cash (non-current)'),
          'B3a': ('B3_Short-term loans', 'B3_Short-term loans'), 'B4': ('B4', 'B4'), 'B5': ('B5', 'B5'), 'B6': ('B6_Total equity', 'B6_Total equity'),
          'S1': ('S1_ordinary_shares_issued_excl_treasury', 'S1_issued_shares_excl_treasury'), 'R1': ('R1_Q2_repurchase', 'R1_amount', '.'), 'R2': ('R2', 'R2', '.'),
          'A1': ('A1', 'A1'), 'A2': ('A2', 'A2'), 'A3': ('A3', 'A3'), 'A4': ('A4', 'A4'), 'X1': ('X1', 'X1_quarterly')},
 'TCOM': {'Q1': ('Q1', 'Q1'), 'Q3': ('Q3', 'Q3'), 'Q4': ('Q4', 'Q4_Adjusted EBITDA'), 'Q5': ('Q5', 'Q5'), 'Q6': ('Q6', 'Q6'),
          'Q7g': ('Q7_GAAP', 'Q7_GAAP_diluted_EPS_per_ADS'), 'Q7n': ('Q7_NonGAAP', 'Q7_NonGAAP_diluted_EPS_per_ADS'),
          'Q8': ('Q8', 'Q8'), 'Q9': ('Q9', 'Q9'), 'Q10': ('Q10', 'Q10'), 'B1': ('B1', 'B1'), 'B2a': ('B2_Short-term investments', 'B2_Short-term investments'),
          'B2f': ('B2_Held to maturity time deposit and financial products (within Investments)', 'B2_Held to maturity time deposit and financial products (within Investments)'),
          'B3a': ('B3_Short-term debt and current portion of long-term debt', 'B3_Short-term debt and current portion of long-term debt'), 'B3b': ('B3_Long-term debt', 'B3_Long-term debt'),
          'B4': ('B4', 'B4'), 'B5': ('B5', 'B5'), 'B6': ("B6_Total shareholders' equity", 'B6_Total shareholders’ equity'),
          'S1': ('S1_shares_outstanding', 'S1_shares_outstanding', '.'), 'R1': ('R1_quarterly_buyback', 'R1', '.'), 'R2': ('R2', 'R2', '.'),
          'A1': ('A1', 'A1'), 'A2': ('A2', 'A2'), 'A3': ('A3', 'A3'), 'A4': ('A4', 'A4'), 'X1': ('X1', 'X1_QREL')}}
LABT = {'TCOM': {'Q4': '조정 EBITDA(회사 정의)', 'B1': '현금·현금성자산+제한현금(합산 표시)', 'B3a': '단기 차입(유동성 장기부채 포함)'},
        'PDD': {'B3a': '차입금(사채·대출)'}, 'NTES': {'R1': '2분기 자사주 매입액(월별 합, US$M)'}}
FYEND = '2025-12-31'


def get(items, i, metric, rx=None):
    c = [x for x in items if x['id'] == i]
    if rx == '.': return c[0] if c else None
    if metric.startswith('A'): c = [x for x in c if re.search(ANN, str(x.get('period')))] or c
    else: c = [x for x in c if re.search(CUR, str(x.get('period')))] or c[:1]
    return c[0] if c else None


XT = {'A1': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
      'A2': ['NetIncomeLossAvailableToCommonStockholdersBasic', 'NetIncomeLossAttributableToParent', 'NetIncomeLoss'],
      'A3': ['NetCashProvidedByUsedInOperatingActivities'],
      'A4': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'PaymentsToAcquireOtherPropertyPlantAndEquipment']}


def xbrl(t, m, target=None):
    F = json.load(open(f'data/xbrl_{t}.json'))['facts'].get('us-gaap', {})
    cands = []
    for tag in XT.get(m, []):
        if tag not in F: continue
        for x in F[tag]['units'].get('CNY', []):
            if x['end'] == FYEND and x.get('form', '').startswith('20-F') and x.get('start', '') == '2025-01-01':
                cands.append((x['val'] / 1e6, tag))
    if not cands: return None
    if target is not None:
        for c in cands:
            if abs(abs(c[0]) - abs(target)) <= max(0.005 * abs(target), 0.5): return c
    return cands[0]


def close(p, q): return abs(p - q) <= max(0.005 * abs(q), 0.011)


res = {}
for t in M:
    A = json.load(open(f'extract_{t}_A.json'))['items']; B = json.load(open(f'extract_{t}_B.json'))['items']
    rows = []
    for m, spec in M[t].items():
        ia, ib = spec[0], spec[1]; rx = spec[2] if len(spec) > 2 else None
        a = get(A, ia, m, rx); b = get(B, ib, m, rx)
        va = a and a.get('value'); vb = b and b.get('value')
        xv = xbrl(t, m, va if isinstance(va, (int, float)) else None) if m in XT else None
        x = xv[0] if xv else None
        vals = [v for v in (va, vb) if isinstance(v, (int, float))]
        if len(vals) == 2 and close(va, vb):
            st = ('✔ XBRL·재추출 일치' if close(abs(va), abs(x)) else '⚠ XBRL 불일치') if x is not None else '✔ 이중 추출 일치'
        elif len(vals) == 2: st = '⚠ 추출 간 불일치'
        elif len(vals) == 1: st = '단일 출처'
        else: st = '자료 없음'
        src = (a or b or {})
        note = (src.get('note') or '')
        if len(vals) == 2 and not close(va, vb):
            note = f"1차 {a.get('period')}: {va:,} / 재추출 {b.get('period')}: {vb:,}. " + note
        rows.append(dict(id=m, label=LABT.get(t, {}).get(m, LAB[m]), a=va, b=vb, xbrl=x, xtag=(xv[1] if xv else ''), status=st,
                         period=src.get('period'), unit=src.get('unit'), src=src.get('source', {}), note=note[:200]))
    res[t] = rows
    print('==', t)
    for r in rows: print(f"  {r['id']:4} {str(r['a'])[:12]:>12} {str(r['b'])[:12]:>12} {str(r['xbrl'])[:12]:>12} {r['status']}  {r['xtag']}")
json.dump(res, open('data/verification.json', 'w'), ensure_ascii=False, indent=1)

# ---- XBRL annual fundamentals (latest-filed value per fiscal year) ----
FT = {'rev': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues'],
      'ni': ['NetIncomeLossAvailableToCommonStockholdersBasic', 'NetIncomeLossAttributableToParent', 'NetIncomeLoss'],
      'ocf': ['NetCashProvidedByUsedInOperatingActivities']}
ADSR = {'PDD': 4, 'NTES': 5, 'TCOM': 1}
fund = {}
for t in M:
    F = json.load(open(f'data/xbrl_{t}.json'))['facts']['us-gaap']
    def annual(tag, unit='CNY'):
        d = {}
        for x in F.get(tag, {}).get('units', {}).get(unit, []):
            if x.get('form', '').startswith('20-F') and x['end'][5:] == '12-31' and x.get('start', '')[5:] == '01-01' and x['start'][:4] == x['end'][:4]:
                yy = int(x['end'][:4])
                if yy not in d or x['filed'] > d[yy][0]: d[yy] = (x['filed'], x['val'])
        return {k: v[1] for k, v in d.items()}
    tbl, tags = {}, {}
    for k, tl in FT.items():
        out = {}; used = []
        for tag in tl:
            for yy, v in annual(tag).items():
                if yy not in out:
                    out[yy] = round(v / 1e6, 1)
                    if tag not in used: used.append(tag)
        tbl[k] = out; tags[k] = used
    Y0 = {'PDD': 2016, 'NTES': 2016, 'TCOM': 2017}   # 매출 태그(정의)가 일관된 연도부터
    yrs = [y for y in sorted(set(tbl['rev']) | set(tbl['ni'])) if y >= Y0[t]]
    tbl = {k: {str(y): v.get(y) for y in yrs} for k, v in tbl.items()}
    sh = annual('WeightedAverageNumberOfDilutedSharesOutstanding', 'shares')
    shares = []
    for yy in sorted(sh):
        if yy < 2008: continue
        v = sh[yy]
        if t == 'PDD' and v < 1e8: v *= 1000            # 일부 연도가 천 주 단위로 태그됨
        if t == 'TCOM' and yy <= 2018: v *= 8           # 2021년 1:8 분할 전 보통주(1주 = 8 ADS)
        shares.append([f'{yy}-12-31', v / ADSR[t]])
    fund[t] = dict(years=yrs, tbl=tbl, tags=tags, shares=shares)
    print(t, 'years', yrs[0], yrs[-1], 'rev', tbl['rev'], '\n ni', tbl['ni'], '\n ocf', tbl['ocf'], tags)
    print('  shares', [(a[:4], round(b / 1e6, 1)) for a, b in shares])
json.dump(fund, open('data/fundamentals.json', 'w'), ensure_ascii=False)
