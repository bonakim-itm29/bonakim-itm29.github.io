import json, numpy as np, pandas as pd
from annual import annual
y = pd.read_pickle('data/prices.pkl'); fr = pd.read_pickle('data/fred.pkl')
E = json.load(open('data/eda_weekly.json')); M = json.load(open('data/moves.json'))
VF = json.load(open('data/verification.json'))['rows']; VAL = json.load(open('data/val_br.json'))
IX = json.load(open('data/ix20f.json'))
SRC = {'VALE': 'VALE', 'PBR': 'PBR', 'ITUB': 'ITUB', 'NU': 'NU', 'BBD': 'BBD', 'ABEV': 'ABEV', 'SBS': 'SBS', 'EMBJ': 'ERJ', 'AXIA3.SA': 'AXIA'}
CUR = {'VALE': 'US$', 'PBR': 'US$', 'NU': 'US$', 'EMBJ': 'US$', 'ITUB': 'R$', 'BBD': 'R$', 'ABEV': 'R$', 'SBS': 'R$', 'AXIA3.SA': 'R$'}
UNIT = {t: ('US$ millions' if c == 'US$' else 'R$ millions') for t, c in CUR.items()}
SBSIMG = {(i['id'], i['period']): i for i in json.load(open('extract_SBS_IMG.json'))['items']}
def row(t, i, p, label, unit=None):
    s = SRC[t]
    for r in VF[s]:
        if r['id'] == i and r['period'] == p:
            st = {'agree': '✔ 이중 추출 일치', 'single': '단일 출처', 'null': '자료 없음', 'differ': '⚠ 불일치'}[r['status']]
            note = r['note'] or ''
            if r['amb']:
                if s == 'SBS' and (i, p) in SBSIMG and SBSIMG[(i, p)]['status'] == 'ok':
                    note = '페이지 이미지로 재확인 · ' + note[:60]
                else: st = '⚠ 모호(확인 필요)'
            src = r['src'] or {}
            n2 = f"{str(src.get('file',''))[:40]} · {src.get('row','')}".strip(' ·') + (f" · {note}" if note else '')
            return dict(id=f'{i} {p}', label=label, blind=r['b'], prior=r['a'], xbrl=None, status=st, unit=unit or UNIT[t], note=n2[:220])
    raise KeyError((t, i, p))
def g(t, i, p):
    for r in VF[SRC[t]]:
        if r['id'] == i and r['period'] == p: return r['a'] if r['a'] is not None else r['b']
    raise KeyError((t, i, p))
