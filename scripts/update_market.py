"""매크로 투자노트 '시장 지표' 데이터를 매일 갱신한다 (GitHub Actions에서 실행).

출처
- 원유 선물: Yahoo Finance 차트 API (NYMEX WTI CL, NYMEX Brent Last Day Financial BZ)
- 10년물 금리 DGS10, 10년 BEI T10YIE, Kim-Wright 10년 텀프리미엄 THREEFYTP10: FRED
- ACM 10년 텀프리미엄 ACMTP10: 뉴욕 연은
한 출처가 실패해도 이전 값은 지우지 않고 남겨 두고, 실패 사실을 기록한다.
"""
import csv, io, json, datetime as dt, pathlib, sys, traceback
import urllib.request, urllib.parse

OUT = pathlib.Path(__file__).resolve().parents[1] / "macro-notes" / "market" / "data.json"
START = "2025-01-01"
UA = {"User-Agent": "Mozilla/5.0 (bonakim-itm29.github.io market updater)"}

FUT = [  # key, 표시명, 야후 심볼, 단위
    ("wti_front", "WTI 근월물", "CL=F", "$/bbl"),
    ("brent_front", "Brent 근월물", "BZ=F", "$/bbl"),
    ("silver_front", "은 근월물", "SI=F", "$/oz"),
    ("gold_front", "금 근월물", "GC=F", "$/oz"),
    ("spx", "S&P 500", "^GSPC", "pt"),
    ("ndx", "나스닥 종합", "^IXIC", "pt"),
    ("dji", "다우존스 산업평균", "^DJI", "pt"),
    ("move", "MOVE 지수 (미 국채 내재변동성)", "^MOVE", "pt"),
    ("copper_front", "구리 근월물", "HG=F", "$/lb"),
    ("dxy", "달러 인덱스", "DX-Y.NYB", "pt"),
    ("usdcny", "달러/위안", "CNY=X", "CNY"),
    ("usdjpy", "달러/엔", "JPY=X", "JPY"),
    ("usdkrw", "달러/원", "KRW=X", "KRW"),
    ("hsi", "항셍 지수", "^HSI", "pt"),
    ("hstech", "항셍테크 ETF (CSOP 3033)", "3033.HK", "HK$"),
    ("wti_dec27", "WTI 2027년 12월물", "CLZ27.NYM", "$/bbl"),
    ("wti_dec28", "WTI 2028년 12월물", "CLZ28.NYM", "$/bbl"),
    ("brent_dec27", "Brent 2027년 12월물", "BZZ27.NYM", "$/bbl"),
    ("brent_dec28", "Brent 2028년 12월물", "BZZ28.NYM", "$/bbl"),
]
FRED = [
    ("ust10", "미 국채 10년물 금리", "DGS10", "%"),
    ("bei10", "10년 기대인플레이션(BEI)", "T10YIE", "%"),
    ("tp10_kw", "10년 명목 텀프리미엄 (Kim-Wright)", "THREEFYTP10", "%p"),
    ("real10", "10년 실질금리 (TIPS)", "DFII10", "%"),
    ("wti_spot", "WTI 현물 (쿠싱)", "DCOILWTICO", "$/bbl"),
    ("brent_spot", "Brent 현물 (유럽)", "DCOILBRENTEU", "$/bbl"),
    ("t10y3m", "장단기 금리차 10년−3개월", "T10Y3M", "%p"),
    ("t10y2y", "장단기 금리차 10년−2년", "T10Y2Y", "%p"),
    ("fed_assets", "연준 총자산", "WALCL", "$M"),
    ("rrp", "역레포(RRP) 잔고", "RRPONTSYD", "$B"),
    ("tga", "재무부 일반계정(TGA)", "WTREGEN", "$M"),
    ("reserves", "은행 지급준비금", "WRESBAL", "$M"),
    ("m2", "M2 통화량", "M2SL", "$B"),
    ("m2v", "M2 유통속도", "M2V", "배"),
    ("debt_gdp", "연방정부 부채/GDP", "GFDEGDQ188S", "%"),
    ("interest", "연방정부 이자비용 (연율)", "A091RC1Q027SBEA", "$B"),
    ("cpi", "CPI", "CPIAUCSL", "지수"),
    ("core_cpi", "근원 CPI", "CPILFESL", "지수"),
    ("pce", "PCE 물가", "PCEPI", "지수"),
    ("core_pce", "근원 PCE 물가", "PCEPILFE", "지수"),
    ("export_px", "미국 수출물가", "IQ", "지수"),
    ("payrolls", "비농업 고용", "PAYEMS", "천명"),
    ("unrate", "실업률", "UNRATE", "%"),
    ("jolts", "JOLTS 구인", "JTSJOL", "천건"),
    ("claims", "신규 실업수당 청구", "ICSA", "건"),
]
LONG_FRED = {"DCOILWTICO", "DCOILBRENTEU", "M2SL", "M2V", "GFDEGDQ188S", "A091RC1Q027SBEA", "CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE", "IQ", "PAYEMS", "UNRATE", "JTSJOL"}
EIA = [  # EIA 주간 원유 재고 (천 배럴)
    ("crude_comm", "미국 상업 원유재고 (SPR 제외)", "WCESTUS1"),
    ("crude_spr", "전략비축유(SPR)", "WCSSTUS1"),
    ("crude_cushing", "쿠싱 원유재고", "W_EPC0_SAX_YCUOK_MBBL"),
]


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


