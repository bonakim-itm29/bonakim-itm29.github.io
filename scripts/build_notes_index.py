"""매크로 투자노트 첫 화면의 '관심 종목'을 섹터별로 묶고 종합 매력도 색을 붙인다.
점수는 각 기업 페이지에 들어 있는 값을 그대로 읽는다(8점 이상 녹색, 6점 이상 노랑, 6점 미만 빨강)."""
import re, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parents[1] / "macro-notes"
SECTORS = [
  ("에너지 E&amp;P", "유가 민감 생산기업", [
    ("crescent-energy", "Crescent Energy", "티커 CRGY · 유가 베타·인수 할인"),
    ("kosmos-energy", "Kosmos Energy", "티커 KOS · Brent·신용 민감도"),
    ("sm-energy", "SM Energy", "티커 SM · 33년 유가 사이클·Civitas 합병")]),
  ("중국 이커머스·소비 플랫폼", "내수 소비와 직접 연결된 플랫폼", [
    ("alibaba", "Alibaba", "NYSE BABA · 위안화·항셍 민감도·AI 투자와 FCF"),
    ("jd", "JD.com", "NASDAQ JD · PER 7배·주주환원"),
    ("pdd", "PDD Holdings", "NASDAQ PDD · 핀둬둬·테무, 순현금이 시총의 절반 이상"),
    ("meituan", "Meituan", "HKEX 3690 · 배달 가격 전쟁 이후 회복"),
    ("trip-com", "Trip.com", "NASDAQ TCOM · 중국·해외 여행 소비")]),
  ("중국 검색·게임·소셜", "광고·게임·콘텐츠 중심 인터넷", [
    ("tencent", "Tencent", "HKEX 0700 · 게임·광고·AI 설비투자와 주주환원"),
    ("baidu", "Baidu", "NASDAQ BIDU · 순현금이 시총의 90%"),
    ("netease", "NetEase", "NASDAQ NTES · 게임·순현금·배당")]),
  ("중국 하드웨어·전기차", "AI 서버·스마트폰·전기차 제조", [
    ("lenovo", "Lenovo Group", "HKEX 0992 · AI 서버 매출 2배·워런트 희석"),
    ("xiaomi", "Xiaomi", "HKEX 1810 · 순현금 시총의 34%·EV 손실 축소"),
    ("byd", "BYD Company", "HKEX 1211 · 판매 반등·공급망 신용")]),
  ("브라질 원자재·산업·소비", "EWZ 편입 · 미국 상장 ADR(AXIA는 B3)", [
    ("vale", "Vale", "NYSE VALE · 철광석·구리, EV/EBITDA 4.9배"),
    ("petrobras", "Petrobras", "NYSE PBR · 석유, FCF 수익률 15%"),
    ("axia", "AXIA Energia", "B3 AXIA3 · 옛 Eletrobras, NYSE 상장폐지"),
    ("sabesp", "Sabesp", "NYSE SBS · 민영화 후 투자 확대"),
    ("ambev", "Ambev", "NYSE ABEV · 맥주, 순현금"),
    ("embraer", "Embraer", "NYSE EMBJ · 항공기, 수주잔고 US$345억")]),
  ("브라질 금융", "은행·핀테크 · P/B·ROE 기준", [
    ("itau", "Itaú Unibanco", "NYSE ITUB · ROE 24%, P/B 2.5배"),
    ("bradesco", "Banco Bradesco", "NYSE BBD · P/B 1.3배·ROE 회복"),
    ("nu", "Nu Holdings", "NYSE NU · 고객 1.39억 명, ROE 33%")]),
  ("한국 반도체", "메모리 사이클", [
    ("samsung-electronics", "Samsung Electronics", "KOSPI 005930 · AI 메모리 호황과 사이클 정점 논쟁"),
    ("sk-hynix", "SK hynix", "KOSPI 000660 · HBM 이익률 76%·원화 민감도")]),
]

def score(slug):
    p = ROOT / "companies" / slug / "index.html"
    if not p.exists():
        return None
    m = re.search(r'"score":\{"total":([0-9.]+)', p.read_text())
    return float(m.group(1)) if m else None