SH = 'shares'
ROWS = {
 'VALE': [('Q1', '2026Q2', '분기 순매출'), ('Q2_Iron Ore Solutions', '2026Q2', '철광석 부문 매출'), ('Q2_Vale Base Metals', '2026Q2', '비철금속(VBM) 매출'), ('Q3', '2026Q2', '조정 EBITDA'), ('Q5', '2026Q2', '귀속 순이익'), ('Q6', '2026Q2', '조정 순이익'),
          ('Q8', '2026Q2', '영업현금흐름'), ('Q9', '2026Q2', '설비투자(회사 제시)'), ('Q10', '2026Q2', 'FCF(회사 제시)'), ('B1', '2026-06-30', '현금'), ('B3', '2026-06-30', '총차입'), ('B4', '2026-06-30', '순부채(회사 제시)'),
          ('B4_Expanded net debt', '2026-06-30', '확장 순부채'), ('S1_Common', '2026-06-30', '유통 보통주', SH), ('R1', '2026H1', '상반기 주주환원 선언(배당+JCP)'), ('OP_Iron ore fines realized price', '2026Q2', '철광석 분광 실현가격(US$/t)', 'US$/t')],
 'PBR': [('Q1', '2026Q2', '분기 매출'), ('Q3_Adjusted EBITDA', '2026Q2', '조정 EBITDA'), ('Q5', '2026Q2', '귀속 순이익'), ('Q5', '2026Q1', '귀속 순이익(1분기)'), ('Q8', '2026Q2', '영업현금흐름'), ('Q9_Total Capex (company)', '2026Q2', '설비투자(회사 제시)'),
         ('Q10', '2026Q2', 'FCF(회사 제시)'), ('B1', '2026-06-30', '현금'), ('B3_Total finance debt', '2026-06-30', '금융부채'), ('B3_Gross debt (company, incl. finance leases)', '2026-06-30', '총부채(리스 포함)'), ('B4', '2026-06-30', '순부채(회사 제시)'),
         ('S1_common', '2026-06-30', '보통주', SH), ('S1_preferred', '2026-06-30', '우선주', SH), ('R1_total', '2026Q2', '2분기 주주환원 선언')],
 'ITUB': [('Q2', '2026Q2', '경상 순이익'), ('Q2', '2026Q1', '경상 순이익(1분기)'), ('Q1', '2026Q2', '회계 순이익'), ('Q3', '2026Q2', '경상 ROE(%)', '%'), ('Q4_managerial_Interest_margin', '2026Q2', '금융마진(경영 기준)'), ('Q5', '2026Q2', '수수료·보험 수익'),
          ('Q6_managerial_Cost_of_Credit', '2026Q2', '신용비용'), ('Q7', '2026Q2', '효율성 지표(%)', '%'), ('B1', '2026-06-30', '대출 포트폴리오'), ('B2', '2026-06-30', '90일 연체율(%)', '%'), ('B4', '2026-06-30', '지배주주지분'),
          ('B5', '2026-06-30', 'CET1(%)', '%'), ('S1_Total', '2026-06-30', '유통주식(보통+우선)', SH), ('R1_total_declared', '2026H1', '상반기 선언 배당·JCP'), ('R2', '2026H1', '상반기 자사주 매입')],
 'BBD': [('Q2', '2026Q2', '경상 순이익'), ('Q2', '2026Q1', '경상 순이익(1분기)'), ('Q3', '2026Q2', '경상 ROE(%)', '%'), ('Q4', '2026Q2', '순이자이익(NII)'), ('Q5', '2026Q2', '수수료 수익'), ('Q6', '2026Q2', '대손비용(확장)'),
         ('Q7', '2026Q2', '효율성 지표(%)', '%'), ('B1', '2026-06-30', '확장 대출 포트폴리오'), ('B2', '2026-06-30', '90일 연체율(%)', '%'), ('B4', '2026-06-30', '지배주주지분'), ('B5', '2026-06-30', 'CET1(%)', '%'),
         ('S1', '2026-06-30', '유통주식(보통+우선)', SH), ('R1_1H26 total accrued (gross)', '2026H1', '상반기 배당·JCP(세전)')],
 'NU': [('Q1', '2026Q2', '귀속 순이익'), ('Q1', '2026Q1', '귀속 순이익(1분기)'), ('Q3', '2026Q2', 'ROE(%)', '%'), ('NU_revenue', '2026Q2', '총수익(IFRS)'), ('Q5', '2026Q2', '수수료 수익'), ('Q6', '2026Q2', '신용손실 비용'),
        ('Q7', '2026Q2', '효율성 지표(%)', '%'), ('NU_customers', '2026Q2', '고객 수(백만 명)', '백만 명'), ('B1_Credit card receivables (gross)', '2026-06-30', '카드 채권(총액)'), ('B1_Total loans (gross)', '2026-06-30', '대출(총액)'),
        ('B6', '2026-06-30', '예금'), ('B4', '2026-06-30', '지배주주지분'), ('B5', '2026-06-30', 'CET1(%)', '%'), ('S1_Class A', '2026-06-30', 'Class A 주식', SH), ('S1_Class B', '2026-06-30', 'Class B 주식', SH), ('R2', '2026H1', '상반기 자사주 매입')],
 'ABEV': [('Q1', '2026Q2', '분기 순매출'), ('Q2_Brazil', '2026Q2', '브라질 매출'), ('Q3', '2026Q2', '정상화 EBITDA'), ('Q5', '2026Q2', '귀속 순이익'), ('Q6', '2026Q2', '정상화 귀속 순이익'), ('Q8', '2026Q2', '영업현금흐름'),
          ('Q9', '2026Q2', '설비투자(현금흐름표)'), ('B1', '2026-06-30', '현금'), ('B3', '2026-06-30', '차입'), ('B4', '2026-06-30', '순부채(음수 = 순현금)'), ('S1_total_issued_ON', '2026-06-30', '발행 보통주(천 주)', '천 주'),
          ('S1_treasury_ON', '2026-06-30', '자기주식(천 주)', '천 주'), ('R1_total', '2026H1', '상반기 JCP'), ('R2_cashflow', '2026H1', '상반기 자사주 매입(현금흐름)')],
 'SBS': [('Q1', '2026Q2', '분기 매출(건설수익 포함)'), ('Q1_Adjusted_Net_Revenue', '2026Q2', '조정 순매출(건설수익 제외)'), ('Q3', '2026Q2', '조정 EBITDA'), ('Q5', '2026Q2', '귀속 순이익'), ('Q6', '2026Q2', '조정 순이익'),
         ('Q8', '2026H1', '상반기 영업현금흐름'), ('Q9_CF', '2026H1', '상반기 설비·계약자산 투자'), ('B1', '2026-06-30', '현금'), ('B2_ST Investments', '2026-06-30', '단기 금융투자'), ('B3', '2026-06-30', '차입·사채'),
         ('B4', '2026-06-30', '순부채(회사 제시)'), ('OP_Tariff_Adjustment', '2026Q2', '요금 조정(%)', '%')],
 'EMBJ': [('Q1', '2026Q2', '분기 매출'), ('Q2_Commercial Aviation', '2026Q2', '상업 항공 매출'), ('Q2_Executive Aviation', '2026Q2', '비즈니스 항공 매출'), ('Q2_Defense & Security', '2026Q2', '방산 매출'),
          ('Q2_Services & Support', '2026Q2', '서비스·지원 매출'), ('Q3', '2026Q2', '조정 EBITDA'), ('Q5', '2026Q2', '귀속 순이익'), ('Q6', '2026Q2', '조정 순이익'), ('Q10', '2026Q2', '조정 FCF(회사 제시, Eve 제외)'),
          ('Q10', '2026H1', '상반기 조정 FCF'), ('B1', '2026-06-30', '현금'), ('B4', '2026-06-30', '순현금, Eve 제외(음수 = 순부채)'), ('B4_Embraer & Eve net cash', '2026-06-30', '연결 순현금(음수 = 순부채)'), ('R1', '2026Q2', '2분기 주주환원(R$)', 'R$ millions')],
 'AXIA3.SA': [('Q1', '2026Q2', '분기 조정 순매출'), ('Q2_Generation', '2026Q2', '발전 매출'), ('Q2_Transmission', '2026Q2', '송전 매출'), ('Q3_Adjusted_EBITDA', '2026Q2', '조정 EBITDA'), ('Q5', '2026H1', '상반기 귀속 순이익'),
              ('Q6_Adjusted_Net_Income', '2026Q2', '조정 순이익'), ('Q8_Managerial_Operating_Cash_Flow', '2026Q2', '영업현금흐름(경영 기준)'), ('Q9_Investments_company', '2026Q2', '투자(회사 제시)'), ('Q10_Free_Cash_Flow', '2026Q2', 'FCF(회사 제시)'),
              ('B1', '2026-06-30', '현금'), ('B3_Gross_Debt_company', '2026-06-30', '총차입(회사 제시)'), ('B4_Net_Debt', '2026-06-30', '순부채(회사 제시)')],
}
def ck(k, a, b): return dict(k=k, a=a, b=b)
CHECKS = {
 'VALE': [ck('1분기 + 2분기 매출 = 상반기', g('VALE', 'Q1', '2026Q1') + g('VALE', 'Q1', '2026Q2'), g('VALE', 'Q1', '2026H1')), ck('1분기 + 2분기 귀속 순이익 = 상반기', g('VALE', 'Q5', '2026Q1') + g('VALE', 'Q5', '2026Q2'), g('VALE', 'Q5', '2026H1')),
          ck('1분기 + 2분기 영업현금흐름 = 상반기', g('VALE', 'Q8', '2026Q1') + g('VALE', 'Q8', '2026Q2'), g('VALE', 'Q8', '2026H1')),
          ck('총차입 + 리스 − 현금 − 단기투자 = 회사 제시 순부채', g('VALE', 'B3', '2026-06-30') + g('VALE', 'B3_Leases', '2026-06-30') - g('VALE', 'B1', '2026-06-30') - g('VALE', 'B2_Short-term investments', '2026-06-30'), g('VALE', 'B4', '2026-06-30'))],
 'PBR': [ck('1분기 + 2분기 매출 = 상반기', g('PBR', 'Q1', '2026Q1') + g('PBR', 'Q1', '2026Q2'), g('PBR', 'Q1', '2026H1')), ck('1분기 + 2분기 귀속 순이익 = 상반기', g('PBR', 'Q5', '2026Q1') + g('PBR', 'Q5', '2026Q2'), g('PBR', 'Q5', '2026H1')),
         ck('총부채(리스 포함) − 현금 − 금융투자 = 회사 제시 순부채', g('PBR', 'B3_Gross debt (company, incl. finance leases)', '2026-06-30') - g('PBR', 'B1', '2026-06-30') - g('PBR', 'B2_Financial investments (total, note 3.2)', '2026-06-30'), g('PBR', 'B4', '2026-06-30'))],
 'ITUB': [ck('1분기 + 2분기 경상 순이익 = 상반기', g('ITUB', 'Q2', '2026Q1') + g('ITUB', 'Q2', '2026Q2'), g('ITUB', 'Q2', '2026H1')),
          ck('부문 경상이익 합 = 2분기 경상 순이익', sum(g('ITUB', 'Q2_' + s, '2026Q2') for s in ['Retail Business', 'Wholesale Business', 'Activities with the Market + Corporation']), g('ITUB', 'Q2', '2026Q2')),
          ck('보통주 + 우선주 = 유통주식(백만 주)', (g('ITUB', 'S1_Common', '2026-06-30') + g('ITUB', 'S1_Preferred', '2026-06-30')) / 1e6, g('ITUB', 'S1_Total', '2026-06-30') / 1e6)],
 'BBD': [ck('1분기 + 2분기 경상 순이익 = 상반기', g('BBD', 'Q2', '2026Q1') + g('BBD', 'Q2', '2026Q2'), g('BBD', 'Q2', '2026H1')), ck('1분기 + 2분기 순이자이익 = 상반기', g('BBD', 'Q4', '2026Q1') + g('BBD', 'Q4', '2026Q2'), g('BBD', 'Q4', '2026H1')),
         ck('1분기 + 2분기 회계 순이익 = 상반기', g('BBD', 'Q1_Book Net Income', '2026Q1') + g('BBD', 'Q1_Book Net Income', '2026Q2'), g('BBD', 'Q1_Book Net Income', '2026H1')),
         ck('발행 보통·우선주 − 자기주식 = 유통주식(백만 주)', (g('BBD', 'S1_Common issued', '2026-06-30') + g('BBD', 'S1_Preferred issued', '2026-06-30') + g('BBD', 'S1_Treasury common', '2026-06-30') + g('BBD', 'S1_Treasury preferred', '2026-06-30')) / 1e6, g('BBD', 'S1', '2026-06-30') / 1e6)],
 'NU': [ck('1분기 + 2분기 귀속 순이익 = 상반기', g('NU', 'Q1', '2026Q1') + g('NU', 'Q1', '2026Q2'), g('NU', 'Q1', '2026H1')), ck('1분기 + 2분기 총수익 = 상반기', g('NU', 'NU_revenue', '2026Q1') + g('NU', 'NU_revenue', '2026Q2'), g('NU', 'NU_revenue', '2026H1')),
        ck('1분기 + 2분기 수수료 수익 = 상반기', g('NU', 'Q5', '2026Q1') + g('NU', 'Q5', '2026Q2'), g('NU', 'Q5', '2026H1'))],
 'ABEV': [ck('1분기 + 2분기 매출 = 상반기', g('ABEV', 'Q1', '2026Q1') + g('ABEV', 'Q1', '2026Q2'), g('ABEV', 'Q1', '2026H1')), ck('1분기 + 2분기 귀속 순이익 = 상반기', g('ABEV', 'Q5', '2026Q1') + g('ABEV', 'Q5', '2026Q2'), g('ABEV', 'Q5', '2026H1')),
          ck('1분기 + 2분기 영업현금흐름 = 상반기', g('ABEV', 'Q8', '2026Q1') + g('ABEV', 'Q8', '2026Q2'), g('ABEV', 'Q8', '2026H1'))],
 'SBS': [ck('1분기 + 2분기 매출 = 상반기', g('SBS', 'Q1', '2026Q1') + g('SBS', 'Q1', '2026Q2'), g('SBS', 'Q1', '2026H1')), ck('1분기 + 2분기 귀속 순이익 = 상반기', g('SBS', 'Q5', '2026Q1') + g('SBS', 'Q5', '2026Q2'), g('SBS', 'Q5', '2026H1')),
         ck('차입·사채 − 현금 − 단기 금융투자 = 회사 제시 순부채', g('SBS', 'B3', '2026-06-30') - g('SBS', 'B1', '2026-06-30') - g('SBS', 'B2_ST Investments', '2026-06-30'), g('SBS', 'B4', '2026-06-30'))],
 'EMBJ': [ck('1분기 + 2분기 매출 = 상반기', g('EMBJ', 'Q1', '2026Q1') + g('EMBJ', 'Q1', '2026Q2'), g('EMBJ', 'Q1', '2026H1')), ck('1분기 + 2분기 귀속 순이익 = 상반기', g('EMBJ', 'Q5', '2026Q1') + g('EMBJ', 'Q5', '2026Q2'), g('EMBJ', 'Q5', '2026H1')),
          ck('1분기 + 2분기 조정 FCF = 상반기', g('EMBJ', 'Q10', '2026Q1') + g('EMBJ', 'Q10', '2026Q2'), g('EMBJ', 'Q10', '2026H1')),
          ck('부문 매출 합 = 2분기 매출', sum(g('EMBJ', 'Q2_' + s, '2026Q2') for s in ['Commercial Aviation', 'Executive Aviation', 'Defense & Security', 'Services & Support', 'Others']), g('EMBJ', 'Q1', '2026Q2'))],
 'AXIA3.SA': [ck('1분기 + 2분기 조정 순매출 = 상반기', g('AXIA3.SA', 'Q1', '2026Q1') + g('AXIA3.SA', 'Q1', '2026Q2'), g('AXIA3.SA', 'Q1', '2026H1')),
              ck('1분기 + 2분기 조정 EBITDA = 상반기', g('AXIA3.SA', 'Q3_Adjusted_EBITDA', '2026Q1') + g('AXIA3.SA', 'Q3_Adjusted_EBITDA', '2026Q2'), g('AXIA3.SA', 'Q3_Adjusted_EBITDA', '2026H1')),
              ck('1분기 + 2분기 조정 순이익 = 상반기', g('AXIA3.SA', 'Q6_Adjusted_Net_Income', '2026Q1') + g('AXIA3.SA', 'Q6_Adjusted_Net_Income', '2026Q2'), g('AXIA3.SA', 'Q6_Adjusted_Net_Income', '2026H1'))],
}
def merge(t, tags):
    out = {}
    for tag in tags:
        a = annual(t, tag)
        for k, v in a.items(): out.setdefault(k, v)
        for k, v in IX.get(t, {}).get(tag, {}).items(): out[int(k)] = v  # 최신 20-F 우선
    return {str(k): out.get(k) for k in range(2021, 2026)}
