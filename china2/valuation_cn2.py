"""PDD / NTES / TCOM valuation + 10-point score (same rules as ../china/valuation_cn.py)."""
import json, pandas as pd
clip = lambda x, a=0.0, b=1.0: max(a, min(b, x))
y = pd.read_pickle('data/prices.pkl')
ASOF = '2026-10-02'                                     # US 종목 마지막 완전 거래일
px = lambda t: float(y[t].dropna().loc[:ASOF].iloc[-1])
FX = px('CNY=X')                                        # RMB per USD, 10/2 이전 마지막 값
FX_DATE = str(y['CNY=X'].dropna().loc[:ASOF].index[-1].date())
# 모든 RMB 값은 verification.json의 이중 추출 일치 값(백만 위안). (계산)은 아래 산식.
V = {
 'PDD': dict(price=px('PDD'), ads=5693.585848 / 4, ads_note='발행주식 5,693.6M주(2025-12-31, 20-F 표지 — 분기 실적발표문에는 주식 수 없음), ADS 1 = 4주(계산)',
             debt=0, liq=128918 + 327496, liq_label='현금및현금성자산 + 단기투자(회사 문장 "RMB456.4bn"과 일치; 제한현금·기타 비유동자산 제외)',
             op=(29071, 21090), op_label='Non-GAAP 영업이익(영업이익 + 주식보상)', op_short='조정 영업이익',
             ni=(28489, 14071), ni_label='Non-GAAP 귀속 순이익',
             fcf_ann=106938.69 - 1145.077, fcf_basis='2025년 연간(20-F)', fcf_note='회사 FCF 지표가 없고 분기 설비투자도 공시되지 않아, 2025년 20-F의 영업현금흐름 ¥106,938.7M + 설비투자 −¥1,145.1M = ¥105,793.6M(계산)을 썼습니다'),
 'NTES': dict(price=px('NTES'), ads=3201.250981 / 5, ads_note='발행주식 3,201.3M주(자사주 제외, 2026-06-30 HKEX 월간 보고), ADS 1 = 5주(계산)',
              debt=12604.17, liq=22814.542 + 101978.645 + 260.0 + 4447.483 + 3.775 + 50599.638,
              liq_label='현금·정기예금(유동·비유동)·제한현금·단기투자 합계(회사 제시 순현금 ¥167.5B의 구성 항목)',
              op=(12089.338, 12656.833), op_label='GAAP 영업이익(회사가 조정 영업이익을 제시하지 않음 — 주식보상을 더하지 않아 보수적)', op_short='영업이익(GAAP)',
              ni=(7746.714, 11274.824), ni_label='Non-GAAP 귀속 순이익(주식보상 제외)',
              fcf=((9972.929 - 18.785 - 61.554), (13733.071 - 312.148 - 290.019)), fcf_basis='최근 2개 분기 연환산',
              fcf_note='회사 FCF 지표가 없어 영업현금흐름 − 유형자산 취득 − 무형자산·콘텐츠 취득으로 계산했습니다(2분기 ¥9,892.6M, 1분기 ¥13,130.9M, 계산)'),
 'TCOM': dict(price=px('TCOM'), ads=629.705222, ads_note='발행주식 629.7M주(2026-03-31, 20-F Item 6.E — 예탁기관 대량발행분 86.2M주 제외), ADS 1 = 1주',
              debt=25767 + 630, liq=56016 + 23499 + 21001,
              liq_label='현금·현금성자산+제한현금(합산 표시)·단기투자·만기보유 정기예금/금융상품(회사 문장 "RMB100.5bn"과 일치)',
              op=(4565, 4830), op_label='조정 EBITDA(회사 정의: 영업손익 + 주식보상 + 감가상각 + 반독점 과징금)', op_short='조정 EBITDA',
              ni=(4798, 3905), ni_label='Non-GAAP 귀속 순이익(과징금·주식보상·평가손익 제외)',
              fcf_ann=14379 - 797, fcf_basis='2025년 연간(20-F)', fcf_note='분기 실적발표문에 현금흐름표가 없어, 2025년 20-F의 영업현금흐름 ¥14,379M + 설비투자 −¥797M = ¥13,582M(계산)을 썼습니다'),
}
E = json.load(open('data/eda_weekly.json'))['res']; M = json.load(open('data/moves.json'))
FW = {'PDD': 0.25, 'NTES': 0.25, 'TCOM': 0.25}   # 26.07.07 칼럼에 거명되지 않음
OPRULE = {'PDD': '회사 Non-GAAP 영업이익 기준.',
          'NTES': '회사가 조정 영업이익을 내지 않아 가장 가까운 공시치인 GAAP 영업이익을 썼습니다(보수적).',
          'TCOM': '회사가 조정 영업이익을 내지 않아 회사 정의 조정 EBITDA를 썼습니다. 2분기 GAAP 영업손실(−¥1,462M)은 일회성 반독점 과징금 ¥5,180M 때문이라 조정치를 씁니다(감가상각 전이라 배수가 다소 낮게 나옴).'}
