"""브라질 ADR 프레임워크 적합도: 신흥국 강세 1.5 + 거명 0.25~0.5 + 헤알 강세 수혜 0.5 + 미국 실질금리 하락 수혜 0.5.
공개 페이지에는 칼럼 제목·인용·번호를 넣지 않는다."""
import json, numpy as np, pandas as pd
clip = lambda x: max(0.0, min(1.0, x))
y = pd.read_pickle('data/prices.pkl'); fr = pd.read_pickle('data/fred.pkl')
SLUG = {'VALE': 'vale', 'PBR': 'petrobras', 'ITUB': 'itau', 'NU': 'nu', 'BBD': 'bradesco', 'ABEV': 'ambev', 'SBS': 'sabesp', 'EMBJ': 'embraer', 'AXIA3.SA': 'axia'}
def rr_run(start='2021-01-01', h=4):
    P = {t: y[t] for t in SLUG}; P['AXIA3.SA'] = y['AXIA3.SA'] / y['BRL=X'].ffill(limit=3)  # 달러 환산
    P['EWZ'] = y['EWZ']; P['^GSPC'] = y['^GSPC']
    D = pd.DataFrame(P); D['RR'] = fr['DFII10']
    W = D.ffill(limit=3).resample('W-FRI').last(); W = W[(W.index <= '2026-10-02') & (W.index >= start)]
    out = {}
    for t in list(SLUG) + ['EWZ']:
        r = np.log(W[t]).diff(h); x = W.RR.diff(h); m = np.log(W['^GSPC']).diff(h)
        d = pd.concat([r.rename('R'), x.rename('RR'), m.rename('SPX')], axis=1).iloc[::h].dropna()
        b = np.linalg.lstsq(np.column_stack([np.ones(len(d)), d.RR, d.SPX]), d.R, rcond=None)[0]
        out[SLUG.get(t, t)] = dict(beta=float(b[1]), beta_simple=float(np.polyfit(d.RR, d.R, 1)[0]), corr=float(d.R.corr(d.RR)), n=len(d), start=str(d.index[0].date()))
    return out
RR = rr_run()
json.dump(RR, open('data/rr_beta.json', 'w'), ensure_ascii=False, indent=1)
BRL_K = '헤알 강세 수혜(헤알 베타)'
RR_K = '미국 실질금리 하락 수혜(실질금리 베타)'
RR_RULE = ('저자는 미국 장기 실질금리 하락 시 중국과 함께 브라질을 가장 큰 수혜국으로 봄. 2021년 이후 월간(4주) 달러 수익률을 '
           '미 10년 실질금리(TIPS) 변화에 회귀한 베타가 −0.20 이하면 만점, 0 이상이면 0점')
BRL_RULE = '저자는 달러 약세를 전망. 헤알 1% 약세(USD/BRL 상승) 때 주가 반응(S&P 500 통제, 주간)이 −1.5% 이하면 만점, 0 이상이면 0점'
def items(bc, slug):
    b = RR[slug]['beta_simple']
    return [dict(k=BRL_K, val=f'{bc:.2f}', pts=round(0.5 * clip(-bc / 1.5), 2), max=0.5, rule=BRL_RULE),
            dict(k=RR_K, val=f'{b:+.2f} (실질금리 1%p 상승 시 월간 {b*100:+.0f}%)', pts=round(0.5 * clip(-b / 0.20), 2), max=0.5, rule=RR_RULE)]
if __name__ == '__main__':
    for k, v in RR.items(): print(f"{k:10s} simple {v['beta_simple']:+.3f} |spx {v['beta']:+.3f} corr {v['corr']:+.2f} n {v['n']}")
