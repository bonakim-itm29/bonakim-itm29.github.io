import json, html, os, math, re as _re
from content_hk3 import C
D = json.load(open('data/page_data.json'))
T = open('template_hk3.html', encoding='utf-8').read()
OUT = '/home/claude/bonakim-itm29.github.io/macro-notes/companies/'
VNOTE = {
 '0992.HK': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 레노버는 3월 결산이라 "2026년 4~6월 분기"가 FY2026/27 1분기입니다. 직전 분기(1~3월) 영업현금흐름·설비투자는 연간 발표문에 3개월 값이 없어 FCF는 FY2025/26 연간 값을 썼습니다. ② EV 배수의 이익은 회사 제시 Non-HKFRS 영업이익(US$15.23억)을 썼고, 직전 분기 값이 없어 최근 분기 × 4만 썼습니다. ⑤ 시가총액은 9월 전환 후 주식 수를 쓰므로, 차입에서도 9월에 전환된 2029년 만기 전환사채(US$4.02억)를 뺐습니다. ③ 미행사 워런트(12.3억 주)와 전환사채(21.1억 주 상당)는 주식 수에 넣지 않았습니다. 모두 전환되면 주당 가치가 약 21% 줄어듭니다(계산). ④ FY2023/24 Non-HKFRS 순이익은 FY2024/25 발표문의 재작성값(US$10.60억)입니다.</div>',
 '1810.HK': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① 회사 제시 현금 자원(¥2,193억)은 회사가 밝힌 정의 항목을 재무상태표에서 더한 값(약 ¥2,275억)과 약 ¥82억 차이가 나며 원인을 확인하지 못했습니다. 순현금은 작은 쪽(회사 제시값)으로 계산했습니다. ② EV·AI 신사업 영업손실과 총차입은 본문의 억 위안 반올림 값입니다. ③ 상반기 자사주 매입은 월별 행을 더한 값입니다. 1분기 조정 순이익은 2분기 발표문의 비교값(¥60.7억)을 썼습니다(1분기 발표 당시 ¥63.5억). ④ 2021~2023년 영업현금흐름·설비투자는 5개년 요약표에 없어 장기 차트에서 뺐습니다.</div>',
 '1211.HK': '<div class="callout warn"><b>⚠ 확인이 필요한 데이터.</b> ① BYD는 중국 기업회계기준(ASBE)으로 보고하며, 2분기 단독 실적을 공시하지 않아 2분기 값은 반기 − 1분기로 계산했습니다. ② 총차입은 경영진 논의의 회사 제시값(¥1,200.6억)을 썼습니다. 재무상태표 차입 항목 합계보다 ¥62억 많습니다(1년 내 만기 비유동부채 중 차입분이 따로 공시되지 않음). ③ 조정(비경상 차감) 순이익은 반기 금액이 공시되지 않았습니다. ④ 2021~2023년 영업현금흐름·설비투자는 연차보고서에 없어 장기 차트는 2024~2025년만 있습니다. ⑤ 시가총액은 H주 가격 × (A주 + H주) 주식 수로 계산했습니다. A주는 다른 가격에 거래됩니다.</div>'}
START_NOTE = {'0992.HK': '레노버는 1994년 홍콩 상장이지만 Yahoo 수정주가가 2000년 3월부터 있어 그때부터 분석했습니다.', '1810.HK': '2018년 7월 홍콩 상장.', '1211.HK': '2002년 7월 홍콩 상장(H주). 분할·무상증자를 반영한 수정주가.'}
DEEP = {'0992.HK': '기준: FY2026/27 1분기(2026년 4~6월) 실적발표(HKEX), 연간은 FY2025/26 실적발표, 주가는 10/6 종가(홍콩달러). 금액은 US$.',
        '1810.HK': '기준: 2026년 2분기 실적발표(HKEX), 연간은 2025년 연차보고서, 주가는 10/6 종가(홍콩달러). 금액은 위안(¥).',
        '1211.HK': '기준: 2026년 중간 실적(HKEX)과 1분기 보고서, 연간은 2025년 연차보고서, 9월 판매 발표, 주가는 10/6 종가(H주, 홍콩달러). 금액은 위안(¥).'}
FUNDNOTE = {'0992.HK': 'FY2022~FY2026(3월 결산) 연간 실적발표 값입니다. 단위 US$. FY2026 = 2025년 4월~2026년 3월.',
            '1810.HK': '2025년 연차보고서의 5개년 재무 요약표(2021~2025) 값입니다. 단위 위안(¥).',
            '1211.HK': '2025년 연차보고서의 5개년 요약(2021~2025) 값입니다. 단위 위안(¥). 영업현금흐름은 2024~2025년만 있습니다.'}