OPK = {'PDD': 'EV/Non-GAAP 영업이익', 'NTES': 'EV/영업이익(GAAP, 조정치 미공시)', 'TCOM': 'EV/조정 EBITDA'}
NIRULE = {'PDD': '', 'NTES': '', 'TCOM': ' 2분기 GAAP 순손실은 과징금 때문이라 Non-GAAP를 씁니다.'}
out = {}
for t, v in V.items():
    mc = v['price'] * v['ads'] / 1e3
    nc = (v['liq'] - v['debt']) / FX / 1e3
    ev = mc - nc
    op = sum(v['op']) * 2 / FX / 1e3; op_q = v['op'][0] * 4 / FX / 1e3
    ni = sum(v['ni']) * 2 / FX / 1e3; ni_q = v['ni'][0] * 4 / FX / 1e3
    fcf = (sum(v['fcf']) * 2 if 'fcf' in v else v['fcf_ann']) / FX / 1e3
    eps = ni / v['ads'] * 1e3; eps_q = ni_q / v['ads'] * 1e3; ncps = nc / v['ads'] * 1e3
    met = dict(price=v['price'], asof=ASOF, ads_m=v['ads'], mcap_b=mc, netcash_b=nc, ev_b=ev, ev_op=ev / op, ev_op_q=ev / op_q, pe=mc / ni, pe_q=mc / ni_q,
               pe_excash=(mc - nc) / ni, fcf_yield=fcf / mc, fcf_b=fcf, nc_share=nc / mc, eps_h1=eps, eps_q=eps_q, ncps=ncps, fx=FX, fx_date=FX_DATE,
               debt_rmb=round(v['debt'], 1), liq_rmb=round(v['liq'], 1), liq_label=v['liq_label'], op_label=v['op_label'], op_short=v['op_short'], ni_label=v['ni_label'],
               ads_note=v['ads_note'], fcf_basis=v['fcf_basis'], fcf_note=v['fcf_note'])
    rows = [dict(label=lab, eps=round(e, 2), vals=[round(m * e, 2) for m in (8, 12, 16)]) for lab, e in [('최근 2개 분기 연환산', eps), ('최근 분기 × 4', eps_q)]]
    implied_pe = v['price'] / eps          # 현재 주가 ÷ EPS(최근 2개 분기 연환산)
    e = E[t]['full']; bc = e['beta_cny']; bs = e['beta_spx']; r2 = e['r2']; rv = M[t]['resid_var_share']; cq = E[t]['corr_q']['OIL']
    A = [dict(k='중국/홍콩 주식 강세 신호', val='강세 · 신뢰도 높음(69% vs 49%)', pts=1.5, max=1.5, rule='프레임워크의 중국/홍콩 입장(관심 종목 공통)'),
         dict(k='저자의 종목 거명', val='직접 거명 없음', pts=FW[t], max=0.5, rule='26.07.07 "버려진 현금흐름 자산" 칼럼에서 거명되면 0.5, 아니면 0.25'),
         dict(k='달러 약세·위안화 강세 수혜(위안화 베타)', val=f'{bc:.2f}', pts=round(clip(-bc / 3), 2), max=1.0, rule='저자는 달러 약세를 전망. 위안화 1% 강세 시 주가 반응이 클수록 높음(−3 이하 만점)')]
    B = [dict(k=OPK[t], val=f'{ev/op:.1f}배', pts=round(clip((25 - ev / op) / 20), 2), max=1.0, rule='5배 이하 만점, 25배 이상 0점. ' + OPRULE[t]),
         dict(k='PER(Non-GAAP)', val=f'{mc/ni:.1f}배', pts=round(clip((25 - mc / ni) / 17), 2), max=1.0, rule='8배 이하 만점, 25배 이상 0점.' + NIRULE[t]),
         dict(k='FCF 수익률', val=f'{fcf/mc*100:.1f}%', pts=round(clip(fcf / mc / 0.10), 2), max=1.0, rule='10% 이상 만점, 0% 이하 0점. ' + v['fcf_note'] + '.'),
         dict(k='순현금/시가총액', val=f'{nc/mc*100:.0f}%', pts=round(clip(nc / mc / 0.5), 2), max=1.0, rule='50% 이상 만점')]
    C = [dict(k='미국 주식 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 저자는 미국 주식 약세를 봄'),
         dict(k='항셍 연동성(분기 상관)', val=f'{cq:.2f}', pts=round(clip(cq / 0.7), 2), max=1.0, rule='저자는 홍콩 주식 강세를 봄. 0.7 이상 만점, 0 이하 0점(사이는 비례)'),
         dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {rv*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달될수록 높음. 점수 = 0.5×min(R²/0.45, 1) + 0.5×min(max((0.9 − 비매크로 비중)/0.3, 0), 1)')]
    if t != 'PDD': B[0]['warn'] = True
    if t in ('PDD', 'TCOM'): B[2]['warn'] = True
    sA, sB, sC = (round(sum(x['pts'] for x in L), 2) for L in (A, B, C))
    score = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    out[t] = dict(val=met, scen=dict(rows=rows, implied_pe=implied_pe, ncps=ncps, mults=[8, 12, 16]), score=score)
    print(t, {k: (round(v2, 3) if isinstance(v2, float) else v2) for k, v2 in met.items() if not isinstance(v2, str)}, 'impliedPE %.2f' % implied_pe)
    print('   score', score['total'], sA, sB, sC, [(i['k'], i['val'], i['pts']) for L in (A, B, C) for i in L])
    for r in rows: print('   ', r)
json.dump(out, open('data/val_cn2.json', 'w'), ensure_ascii=False)