BANK = {'ITUB', 'BBD', 'NU'}
FUNDTAGS = {
 'default': (['Revenue'], ['CashFlowsFromUsedInOperatingActivities', 'CashFlowFromUsedInOperatingActivities'], ['ProfitLossAttributableToOwnersOfParent'], ['매출', '영업현금흐름', '귀속 순이익']),
 'SBS': (['Revenue'], ['CashFlowsFromUsedInOperatingActivities'], ['ProfitLoss'], ['매출(건설수익 포함)', '영업현금흐름', '순이익']),
 'ITUB': (['Revenue'], ['FeeAndCommissionIncome', 'FeeAndCommissionIncomeExpense'], ['ProfitLossAttributableToOwnersOfParent'], ['영업수익(IFRS)', '수수료 수익', '귀속 순이익']),
 'BBD': (['InterestRevenueExpense'], ['FeeAndCommissionIncome', 'FeeAndCommissionIncomeExpense'], ['ProfitLossAttributableToOwnersOfParent'], ['순이자이익', '수수료 수익', '귀속 순이익']),
 'NU': (['Revenue'], ['FeeAndCommissionIncome', 'FeeAndCommissionIncomeExpense'], ['ProfitLossAttributableToOwnersOfParent'], ['총수익', '수수료 수익', '귀속 순이익']),
}
def snap(asof):
    def pair(s):
        s = s.dropna().loc[:asof]; a = s.iloc[-1]; b = s.loc[:pd.Timestamp(s.index[-1]) - pd.Timedelta(days=365)].iloc[-1]; return [float(a), float(b)]
    return dict(date=asof, BRL=pair(y['BRL=X']), EWZ=pair(y['EWZ']), UST10=pair(fr.DGS10), RR=pair(fr.DFII10), VIX=pair(y['^VIX']), USD=pair(y['DX-Y.NYB']), COPPER=pair(y['HG=F']), SPX=pair(y['^GSPC']))