COMP = [  # 관심기업 주가: slug(페이지 폴더), 야후 심볼, 통화
    ("crescent-energy", "CRGY", "USD"), ("kosmos-energy", "KOS", "USD"), ("sm-energy", "SM", "USD"),
    ("alibaba", "BABA", "USD"), ("baidu", "BIDU", "USD"), ("jd", "JD", "USD"),
    ("pdd", "PDD", "USD"), ("netease", "NTES", "USD"), ("trip-com", "TCOM", "USD"),
    ("tencent", "0700.HK", "HKD"), ("meituan", "3690.HK", "HKD"),
    ("lenovo", "0992.HK", "HKD"), ("xiaomi", "1810.HK", "HKD"), ("byd", "1211.HK", "HKD"),
    ("samsung-electronics", "005930.KS", "KRW"), ("sk-hynix", "000660.KS", "KRW"),
]
PRICES = OUT.parent.parent / "companies" / "prices.json"

LONG = {"CL=F", "SI=F", "GC=F"}  # 오일/실버 비율의 장기 비교용


def yahoo(sym, closed_only=False):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?{'period1=1262304000&period2=' + str(int(dt.datetime.utcnow().timestamp())) if sym in LONG else 'range=2y'}&interval=1d"
    j = json.loads(get(url))["chart"]["result"][0]
    ts = j["timestamp"]; close = j["indicators"]["quote"][0]["close"]
    pts = []
    for t, c in zip(ts, close):
        if c is None:
            continue
        d = dt.datetime.utcfromtimestamp(t).date().isoformat()
        if d >= ("2010-01-01" if sym in LONG else START):
            pts.append([d, round(float(c), 2)])
    # 마지막 일봉 종가가 아직 비어 있으면(야후 지연) 메타의 정규장 가격으로 보충
    meta = j.get("meta", {})
    mp, mt = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    reg_end = (meta.get("currentTradingPeriod") or {}).get("regular", {}).get("end", 0)
    closed = mt and reg_end and not ((meta.get('currentTradingPeriod') or {}).get('regular', {}).get('start', 0) <= mt < reg_end - 1800)  # 정규장 마감 이후 가격만(장중 가격은 쓰지 않음)
    if mp is not None and closed:
        md = dt.datetime.utcfromtimestamp(mt + int(meta.get("gmtoffset") or 0)).date().isoformat()
        if not pts or md > pts[-1][0]:
            pts.append([md, round(float(mp), 2)])
    reg_start = (meta.get("currentTradingPeriod") or {}).get("regular", {}).get("start", 0)
    if closed_only and mt and reg_end and reg_start <= mt < reg_end - 1800 and pts:
        # 장중이면 오늘의 미완성 일봉은 빼고 직전 종가까지만 쓴다
        today = dt.datetime.utcfromtimestamp(mt + int(meta.get("gmtoffset") or 0)).date().isoformat()
        if pts[-1][0] == today:
            pts.pop()
    # 같은 날짜 중복 시 마지막 값
    return [[d, v] for d, v in dict(pts).items()]


def fred(sid):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={'2015-01-01' if sid in LONG_FRED else START}"
    rows = list(csv.reader(io.StringIO(get(url).decode())))
    pts = []
    for r in rows[1:]:
        try:
            pts.append([r[0], round(float(r[1]), 3)])
        except (ValueError, IndexError):
            pass  # 휴일 '.' 등
    return pts


_ACM = {}


def eia(sid):
    import pandas as pd
    raw = get(f"https://www.eia.gov/dnav/pet/hist_xls/{sid}w.xls", 90)
    df = pd.read_excel(io.BytesIO(raw), sheet_name="Data 1", skiprows=2)
    df = df.iloc[:, :2].dropna()
    df.columns = ["date", "v"]
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= START]
    return [[d.date().isoformat(), float(v)] for d, v in zip(df["date"], df["v"])]


def acm(col):
    import pandas as pd
    if "df" in _ACM:
        df = _ACM["df"]
        return [[d.date().isoformat(), round(float(v), 3)] for d, v in zip(df["DATE"], df[col]) if v == v]
    raw = get("https://www.newyorkfed.org/medialibrary/media/research/data_indicators/ACMTermPremium.xls", 90)
    df = pd.read_excel(io.BytesIO(raw), sheet_name="ACM Daily")
    df["DATE"] = pd.to_datetime(df["DATE"], format="%d-%b-%Y", errors="coerce")
    df = df.dropna(subset=["DATE"])
    df = df[df["DATE"] >= START]
    _ACM["df"] = df
    return acm(col)


