# 유가 시나리오별 EV/EBITDAX·PER 적정주가
import json
N = json.load(open('data/nav_scen.json'))
C = {  # Q2 2026 실적(검증 표), 헤지 정산손실은 원문 수치로 되돌림(헤지 전 기준)
 'CRGY': dict(ebitdax=797.94, hedge=(96.61 - 73.33) * 140 * 91 / 1000, adjni=263.007, oilq=140 * 91 / 1000, p0=95.65, bench='WTI', tp=2.27 / 45.76, tm=0.21, nd=4901.0, sh=330.403696, price=13.15,
             hnote='CRGY 헤지 손실은 원유 실현가 차이($96.61 → $73.33) × 원유 판매량으로 계산했습니다(가스 헤지 제외).'),
 'KOS':  dict(ebitdax=311.656, hedge=105.381, adjni=68.177, oilq=4.571, p0=102.63, bench='Brent', tp=0.0, tm=0.35, nd=2563.445, sh=595.487651, price=2.65,
             hnote='KOS 헤지 손실은 2분기 파생상품 현금정산 $105.4M(전 상품)입니다. 원유 물량은 판매량 4,571 MBbl 기준입니다.'),
 'SM':   dict(ebitdax=1406.0, hedge=5.5 * 439.7 * 91 / 1000, adjni=526.0, oilq=229.8 * 91 / 1000, p0=95.65, bench='WTI', tp=3.25 / 62.48, tm=0.21, nd=6253.0, sh=237.854068, price=33.91,
             hnote='SM 헤지 손실은 파생상품 정산 −$5.50/Boe × 판매량으로 계산했습니다(7/16 8-K의 약 $220M과 일치).'),
}
EVM = (3.0, 4.0, 5.0); PEM = (6.0, 8.0, 10.0)
out = {}
for t, c in C.items():
    ebit_u = c['ebitdax'] + c['hedge']            # 헤지 전 분기 EBITDAX
    ni_u = c['adjni'] + c['hedge'] * (1 - c['tm'])
    cur_m = (c['price'] * c['sh'] + c['nd']) / (4 * c['ebitdax'])
    def ann(P):
        d = c['oilq'] * (P - c['p0']) * (1 - c['tp'])
        return 4 * (ebit_u + d), 4 * (ni_u + d * (1 - c['tm']))
    rows = []
    for lab, P in [(f"선물 스트립 환산 {c['bench']}", N['res'][t]['fut']), (f"2분기 평균 {c['bench']}(헤지 전)", c['p0']), (f"{c['bench']} $100", 100.0), (f"{c['bench']} $150", 150.0), (f"{c['bench']} $200", 200.0)]:
        e, n = ann(P)
        ev = [(m * e - c['nd']) / c['sh'] for m in EVM]
        pe = [m * n / c['sh'] for m in PEM]
        rows.append(dict(label=lab, oil=P, ebitdax=round(e, 0), ni=round(n, 0), eps=round(n / c['sh'], 2),
                         ev=[round(x, 2) for x in ev], pe=[round(x, 2) for x in pe], cur=round((cur_m * e - c['nd']) / c['sh'], 2)))
    out[t] = dict(bench=c['bench'], price=c['price'], cur_m=cur_m, evm=EVM, pem=PEM, rows=rows, hedge_q=c['hedge'], tp=c['tp'], tm=c['tm'], note=c['hnote'],
                  per10_ebitdax=4 * c['oilq'] * 10 * (1 - c['tp']))
    print(t, 'cur EV/EBITDAX %.2f' % cur_m, 'hedge %.0f' % c['hedge'])
    for r in rows: print('   ', r['label'], r['ebitdax'], r['ni'], 'EV', r['ev'], 'PE', r['pe'], 'cur', r['cur'])
N['mult'] = out
json.dump(N, open('data/nav_scen.json', 'w'), ensure_ascii=False)
