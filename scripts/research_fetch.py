"""연구용 원자료 수집 (수동 실행 전용 GitHub Actions).

사이트 페이지와 무관하며, 결과는 research-data 브랜치에만 저장한다.
spec(JSON): {"sec": ["PDD", ...], "since": "2026-03-01",
             "docs": [["PDD", "0001104659-26-000000"], ...],
             "yahoo": ["PDD", ...], "fred": ["DGS10", ...]}
"""
import json, os, pathlib, sys, time, csv, io, datetime as dt
import urllib.request, urllib.parse

OUT = pathlib.Path("out")
SEC_UA = {"User-Agent": "bonakim-itm29 research bonakim-itm29@users.noreply.github.com",
          "Accept-Encoding": "identity"}
WEB_UA = {"User-Agent": "Mozilla/5.0 (research fetch)"}
log = []


def get(url, headers, timeout=60, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            log.append(f"retry {i} {url}: {e}")
            time.sleep(2 + 3 * i)
    raise RuntimeError(f"failed {url}")


def sec_get(url):
    time.sleep(0.25)  # SEC 공정 접근 기준(초당 10회 미만)
    return get(url, SEC_UA)


def save(rel, data):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode())


def ciks():
    j = json.loads(sec_get("https://www.sec.gov/files/company_tickers.json"))
    return {v["ticker"]: int(v["cik_str"]) for v in j.values()}


def filing_files(cik, acc):
    nod = acc.replace("-", "")
    idx = json.loads(sec_get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{nod}/index.json"))
    return [it["name"] for it in idx["directory"]["item"]
            if it["name"].lower().endswith((".htm", ".html", ".pdf")) and "index" not in it["name"].lower()
            and int(it.get("size") or 0) < 25_000_000]


def submissions(cik):
    base = json.loads(sec_get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    rows = []
    def add(r):
        for i in range(len(r["form"])):
            rows.append(dict(form=r["form"][i], filed=r["filingDate"][i], acc=r["accessionNumber"][i],
                             doc=r["primaryDocument"][i], desc=r.get("primaryDocDescription", [""] * len(r["form"]))[i],
                             size=r["size"][i]))
    add(base["filings"]["recent"])
    for f in base["filings"].get("files", []):
        add(json.loads(sec_get("https://data.sec.gov/submissions/" + f["name"])))
    return base, rows


def main(spec):
    sec = spec.get("sec", [])
    since = spec.get("since", "2026-01-01")
    cmap = ciks() if (sec or spec.get("docs")) else {}
    hist = {}
    for t in sec:
        cik = cmap[t]
        base, rows = submissions(cik)
        hist[t] = dict(name=base.get("name"), cik=cik, fiscalYearEnd=base.get("fiscalYearEnd"), rows=rows)
        save(f"xbrl_{t}.json", sec_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"))
        f20 = [r for r in rows if r["form"] in ("20-F", "10-K")][:1]
        k6 = [r for r in rows if r["form"] in ("6-K", "8-K") and r["filed"] >= since]
        for r in f20:
            save(f"raw/{t}__{r['form']}__{r['filed']}__{r['doc']}", sec_get(
                f"https://www.sec.gov/Archives/edgar/data/{cik}/{r['acc'].replace('-', '')}/{r['doc']}"))
        for r in k6:
            for name in filing_files(cik, r["acc"]):
                save(f"raw/{t}__{r['form']}__{r['filed']}__{name}", sec_get(
                    f"https://www.sec.gov/Archives/edgar/data/{cik}/{r['acc'].replace('-', '')}/{name}"))
    if hist:
        save("sec_hist.json", json.dumps(hist, ensure_ascii=False))
    for t, acc in spec.get("docs", []):
        cik = cmap[t]
        for name in filing_files(cik, acc):
            save(f"raw_events/{t}__{acc.replace('-', '')}__{name}", sec_get(
                f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{name}"))
    now = int(time.time())
    ev = {}
    for s in spec.get("yahoo", []):
        u = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}"
             f"?period1=0&period2={now}&interval=1d&events=div,splits")
        try:
            j = json.loads(get(u, WEB_UA))["chart"]["result"][0]
        except Exception as e:
            log.append(f"yahoo fail {s}: {e}")
            continue
        q = j["indicators"]["quote"][0]
        adj = (j["indicators"].get("adjclose") or [{}])[0].get("adjclose") or [None] * len(j["timestamp"])
        buf = io.StringIO(); w = csv.writer(buf); w.writerow(["date", "close", "adjclose"])
        for t_, c, a in zip(j["timestamp"], q["close"], adj):
            w.writerow([dt.datetime.utcfromtimestamp(t_).date().isoformat(), c, a])
        save(f"yahoo/{s.replace('^', '_').replace('=', '_')}.csv", buf.getvalue())
        ev[s] = j.get("events", {})
    if ev:
        save("yahoo_events.json", json.dumps(ev))
    for sid in spec.get("fred", []):
        try:
            save(f"fred/{sid}.csv", get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", WEB_UA))
        except Exception as e:
            log.append(f"fred fail {sid}: {e}")
    save("log.txt", "\n".join(log))
    print("\n".join(log[-30:]))


if __name__ == "__main__":
    main(json.loads(os.environ["SPEC"]))