# 포트폴리오 재구성·위험 신호 (기준은 이선철 칼럼에서 가져옴, 페이지에 출처 표기)
RULES = [
    dict(key="oil_silver", name="오일/실버 비율 3 이상", note="원유 최대 비중을 줄이고 다변화를 검토할 시점 (이선철 대표 기준)"),
    dict(key="gold_oil", name="금/원유 비율 13배럴 이하 (오일/금 정상화)", note="금 1온스 = 원유 약 13배럴(장기 평균, 이선철 대표 칼럼 기준)"),
    dict(key="move", name="MOVE 120 이상", note="국채 변동성 급등 → 나스닥·S&P 500 위험 신호 (사용자 설정 기준)"),
]


def _ratio(series, a, b, inv=False):
    if a not in series or b not in series:
        return None
    B = dict(series[b]["points"])
    rows = [(d, v / B[d]) for d, v in series[a]["points"] if d in B and v > 0 and B[d] > 0]
    if not rows:
        return None
    d, v = rows[-1]
    return d, (1 / v if inv else v)


def compute_signals(series, prev):
    vals = {
        "oil_silver": _ratio(series, "wti_front", "silver_front"),
        "gold_oil": _ratio(series, "gold_front", "wti_front"),
        "move": (series["move"]["points"][-1][0], series["move"]["points"][-1][1]) if "move" in series else None,
    }
    test = {"oil_silver": lambda v: v >= 3.0, "gold_oil": lambda v: v <= 13.0, "move": lambda v: v >= 120.0}
    out = {}
    for r in RULES:
        k = r["key"]; v = vals.get(k)
        if not v:
            if k in prev: out[k] = prev[k]
            continue
        on = bool(test[k](v[1]))
        was = prev.get(k, {}).get("on", False)
        since = prev.get(k, {}).get("since") if on == was else v[0]
        out[k] = dict(name=r["name"], note=r["note"], date=v[0], value=round(v[1], 3), on=on, since=since,
                      changed=(on != was))
    return out


def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {"series": {}}
    series, errors = {}, []
    jobs = [(k, n, u, "Yahoo Finance", f"https://finance.yahoo.com/quote/{urllib.parse.quote(s)}", (lambda s=s: yahoo(s))) for k, n, s, u in FUT]
    jobs += [(k, n, u, "FRED", f"https://fred.stlouisfed.org/series/{s}", (lambda s=s: fred(s))) for k, n, s, u in FRED]
    jobs += [(k, n, "천배럴", "미 에너지정보청(EIA)", f"https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s={s}&f=W", (lambda s=s: eia(s))) for k, n, s in EIA]
    ACM_LINK = "https://www.newyorkfed.org/research/data_indicators/term-premia-tabs"
    for key, name, col in [("tp10_acm", "10년 명목 텀프리미엄 (ACM)", "ACMTP10"),
                           ("rny10_acm", "기대 단기금리 경로 (ACM 위험중립 10년)", "ACMRNY10"),
                           ("y10_acm", "10년물 금리 (ACM 모형 적합치)", "ACMY10")]:
        jobs.append((key, name, "%" if col != "ACMTP10" else "%p", "뉴욕 연은", ACM_LINK, (lambda c=col: acm(c))))
    for key, name, unit, src, link, fn in jobs:
        prev = old.get("series", {}).get(key)
        try:
            pts = fn()
            if not pts:
                raise ValueError("빈 데이터")
            series[key] = dict(name=name, unit=unit, source=src, link=link, points=pts, ok=True)
        except Exception as e:
            errors.append(f"{key}: {e}")
            traceback.print_exc()
            if prev:
                prev["ok"] = False
                series[key] = prev
    signals = compute_signals(series, old.get("signals", {}))
    out = dict(signals=signals, updated_utc=dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
               series=series, errors=errors)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    newly = [s for s in signals.values() if s.get("changed")]
    (OUT.parent.parent.parent / "alerts_new.json").write_text(json.dumps(newly, ensure_ascii=False))
    write_prices()
    print(f"wrote {OUT} ({len(series)} series, {len(errors)} errors)")
    if len(errors) == len(jobs):
        sys.exit(1)


def write_prices():
    """관심기업 주가를 companies/prices.json에 저장. 실패한 종목은 이전 값을 유지."""
    old = json.loads(PRICES.read_text()) if PRICES.exists() else {"prices": {}}
    out, errs = {}, []
    for slug, sym, cur in COMP:
        try:
            pts = yahoo(sym, closed_only=True)
            if not pts:
                raise ValueError("빈 데이터")
            out[slug] = dict(symbol=sym, currency=cur, points=pts, ok=True,
                             link=f"https://finance.yahoo.com/quote/{urllib.parse.quote(sym)}")
        except Exception as e:
            errs.append(f"{slug}: {e}")
            if slug in old.get("prices", {}):
                out[slug] = dict(old["prices"][slug], ok=False)
    PRICES.write_text(json.dumps(dict(updated_utc=dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
                                      prices=out, errors=errs), ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {PRICES} ({len(out)} companies, {len(errs)} errors)")


if __name__ == "__main__":
    main()