FINSRC = {'0992.HK': '재무: HKEX 원본 PDF(FY2026/27 1분기 실적발표, FY2023~FY2026 연간 실적발표, 9월 월간 주식변동 보고). 페이지별로 표 구조와 열(기간)을 유지해 읽었고, 서로 다른 두 에이전트가 따로 추출해 대조했습니다. 금액은 US$ 기준이며 홍콩달러 환산은 2026-10-06 USD/HKD 7.85를 썼습니다.',
          '1810.HK': '재무: HKEX 원본 PDF(2026년 1·2분기 실적발표, 2025년 연간 실적발표·연차보고서, 8월 월간 주식변동 보고). 페이지별로 표 구조와 열(기간)을 유지해 읽었고, 서로 다른 두 에이전트가 따로 추출해 대조했습니다. 금액은 위안(¥) 기준이며 홍콩달러 환산은 2026-10-06 USD/CNY 6.69, USD/HKD 7.85(1 HK$ = ¥0.853)를 썼습니다.',
          '1211.HK': '재무: HKEX 원본 PDF(2026년 중간 실적, 1분기 보고서, 2025년 연차보고서, 9월 월간 주식변동 보고·판매 발표). 페이지별로 표 구조와 열(기간)을 유지해 읽었고, 서로 다른 두 에이전트가 따로 추출해 대조했습니다. 금액은 위안(¥) 기준이며 홍콩달러 환산은 2026-10-06 USD/CNY 6.69, USD/HKD 7.85(1 HK$ = ¥0.853)를 썼습니다.'}
COMMON = '''<div class="panel"><h3><span class="pill p-neu">업종 공통</span>중국 공통 충격으로 분류된 날</h3><p class="small">항셍지수나 미국 상장 중국 인터넷 ETF(KWEB)가 같은 날 같은 방향으로 크게 움직인 날은 회사 고유 사건이 아니라 "중국 공통 충격"으로 따로 분류했습니다. 대표적으로 2022년 3월 16일(국무원 금융안정발전위원회의 플랫폼 정비 조기 마무리·자본시장 지원 발표)과 2022년 10월 24일(당대회 직후 첫 거래일)이 있습니다.</p></div>'''
for t, c in C.items():
    d = D['data'][t]
    for e in d['moves']['events']:
        if e.get('cn') is not None: e['cn'] = round(math.expm1(e['cn']), 4)
    d['extraEvent'] = COMMON
    ev = d['events']
    ev['unread'] = [o for o in ev['others'] if '미확보' in o['title_ko']]
    ev['others'] = [o for o in ev['others'] if '미확보' not in o['title_ko']]
    def _clean(s):
        s = _re.sub(r'(?:매크로 (?:모델 )?예측 )?fit ([+\-−]?\d)', r'매크로 예측 \1', s)
        s = _re.sub(r'(?:잔차 )?res ([+\-−]?\d)', r'잔차 \1', s)
        s = _re.sub(r'(?:수익률 |주가 )?\bR ([+\-−]?\d)', r'수익률 \1', s)
        return s
    for e in ev['top']:
        for k, v in list(e.items()):
            if isinstance(v, str): e[k] = _clean(v)
    els = ''.join(f'<details class="acc"><summary><span class="n">{i+1}</span><b>{html.escape(h)}</b><span class="chev"></span><span class="hl">{html.escape(c["heads"][i])}</span></summary><ul class="tight">' + ''.join(f'<li>{html.escape(b)}</li>' for b in bl) + '</ul></details>' for i, (h, bl) in enumerate(c['elements']))
    mon = ''.join(f'<div><b>{html.escape(a)}</b>{html.escape(b)}</div>' for a, b in c['monitor'])
    fr = c['frame']
    s = (T.replace('__NAME__', c['name']).replace('__T__', t).replace('__EXCH__', c['exch']).replace('__LEAD__', html.escape(c['lead']))
          .replace('__THESIS__', ''.join(f'<li>{html.escape(x)}</li>' for x in c['thesis'])).replace('__ELEMENTS__', els)
          .replace('__MACROREAD__', html.escape(c['macro_read'])).replace('__MONITOR__', mon).replace('__VNOTE__', VNOTE[t])
          .replace('__FRAMEREAD__', html.escape(fr['read'])).replace('__UP__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['up'])).replace('__DOWN__', ''.join(f'<li>{html.escape(x)}</li>' for x in fr['down']))
          .replace('__START__', d['stats']['start']).replace('__STARTNOTE__', START_NOTE[t]).replace('__DEEPBASIS__', DEEP[t]).replace('__FUNDNOTE__', FUNDNOTE[t])
          .replace('__LEG3__', d['fundlab'][0]).replace('__LEG2__', d['fundlab'][1]).replace('__FINSRC__', FINSRC[t])
          .replace('__LABELS__', json.dumps(D['labels'], ensure_ascii=False))
          .replace('__DATA__', json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')))
    os.makedirs(OUT + c['slug'], exist_ok=True)
    open(OUT + c['slug'] + '/index.html', 'w', encoding='utf-8').write(s)
    left = sorted(set(_re.findall(r'__[A-Z0-9]+__', s.split('<script>')[0])))
    print(t, c['slug'], len(s), left)
