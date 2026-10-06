"""기업 페이지에 박힌 분석 시점 가치평가 값을 읽어 companies/base.json으로 저장한다.
live-price.js가 이 값과 매일 갱신되는 prices.json을 비교해 주가 연동 지표를 다시 계산한다.
실적 반영으로 페이지를 다시 만든 뒤에는 이 스크립트를 다시 실행한다."""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1] / "macro-notes" / "companies"
DEC = json.JSONDecoder()
DATES = {  # 페이지에 asof가 없을 때 쓰는 분석 기준일
    "samsung-electronics": "2026-09-23", "sk-hynix": "2026-09-23",
}
DEFAULT_DATE = "2026-09-25"


def grab(html, key):
    m = re.search(r'"%s":\s*\{' % key, html)
    if not m:
        return None
    return DEC.raw_decode(html, m.end() - 1)[0]


def clip(v):
    return max(0.0, min(1.0, v))


RULES = {  # 페이지 점수 규칙과 동일
    "cn_ev": lambda x: clip((25 - x) / 20), "pe": lambda x: clip((25 - x) / 17),
    "cn_yield": lambda y: clip(y / 0.10), "nc": lambda y: clip(y / 0.5),
    "en_ev": lambda x: clip((5 - x) / 2.5), "en_yield": lambda y: clip(y / 0.20),
    "pnav": lambda x: clip((1.5 - x) / 1),
}


def val_items(score, kind, b):
    """가치평가 기둥의 항목별로 주가에 따라 어떻게 변하는지(move)와 점수 규칙(rule)을 붙인다.
    분석 시점 값으로 규칙을 다시 계산해 페이지 점수와 맞을 때만 rule을 남긴다(자체 검증)."""
    pil = next((p for p in score["pillars"] if p["name"] == "가치평가"), None)
    if not pil:
        return None
    items = []
    for it in pil["items"]:
        k, v = it["k"], str(it["val"])
        m = re.search(r"-?\d+(?:\.\d+)?", v.replace(",", ""))
        x = float(m.group()) / (100 if "%" in v[: m.end() + 1] else 1) if m else None
        if k.startswith("EV/"):
            move, rule = "ev", ("en_ev" if kind == "energy" else "cn_ev")
        elif k.startswith("PER"):
            move, rule = "price", "pe"
        elif "수익률" in k:
            move, rule = "inv", ("en_yield" if kind == "energy" else "cn_yield")
        elif k.startswith("순현금"):
            move, rule = "inv", "nc"
        elif "NAV" in k:
            move, rule = "price", "pnav"
        else:
            move, rule = "fixed", None
        exact = {"ev": b.get("ev_op") if kind == "cn" else b.get("ev_ebitdax"), "price": b.get("pe"),
                 "inv": b.get("fcf_yield") if "수익률" in k else b.get("nc_share")}.get(move)
        if "NAV" in k and b.get("nav_sec"):
            exact = b["price"] / b["nav_sec"] if b["nav_sec"] > 0 else None
        if x is not None and exact is not None and abs(exact - x) <= 0.06 * abs(x) + 0.006:
            x = exact  # 페이지 표시값(반올림) 대신 정밀값
        if x is None or rule is None or abs(RULES[rule](x) - it["pts"]) > 0.02:
            move, rule = "fixed", None
        items.append(dict(k=k, val=v, x=x, pts=it["pts"], move=move, rule=rule))
    return dict(max=pil["max"], score=pil["score"], items=items,
                others=round(sum(p["score"] for p in score["pillars"] if p is not pil), 3))


def main():
    out = {}
    for page in sorted(ROOT.glob("*/index.html")):
        slug, html = page.parent.name, page.read_text()
        cn, val, nav, score = grab(html, "cnval"), grab(html, "val"), grab(html, "nav"), grab(html, "score")
        b = {"score": score.get("total") if score else None}
        if cn:
            b.update(kind="cn", date=cn.get("asof") or DATES.get(slug, DEFAULT_DATE), price=cn["price"],
                     mcap=cn["mcap_b"], netcash=cn["netcash_b"], ev=cn["ev_b"], ev_op=cn.get("ev_op"),
                     pe=cn.get("pe"), fcf_yield=cn.get("fcf_yield"), nc_share=cn.get("nc_share"))
        elif val and "net_debt_m" in val:
            b.update(kind="energy", date=val.get("asof") or DATES.get(slug, DEFAULT_DATE), price=val["price"],
                     mcap=val["mktcap_m"], net_debt=val["net_debt_m"], ev=val["ev_m"],
                     ev_ebitdax=val.get("ev_ebitdax_q2ann"), fcf_yield=val.get("fcf_yield_h1ann"))
            if nav and nav.get("rows"):
                r0 = nav["rows"][0]
                b.update(nav_sec=r0["nav"], nav_oil0=r0["oil"], nav_per10=nav.get("per10"), nav_bench=nav.get("bench"))
        else:
            continue
        b["val_pillar"] = val_items(score, b["kind"], b) if score else None
        out[slug] = b
    (ROOT / "base.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"base.json: {len(out)} companies")


if __name__ == "__main__":
    main()
