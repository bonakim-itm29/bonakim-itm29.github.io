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
]


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


LONG = {"CL=F", "SI=F", "GC=F"}  # 오일/실버 비율의 장기 비교용


def yahoo(sym):
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
    # 같은 날짜 중복 시 마지막 값
    return [[d, v] for d, v in dict(pts).items()]


def fred(sid):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}"
    rows = list(csv.reader(io.StringIO(get(url).decode())))
    pts = []
    for r in rows[1:]:
        try:
            pts.append([r[0], round(float(r[1]), 3)])
        except (ValueError, IndexError):
            pass  # 휴일 '.' 등
    return pts


_ACM = {}


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
    dict(key="oil_silver", name="오일/실버 비율 3 이상", note="투자 시계열에서 원유 MAX 포지션을 줄이고 다변화할 시점 (NOTE #251, 2026-09-15)"),
    dict(key="gold_oil", name="금/원유 비율 13배럴 이하 (오일/금 정상화)", note="금 1온스 = 원유 약 13배럴이 장기 평균. 비율 정상화는 유가 급등으로 이뤄질 것 (2026-07-23, 2026-08-09 칼럼)"),
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
    print(f"wrote {OUT} ({len(series)} series, {len(errors)} errors)")
    if len(errors) == len(jobs):
        sys.exit(1)


if __name__ == "__main__":
    main()
