# 유가 시나리오별 세후 NAV (Standardized Measure 증분 모델)
import json, numpy as np
F = json.load(open('data/futures_strip.json'))
def strip(root):
    by = {}
    for sym, meta, close, dt in [r + [None] * (4 - len(r)) for r in F[root]]:
        v = close if isinstance(close, (int, float)) else None
        if v is None: continue
        by.setdefault(2000 + int(sym[3:5]), []).append(v)
    return {y: float(np.mean(v)) for y, v in sorted(by.items())}
CL, BZ = strip('CL'), strip('BZ')
spread = np.mean([BZ[y] - CL[y] for y in (2028, 2029) if y in BZ and y in CL])
BRENT = {y: (BZ[y] if y in BZ and y <= 2028 else CL[y] + spread) for y in CL}

def equiv(curve, life):
    """매장량 수명(life년) 동안 연 10% 할인 가중 평균. 2031년 이후는 마지막 해 가격 유지."""
    ys = sorted(curve); last = curve[ys[-1]]
    w = []; p = []
    for k in range(int(round(life))):
        y = 2027 + k
        p.append(curve.get(y, last)); w.append(1.1 ** -(k + 0.5))
    return float(np.dot(w, p) / sum(w))

C = {  # 입력: 모두 10-K/10-Q 원문 추출값(std_*.json, 검증 표) + 표시한 가정
 'CRGY': dict(S7=7755.55, S5=13153.408, oil=359.695, pbase=65.34, bench='WTI', nd=4901.0, sh=330.403696, price=13.15, rp=975.518 / (335 * .365), tp=0.05, tm=0.21, curve=CL, now=96.41),
 'KOS':  dict(S7=1890.0, S5=3314.0, oil=120.0, pbase=69.51, bench='Brent', nd=2563.445, sh=595.487651, price=2.65, rp=249 / (71.4 * .365), tp=0.0, tm=0.35, curve=BRENT, now=114.89),
 'REI':  dict(S7=1123.493, S5=2526.885, oil=90.320048, pbase=61.82, bench='WTI', nd=361.58, sh=260.539607, price=1.36, rp=153.278 / (19.99 * .365), tp=0.07, tm=0.21, curve=CL, now=96.41),
 'SM':   dict(S7=13576 - 660, S5=21685, dS7=13576, oil=616.4 * (1 - 168.1 / 1531.6), pbase=65.34, bench='WTI', nd=6253.0, sh=237.854068, price=33.91, rp=(1531.6 - 168.1) / (439.7 * .365), tp=0.052, tm=0.21, curve=CL, now=96.41),
}
NOTE = {
 'CRGY': [],
 'KOS': ['KOS는 SEC 기준 Brent 가격을 공시하지 않아, FRED Brent의 2025년 매월 첫 거래일 평균($69.51)으로 재계산해 썼습니다(근사).', 'KOS의 원유 물량 120 MMBbl에는 NGL이 포함돼 있어 원유 가격에 같이 연동했습니다(소폭 과대).', '생산물분배계약 구조상 증분 생산세는 0으로 두었습니다.'],
 'REI': ['REI의 SEC 기준가 $61.82는 공시가(posted) 기준이라 다른 회사($65.34)보다 낮습니다.'],
 'SM': ['SM은 합산(pro forma) 매장량 기준입니다. 4월 매각분(168.1 MMBoe, 세후 $660M)의 제품별 물량이 공시되지 않아, 원유 물량을 매각 비중(11%)만큼 비례 차감했습니다(가정).'],
}
out = {}
for t, c in C.items():
    d = c.get('dS7', c['S7']) / c['S5']                       # 세후 할인율 비(현재가치/할인 전)
    k = d * c['oil'] * (1 - c['tp']) * (1 - c['tm'])   # 유가 $1 변화당 세후 PV 변화($M)
    nav = lambda P: (c['S7'] + k * (P - c['pbase']) - c['nd']) / c['sh']
    fut = equiv(c['curve'], c['rp'])
    implied = c['pbase'] + (c['price'] * c['sh'] - (c['S7'] - c['nd'])) / k
    rows = [('SEC 기준가(2025년 평균)', c['pbase']), (f'선물 스트립 환산', fut), (f'현재 {c["bench"]} 유지', c['now']),
            (f'{c["bench"]} $100', 100.0), (f'{c["bench"]} $150', 150.0), (f'{c["bench"]} $200', 200.0)]
    out[t] = dict(bench=c['bench'], price=c['price'], k_per_dollar=k, per10=10 * k / c['sh'], disc=d, life=c['rp'], implied=implied,
                  strip={str(y): round(v, 2) for y, v in c['curve'].items()}, fut=fut,
                  rows=[dict(label=l, oil=round(P, 2), nav=round(nav(P), 2), pnav=(round(c['price'] / nav(P), 2) if nav(P) > 0 else None)) for l, P in rows],
                  params=dict(tp=c['tp'], tm=c['tm'], oil=c['oil'], pbase=c['pbase'], S7=c['S7'], S5=c['S5'], nd=c['nd'], sh=c['sh']),
                  notes=NOTE[t])
    print(t, 'd=%.3f k=$%.1fM/$' % (d, k), '$10당 NAV %.2f' % (10 * k / c['sh']), 'life %.1f' % c['rp'], 'fut %.1f' % fut, 'implied %.1f' % implied)
    for r in out[t]['rows']: print('   ', r)
json.dump(dict(res=out, CL=CL, BRENT=BRENT, spread=spread), open('data/nav_scen.json', 'w'), ensure_ascii=False)
