# 규칙 기반 매력도 점수(10점 만점). 입력은 검증된 값만 사용하며, 규칙은 관심 종목에 동일하게 적용한다.
import json
clip = lambda x, a=0.0, b=1.0: max(a, min(b, x))
D = json.load(open('data/page_data.json'))
# 2026 하반기 원유 헤지 비율(검증 표·10-Q 기준). CRGY는 기간 모호 → 중립값 적용
HEDGE = {'CRGY': None, 'KOS': 0.352, 'REI': 0.739, 'SM': 0.544}
VALX = {'REI': dict(ev_ebitdax_q2ann=715.9 / (54.482 * 4), fcf_yield_h1ann=(0.237 + 4.375) * 2 / 354.33, nd_ebitdax_h1ann=361.58 / ((38.31 + 54.482) * 2), nav_stdm_ps=2.92),
        'SM': dict(nav_stdm_ps=28.01)}
PRICE = {'CRGY': 13.15, 'KOS': 2.65, 'REI': 1.36, 'SM': 33.91}
out = {}
for t, d in D['data'].items():
    v = dict(d['val']); v.update(VALX.get(t, {}))
    e = d['eda']; m = d['moves']
    # A. 프레임워크 적합도 (3)
    # 프레임워크: 원유 강세(확신 최상). 투자 순서 원유 직접 → 생산기업 → 오일서비스, E&P 로테이션은 WTI $150~200 (26.06.04)
    wti = 96.41; stage = 0.5 if wti >= 150 else 0.25
    h = HEDGE[t]; part = 0.5 if h is None else clip(1 - h)
    A = [dict(k='원유 강세 신호', val='강세 · 확신 최상', pts=1.5, max=1.5, rule='프레임워크의 원유 입장(관심 종목 공통)'),
         dict(k='투자 순서상 E&P 단계', val='WTI $96: 원유 직접 우선', pts=stage, max=0.5, rule='WTI $150~200이면 E&P 로테이션 구간 0.5, 그 전에는 0.25(빠르면 올여름부터 이동 가능하다는 언급 반영)'),
         dict(k='유가 상승 참여도(하반기 미헤지 비중)', val=('확인 필요(중립 0.5)' if h is None else f'{(1-h)*100:.0f}%'), pts=round(part, 2), max=1.0, warn=h is None, rule='하반기 원유 중 헤지하지 않은 비중(0~1)')]
    # B. 가치평가 (4)
    ev = v['ev_ebitdax_q2ann']; fy = v['fcf_yield_h1ann']; nd = v['nd_ebitdax_h1ann']; nav = v.get('nav_stdm_ps')
    pnav = PRICE[t] / nav if nav and nav > 0 else None
    B = [dict(k='EV/EBITDAX', val=f'{ev:.1f}배', pts=round(clip((5 - ev) / 2.5), 2), max=1.0, rule='2.5배 이하 만점, 5배 이상 0점'),
         dict(k='FCF 수익률', val=f'{fy*100:.1f}%', pts=round(clip(fy / 0.20), 2), max=1.0, rule='20% 이상 만점, 0% 이하 0점'),
         dict(k='주가/세후 NAV', val=('NAV 마이너스' if pnav is None else f'{pnav:.2f}배'), pts=round(0 if pnav is None else clip((1.5 - pnav) / 1.0), 2), max=1.0, rule='0.5배 이하 만점, 1.5배 이상 0점'),
         dict(k='순부채/EBITDAX', val=f'{nd:.1f}배', pts=round(clip((3 - nd) / 2), 2), max=1.0, rule='1배 이하 만점, 3배 이상 0점')]
    # C. 역사적 매크로 반응 (3)
    bo = e['full']['beta_oil']; bs = e['full']['beta_spx']; r2 = e['full']['r2']; rv = m['resid_var_share']
    C = [dict(k='원유 민감도(주간 베타)', val=f'{bo:.2f}', pts=round(clip(bo / 0.8), 2), max=1.0, rule='0.8 이상 만점 — 프레임워크가 원유 강세를 보는 만큼 유리'),
         dict(k='주식시장 조정 내성(S&P 베타)', val=f'{bs:.2f}', pts=round(clip(1 - (bs - 0.8) / 0.8), 2), max=1.0, rule='0.8 이하 만점, 1.6 이상 0점 — 10년물 5%대의 자산 조정 위험 반영'),
         dict(k='매크로 연결성(R²·비매크로 변동)', val=f'R² {r2:.2f} · 비매크로 {rv*100:.0f}%', pts=round(0.5 * clip(r2 / 0.45) + 0.5 * clip((0.9 - rv) / 0.3), 2), max=1.0, rule='매크로 판단이 주가로 잘 전달되고 회사 고유 급변동이 적을수록 높음')]
    sA, sB, sC = (round(sum(x['pts'] for x in L), 2) for L in (A, B, C))
    out[t] = dict(total=round(sA + sB + sC, 1), pillars=[dict(name='프레임워크 적합도', max=3, score=sA, items=A), dict(name='가치평가', max=4, score=sB, items=B), dict(name='역사적 매크로 반응', max=3, score=sC, items=C)])
    print(t, out[t]['total'], sA, sB, sC)
json.dump(out, open('data/scores.json', 'w'), ensure_ascii=False)