def tier(v):
    return ("g", "녹색") if v >= 8 else ("y", "노랑") if v >= 6 else ("r", "빨강")

out = ['<section id="companies">', '  <h2>관심 종목</h2>',
       '  <p class="sc-legend"><span class="scb g">8+</span> 녹색 · <span class="scb y">6+</span> 노랑 · <span class="scb r">6 미만</span> 빨강 — 같은 섹터 안에서 비교한 학습용 종합 매력도(10점 만점)이며 매수·매도 권유가 아닙니다.</p>']
for name, sub, items in SECTORS:
    rows = [(s, n, d, score(s)) for s, n, d in items]
    rows = [r for r in rows if r[3] is not None]
    if not rows:
        continue
    rows.sort(key=lambda r: -r[3])
    out.append(f'  <h3 class="sector">{name} <span>{sub}</span></h3>')
    out.append('  <div class="grid2">')
    for s, n, d, v in rows:
        t, lab = tier(v)
        out.append(f'    <a class="card" href="companies/{s}/index.html">\n      <h3>{html.escape(n)} <span class="scb {t}" title="종합 매력도 {v:.1f} ({lab})">{v:.1f}</span></h3>\n      <p>{d}</p>\n      <div class="meta"><span class="tag live">심층 분석</span><span class="tag">{name}</span></div>\n    </a>')
    out.append('  </div>')
ETFS = [("ewz", "EWZ · 브라질", "iShares MSCI Brazil · 원자재·금융, 헤알화 연동", "강세"),
        ("kweb", "KWEB · 중국 인터넷", "KraneShares CSI China Internet · 저자가 가장 자주 쓰는 중국 ETF", "강세(가장 선호)"),
        ("ktec", "KTEC · 항셍테크", "KraneShares Hang Seng TECH · 실질금리 민감도 가장 큼", "강세"),
        ("fxi", "FXI · 중국 대형주", "iShares China Large-Cap · 국유 은행 비중 큼", "강세"),
        ("kba", "KBA · 중국 본토 A주", "KraneShares MSCI China A 50 · 상해 증시 대용", "장기 강세")]
out.append('  <h3 class="sector">칼럼에 나온 ETF <span>브라질·중국 · 점수 대신 저자 입장 표시</span></h3>')
out.append('  <div class="grid2">')
for s, n, d, st in ETFS:
    if (ROOT / "etfs" / s / "index.html").exists():
        out.append(f'    <a class="card" href="etfs/{s}/index.html">\n      <h3>{html.escape(n)} <span class="scb n" title="저자 입장">{st}</span></h3>\n      <p>{d}</p>\n      <div class="meta"><span class="tag live">ETF</span><span class="tag">칼럼 언급</span></div>\n    </a>')
out.append('  </div>')
out.append('</section>')
STYLE = '''<style id="sc-style">
.scb{display:inline-block;min-width:2.6em;text-align:center;font-size:13px;font-weight:700;padding:2px 8px;border-radius:999px;margin-left:6px;vertical-align:2px;color:#fff}
.scb.g{background:#2e7d4f}.scb.y{background:#b8860b}.scb.r{background:#c0392b}.scb.n{background:#5b6b7a;min-width:0}
@media (prefers-color-scheme: dark){.scb.g{background:#3f9e66}.scb.y{background:#c99a1e}.scb.r{background:#d0574a}}
.sc-legend{font-size:13px;color:var(--muted)}
.sc-legend .scb{margin:0 2px 0 0;min-width:0}
h3.sector{font-size:16px;margin:26px 0 8px}
h3.sector span{font-size:13px;color:var(--muted);font-weight:500;margin-left:6px}
</style>'''
idx = ROOT / "index.html"
t = idx.read_text()
t = re.sub(r'<section id="companies">.*?</section>', "\n".join(out), t, count=1, flags=re.S)
if 'id="sc-style"' in t:
    t = re.sub(r'<style id="sc-style">.*?</style>', STYLE, t, flags=re.S)
else:
    t = t.replace("</head>", STYLE + "\n</head>", 1)
idx.write_text(t)
print("ok")
