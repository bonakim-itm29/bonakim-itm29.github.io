import json, html, re
A = json.load(open('data/hk3_ann.json'))
MAP = {'LENOVO': '0992.HK', 'XIAOMI': '1810.HK', 'BYD': '1211.HK'}
SKIP = ('Next Day Disclosure Returns', 'Monthly Returns', 'Share Buyback Reports', 'Proxy Forms', 'Constitutional Documents')
SKIP_SUB = ('Date of Board Meeting', 'Change in Directors', 'Change of Company Secretary', 'Closure of Books', 'Results of AGM', 'Results of EGM',
            'Notice of AGM', 'Notice of EGM', 'Change in Auditors', 'Change in Principal Share Registrar', 'List of Directors')
out = {}
for k, rows in A.items():
    R = []
    for r in rows:
        d = r['d']; filed = f'{d[6:10]}-{d[3:5]}-{d[0:2]}'
        cat = html.unescape(r['l'] or ''); title = html.unescape(r['t'] or '').replace('\n', ' ')
        key = not cat.startswith(SKIP) and not any(s in cat for s in SKIP_SUB)
        R.append(dict(filed=filed, time=d[11:], title=title, cat=cat, link=r['f'], key=key))
    out[MAP[k]] = dict(rows=R)
    print(k, len(R), sum(r['key'] for r in R))
json.dump(out, open('data/hk_hist.json', 'w'), ensure_ascii=False)
