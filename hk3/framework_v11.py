"""중국·홍콩 기업 프레임워크 적합도 v1.1: 2026년 10월 칼럼 판단 반영.
위안화 베타 1.0점 → 0.5점, 미국 실질금리 하락 수혜(실질금리 베타) 0.5점 신설. 공개 페이지에는 칼럼 제목·인용을 넣지 않는다."""
import json, re, sys, pathlib
sys.path.insert(0, '.')
from rr_beta import run
clip = lambda x: max(0.0, min(1.0, x))
RR = run('2021-01-01', 4)
json.dump(RR, open('data/rr_beta.json', 'w'), ensure_ascii=False, indent=1)
CNY_K = '달러 약세·위안화 강세 수혜(위안화 베타)'
RR_K = '미국 실질금리 하락 수혜(실질금리 베타)'
RR_RULE = ('2026년 10월 칼럼 판단: 미국 장기 실질금리 하락이 중국 플랫폼·테크 턴어라운드의 가장 중요한 대외 요인. '
           '2021년 이후 월간 수익률을 미 10년 실질금리(TIPS) 변화에 회귀한 베타가 −0.20 이하면 만점, 0 이상이면 0점')
CNY_RULE = '저자는 달러 약세를 전망. 위안화 1% 강세 시 주가 반응이 클수록 높음(−3 이하 만점)'

def items(bc, slug):
    b = RR[slug]['beta_simple']
    return [dict(k=CNY_K, val=f'{bc:.2f}', pts=round(0.5 * clip(-bc / 3), 2), max=0.5, rule=CNY_RULE),
            dict(k=RR_K, val=f'{b:+.2f} (실질금리 1%p 상승 시 월간 {b*100:+.0f}%)', pts=round(0.5 * clip(-b / 0.20), 2), max=0.5, rule=RR_RULE)]

def patch_score(score, slug):
    fw = score['pillars'][0]
    old = [i for i in fw['items'] if i['k'] == CNY_K]
    if not old:
        return False
    bc = float(old[0]['val'])
    fw['items'] = [i for i in fw['items'] if i['k'] not in (CNY_K, RR_K)] + items(bc, slug)
    fw['score'] = round(sum(i['pts'] for i in fw['items']), 2)
    score['total'] = round(sum(p['score'] for p in score['pillars']), 1)
    return True
