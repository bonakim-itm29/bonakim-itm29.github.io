import json, re, sys
sys.path.insert(0, '.')
from framework_v11 import patch_score
ROOT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
CN = {'alibaba': 'BABA', 'baidu': 'BIDU', 'jd': 'JD', 'pdd': 'PDD', 'netease': 'NTES', 'trip-com': 'TCOM', 'tencent': '0700.HK', 'meituan': '3690.HK'}
DEC = json.JSONDecoder()
def sub_obj(h, key, fn):
    out, pos, n = [], 0, 0
    for m in re.finditer(r'"%s":\{' % key, h):
        if m.start() < pos: continue
        obj, end = DEC.raw_decode(h, m.end() - 1)
        new = fn(obj)
        out.append(h[pos:m.end() - 1]); out.append(json.dumps(new, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')); pos = end; n += 1
    out.append(h[pos:]); return ''.join(out), n
def run_scores():
    tot = {}
    for slug, t in CN.items():
        p = ROOT + slug + '/index.html'; h = open(p).read()
        def f(s, slug=slug):
            if 'pillars' in s: patch_score(s, slug); tot[t] = s['total']
            return s
        h, n = sub_obj(h, 'score', f)
        h = h.replace('위안화 강세 수혜(0~1점)로 구성됩니다', '위안화 강세 수혜(0~0.5점), 미국 실질금리 하락 수혜(0~0.5점, 2026년 10월 추가)로 구성됩니다')
        open(p, 'w').write(h); print(slug, n, tot.get(t))
    return tot
def run_peers(tot):
    for slug in CN:
        p = ROOT + slug + '/index.html'; h = open(p).read()
        h, n = sub_obj(h, 'peers', lambda o: {k: tot.get(k, v) for k, v in {**o, **tot}.items()})
        open(p, 'w').write(h)
if __name__ == '__main__':
    tot = run_scores(); json.dump(tot, open('data/cn_totals_v11.json', 'w')); run_peers(tot); print(tot)
