"""Render the report dict as one self-contained static HTML page (no scripts, no external requests)."""

from __future__ import annotations

from html import escape

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--fg:#14202b;--muted:#4a5a69;--line:rgba(20,32,43,.14);--accent:#0e7490;--warn-bg:#fff4d6;--warn-fg:#5c4200}
@media (prefers-color-scheme:dark){:root{--bg:#10171d;--card:#17212a;--fg:#e6edf3;--muted:#a9b8c6;--line:rgba(255,255,255,.12);--accent:#5cc6de;--warn-bg:#3a2f0b;--warn-fg:#ffe6a3}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,"Segoe UI",sans-serif}
main{max-width:1040px;margin:0 auto;padding:16px}
.banner{background:var(--warn-bg);color:var(--warn-fg);padding:10px 16px;font-weight:600}
h1{font-size:1.6rem;margin:.6rem 0 .2rem}h2{font-size:1.1rem;margin:0 0 .6rem}
.lede{color:var(--muted);margin:0 0 1rem}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin-bottom:16px}
.kpis .card{margin:0}.k{color:var(--muted);font-size:.85rem}.v{font-size:1.5rem;font-weight:650;font-variant-numeric:tabular-nums}
.v.focus{color:var(--accent)}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;font-size:.92rem}
th,td{text-align:right;padding:8px 10px;border-bottom:1px solid var(--line)}th:first-child,td:first-child{text-align:left}
th{color:var(--muted);font-weight:600}.scroll{overflow-x:auto}
svg{width:100%;height:auto;display:block}.axis{fill:var(--muted);font-size:11px}.bar{fill:var(--accent)}.line{stroke:var(--accent);fill:none;stroke-width:2}
footer{color:var(--muted);font-size:.85rem;padding:8px 0 24px}
"""


def _n(x) -> str:
    return "n/a" if x is None else f"{x:,.0f}" if isinstance(x, int) else f"{x:,.2f}"


def _d(yyyymmdd: str) -> str:
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}"


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _table(headers: list[str], rows: list[list[str]], caption: str) -> str:
    head = "".join(f'<th scope="col">{escape(h)}</th>' for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in r) + "</tr>" for r in rows)
    return (
        f'<div class="scroll"><table><caption class="axis" style="text-align:left">{escape(caption)}</caption>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def _line_chart(daily: list[dict]) -> str:
    w, h, pad = 640, 200, 34
    vals = [d["sessions"] for d in daily]
    hi = max(vals) or 1
    pts = " ".join(
        f"{pad + i * (w - 2 * pad) / max(1, len(vals) - 1):.1f},{h - pad - v / hi * (h - 2 * pad):.1f}"
        for i, v in enumerate(vals)
    )
    return (
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Daily sessions, {_d(daily[0]["date"])} to {_d(daily[-1]["date"])}, '
        f'peak {hi}. The table below holds the same data.">'
        f'<line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="currentColor" opacity=".25"/>'
        f'<polyline class="line" points="{pts}"/>'
        f'<text class="axis" x="{pad}" y="{h - 10}">{_d(daily[0]["date"])}</text>'
        f'<text class="axis" x="{w - pad}" y="{h - 10}" text-anchor="end">{_d(daily[-1]["date"])}</text>'
        f'<text class="axis" x="{pad}" y="14">peak {hi:,}</text></svg>'
    )


def _bar_chart(channels: list[dict]) -> str:
    w, row = 640, 30
    hi = max(c["sessions"] for c in channels) or 1
    rows = []
    for i, c in enumerate(channels):
        bw = c["sessions"] / hi * (w - 260)
        y = i * row
        rows.append(
            f'<text class="axis" x="0" y="{y + 19}">{escape(c["channel"])}</text>'
            f'<rect class="bar" x="130" y="{y + 5}" width="{bw:.1f}" height="18" rx="2"/>'
            f'<text class="axis" x="{136 + bw:.1f}" y="{y + 19}">{c["sessions"]:,}</text>'
        )
    return (
        f'<svg viewBox="0 0 {w} {len(channels) * row}" role="img" aria-label="Sessions by channel">'
        + "".join(rows)
        + "</svg>"
    )


def render(report: dict) -> str:
    t = report["totals"]
    kpis = [
        ("Revenue (synthetic)", f"${t['revenue']:,.0f}", True),
        ("Sessions", _n(t["sessions"]), False),
        ("Engagement rate", _pct(t["engagement_rate"]), False),
        ("Conversion rate", _pct(t["conversion_rate"]), False),
        ("Ad spend", f"${t['ad_spend']:,.0f}", False),
    ]
    kpi_html = "".join(
        f'<div class="card"><div class="k">{k}</div><div class="v{" focus" if f else ""}">{v}</div></div>'
        for k, v, f in kpis
    )
    ch_rows = [
        [
            c["channel"],
            _n(c["sessions"]),
            _pct(c["engagement_rate"]),
            _pct(c["conversion_rate"]),
            f"${c['revenue']:,.0f}",
        ]
        for c in report["channels"]
    ]
    ad_rows = [
        [
            a["campaign"],
            a["platform"],
            _n(a["clicks"]),
            _pct(a["ctr"]),
            f"${a['cost']:,.0f}",
            f"${a['cpc']:.2f}",
            _n(a["cpa"]),
            _n(a["roas"]),
        ]
        for a in report["ads"]
    ]
    q_rows = [
        [q["query"], _n(q["clicks"]), _n(q["impressions"]), _pct(q["ctr"]), _n(q["position"])]
        for q in report["search"]["top_queries"]
    ]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Marketing report (synthetic data)</title><style>{CSS}</style></head>
<body><div class="banner" role="note">Synthetic data: generated by a seeded script, not from any real site, client or Google account.</div>
<main><h1>Marketing report</h1>
<p class="lede">GA4-style events, Search Console and Ads exports combined. Built by DCtech. analytics-labs.</p>
<section class="kpis" aria-label="Key figures">{kpi_html}</section>
<section class="card"><h2>Sessions per day</h2>{_line_chart(report["daily"])}</section>
<section class="card"><h2>Sessions by channel</h2>{_bar_chart(report["channels"])}
{_table(["Channel", "Sessions", "Engagement", "Conversion", "Revenue"], ch_rows, "Channel performance")}</section>
<section class="card"><h2>Paid campaigns</h2>
{_table(["Campaign", "Platform", "Clicks", "CTR", "Cost", "CPC", "CPA", "ROAS"], ad_rows, "ROAS = GA revenue of the matching channel / ad cost")}</section>
<section class="card"><h2>Search Console: top queries</h2>
<p class="lede">{report["search"]["clicks"]:,} clicks, {report["search"]["impressions"]:,} impressions, CTR {_pct(report["search"]["ctr"])}.</p>
{_table(["Query", "Clicks", "Impressions", "CTR", "Avg position"], q_rows, "Impression-weighted average position")}</section>
<footer>Synthetic data. Revenue, spend and every rate above are invented to exercise the pipeline.</footer></main></body></html>
"""