SNAP = snap('2026-10-06')
peers = {t: v['score']['total'] for t, v in VAL.items()}
PEERNAME = {'AXIA3.SA': 'AXIA', 'EMBJ': 'EMBJ'}
out = {}
for t in SRC:
    vrows = [row(t, *x) for x in ROWS[t]]
    chk = []
    for c in CHECKS[t]:
        ok = abs(c['a'] - c['b']) <= max(1, abs(c['b']) * 0.001)
        chk.append(dict(name=c['k'], lhs=round(c['a'], 1), rhs=round(c['b'], 1), ok=ok)); print(t, c['k'], round(c['a'], 1), round(c['b'], 1), ok)
    V = VAL[t]['val']
    if V['kind'] == 'bank':
        sanity = [dict(name='P/B', val=V['pb'], ok=0.3 < V['pb'] < 8), dict(name='PER(연환산)', val=V['pe'], ok=0 < V['pe'] < 60), dict(name='CET1(%)', val=V['cet1'], ok=8 < V['cet1'] < 20)]
    else:
        sanity = [dict(name='EV/EBITDA', val=V['ev_op'], ok=0 < V['ev_op'] < 40), dict(name='순부채/EBITDA', val=V['nd_ebitda'], ok=-3 < V['nd_ebitda'] < 6), dict(name='PER(연환산)', val=V['pe'] or 0, ok=0 < (V['pe'] or 0) < 80)]
    ft = FUNDTAGS.get(SRC[t], FUNDTAGS['default'])
    fund = dict(years=list(range(2021, 2026)), tbl=dict(rev=merge(SRC[t], ft[0]), ocf=merge(SRC[t], ft[1]), ni=merge(SRC[t], ft[2])), tags={}, shares=[],
                sh_note='연도별 주식 수 시계열은 만들지 않았습니다. 최근 주식 수와 계산 방법은 밸류에이션 타일과 "계산 방법"을 참고하세요.')
    evs = [dict(date=e['date'], R=e['R'], fit=e['fit'], res=e['res'], share=e['share'], type=e['type'], oil=e['oil'], spx=e['spx'], cn=e.get('cn'),
                nf=len(e['filings']), fil=[f"SEC {f['form']} {f['filed']} {f['doc'].split('/')[-1][:40]}" for f in e['filings']][:3]) for e in M[t]['events']]
    mv = dict(threshold=M[t]['threshold'], counts=M[t]['counts'], resid_var_share=M[t]['resid_var_share'], events=evs)
    ev = json.load(open(f'events_{SRC[t]}.json'))
    px = y[t].dropna(); px = px[px.index >= E['res'][t]['start']]; ewz = y['EWZ'].dropna()
    yrs_n = (px.index[-1] - px.index[0]).days / 365.25; dd = px / px.cummax() - 1
    h0 = ewz.loc[:px.index[0]].iloc[-1]; h1 = ewz.loc[:px.index[-1]].iloc[-1]
    stats = dict(start=str(px.index[0].date()), p0=round(float(px.iloc[0]), 2), p1=round(float(px.iloc[-1]), 2), last=str(px.index[-1].date()), tr=float(px.iloc[-1] / px.iloc[0] - 1),
                 cagr=float((px.iloc[-1] / px.iloc[0]) ** (1 / yrs_n) - 1), mdd=float(dd.min()), mdd_date=str(dd.idxmin().date()), peak=round(float(px.max()), 2), peak_date=str(px.idxmax().date()),
                 cmp_start=str(px.index[0].date()), xle_cagr=float((h1 / h0) ** (1 / yrs_n) - 1))
    val = dict(mktcap_m=V['mcap_b'] * 1000, shares_m=V['ads_m'])
    out[t] = dict(ticker=t, cs=CUR[t], pxcur=V['pxcur'], fundlab=ft[3], eda=E['res'][t], moves=mv, events=ev, verify=dict(rows=vrows, checks=chk, sanity=sanity), fund=fund, val=val, cnval=V,
                  scen=VAL[t]['scen'], score=VAL[t]['score'], stats=stats, snap=SNAP, peers={PEERNAME.get(k, k): v for k, v in peers.items()}, peername=PEERNAME.get(t, t))
    print(t, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in stats.items()}, fund['tbl'])
LABELS = dict(E['labels']); LABELS.update(BRL='USD/BRL', EWZ='EWZ', RR='미 10년 실질금리')
json.dump(dict(data=out, labels=LABELS), open('data/page_data.json', 'w'), ensure_ascii=False, default=float)
print(peers)
