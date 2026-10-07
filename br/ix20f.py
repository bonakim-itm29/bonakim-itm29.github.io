"""20-F 인라인 XBRL(원본 HTML)에서 차원 없는 연간 값을 읽는다."""
import re, json, sys
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings; warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)
def parse(t):
    s = BeautifulSoup(open(f'raw20f/{t}_20F_2025.htm', encoding='utf-8', errors='ignore').read(), 'lxml')
    ctx = {}
    for c in s.find_all(re.compile('xbrli:context$')):
        if c.find(re.compile('xbrldi:explicitmember$')) or c.find(re.compile('xbrldi:typedmember$')): continue
        st, en = c.find(re.compile('xbrli:startdate$')), c.find(re.compile('xbrli:enddate$'))
        if st and en: ctx[c['id']] = (st.text.strip(), en.text.strip())
    out = {}
    for f in s.find_all(re.compile('ix:nonfraction$')):
        cid = f.get('contextref'); 
        if cid not in ctx: continue
        name = f['name'].split(':')[-1]; txt = f.text.strip().replace(',', '')
        if not txt or txt == '-': v = 0.0
        else:
            try: v = float(txt)
            except: continue
        v *= 10 ** int(f.get('scale', '0'))
        if f.get('sign') == '-': v = -v
        st, en = ctx[cid]
        if not (st[5:] == '01-01' and en[5:] == '12-31' and st[:4] == en[:4]): continue
        out.setdefault(name, {})[int(en[:4])] = round(v / 1e6, 1)
    return out
if __name__ == '__main__':
    R = {}
    for t in ['VALE','PBR','ITUB','NU','BBD','ABEV','SBS','ERJ','AXIA']:
        o = parse(t); R[t] = o
        print(t, {k: o.get(k) for k in ['Revenue', 'ProfitLossAttributableToOwnersOfParent', 'CashFlowsFromUsedInOperatingActivities']})
    json.dump(R, open('data/ix20f.json', 'w'))
