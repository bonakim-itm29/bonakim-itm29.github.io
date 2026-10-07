import json, html, os, math, re as _re, sys, importlib
D = json.load(open('data/page_data.json'))
T = open('template_br.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
C = {}
for m in ['content_br_a', 'content_br_b', 'content_br_c', 'content_br_d']:
    if os.path.exists(m + '.py'): C.update(importlib.import_module(m).C)
ONLY = sys.argv[1:] or list(C)
COMMON = '''<div class="panel"><h3><span class="pill p-neu">시장 공통</span>브라질 공통 충격으로 분류된 날</h3><p class="small">브라질 ETF(EWZ)나 신흥국 ETF(EEM)가 같은 날 같은 방향으로 크게 움직인 날은 회사 고유 사건이 아니라 "브라질 공통 충격"으로 따로 분류했습니다. 2008년 금융위기, 2016년 탄핵 정국, 2018·2022년 대선 전후처럼 정치·재정 사건이 많습니다.</p></div>'''
for t in ONLY:
    c = C[t]; d = D['data'][t]
    for e in d['moves']['events']:
        if e.get('cn') is not None: e['cn'] = round(math.expm1(e['cn']), 4)
    d['extraEvent'] = COMMON
    if not d['events'].get('top') and d['events'].get('top_note_ko'):
        d['extraEvent'] = '<div class="panel"><h3><span class="pill p-neu">확인 결과</span>회사 고유 핵심 이벤트 없음</h3><p class="small">' + html.escape(d['events']['top_note_ko']) + '</p></div>' + COMMON
    ev = d['events']
    ev.setdefault('top', []); ev.setdefault('others', []); ev.setdefault('no_filing_moves', [])
    ev['unread'] = [o for o in ev['others'] if '미확보' in (o.get('title_ko') or '')]
    ev['others'] = [o for o in ev['others'] if '미확보' not in (o.get('title_ko') or '')]
    for o in ev['others']:
        for k in ('R', 'res'):
            if not isinstance(o.get(k), (int, float)): o[k] = None
    for o in ev['unread'] + ev['no_filing_moves']:
        if not isinstance(o.get('R'), (int, float)): o['R'] = 0
    def _clean(s):
        s = _re.sub(r'(?:매크로 (?:모델 )?예측 )?fit ([+\-−]?\d)', r'매크로 예측 \1', s)
        s = _re.sub(r'(?:잔차 )?res ([+\-−]?\d)', r'잔차 \1', s)
        s = _re.sub(r'(?:수익률 |주가 )?\bR ([+\-−]?\d)', r'수익률 \1', s)
        return s
    for e in ev['top']:
        for k, v in list(e.items()):
            if isinstance(v, str): e[k] = _clean(v)
        e.setdefault('facts', [])
    els = ''.join(f'<details class="acc"><summary><span class="n">{i+1}</span><b>{html.escape(h)}</b><span class="chev"></span><span class="hl">{html.escape(c["heads"][i])}</span></summary><ul class="tight">' + ''.join(f'<li>{html.escape(b)}</li>' for b in bl) + '</ul></details>' for i, (h, bl) in enumerate(c['elements']))
    mon = ''.join(f'<div><b>{html.escape(a)}</b>{html.escape(b)}</div>' for a, b in c['monitor'])
    fr = c['frame']
    s = (T.replace('__NAME__', c['name']).replace('__T__', c.get('tdisp', t)).replace('__EXCH__', c['exch']).replace('__LEAD__', html.escape(c['lead']))
          .replace('__THESIS__', ''.join(f'<li>{html.escape(x)}</li>' for x in c['thesis'])).replace('__ELEMENTS__', els)
          .replace('__MACROREAD__', html.escape(c['macro_read'])).replace('__MONITOR__', mon).replace('__VNOTE__', c['vnote'])
          .replace('__FRAMEREAD__', html.escape(fr['read'])).replace('__UP__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['up'])).replace('__DOWN__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['down']))
          .replace('__START__', d['stats']['start']).replace('__STARTNOTE__', c['start_note']).replace('__DEEPBASIS__', c['deep']).replace('__FUNDNOTE__', c['fundnote'])
          .replace('__LEG1__', d['fundlab'][0]).replace('__LEG3__', d['fundlab'][1]).replace('__LEG2__', d['fundlab'][2]).replace('__FINSRC__', c['finsrc'])
          .replace('__LABELS__', json.dumps(D['labels'], ensure_ascii=False))
          .replace('__DATA__', json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    left = sorted(set(_re.findall(r'__[A-Z0-9]+__', s.split('<script>')[0])))
    print(t, c['slug'], len(s), left)
