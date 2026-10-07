import json, datetime as dt
def annual(t, tag, years=range(2021, 2026)):
    f = json.load(open(f'data/facts_{t}.json'))['facts'].get('ifrs-full', {})
    if tag not in f: return {}
    out = {}
    for u, L in f[tag]['units'].items():
        if '/' in u: continue
        for x in L:
            if x.get('form') not in ('20-F', '20-F/A') or 'start' not in x: continue
            s, e = dt.date.fromisoformat(x['start']), dt.date.fromisoformat(x['end'])
            if not (350 <= (e - s).days <= 380) or e.month != 12 or e.year not in years: continue
            k = e.year
            if k not in out or x['filed'] > out[k][1]: out[k] = (x['val'] / 1e6, x['filed'], u)
    return {k: round(v[0], 1) for k, v in sorted(out.items())}
if __name__ == '__main__':
    for t in ['VALE','PBR','ITUB','NU','BBD','ABEV','SBS','ERJ','AXIA']:
        print(t)
        for tag in ['Revenue', 'ProfitLossAttributableToOwnersOfParent', 'CashFlowsFromUsedInOperatingActivities', 'InterestRevenueExpense', 'RevenueFromInterest', 'FeeAndCommissionIncome', 'DividendsPaidClassifiedAsFinancingActivities']:
            a = annual(t, tag)
            if a: print('  ', tag[:40], a)
