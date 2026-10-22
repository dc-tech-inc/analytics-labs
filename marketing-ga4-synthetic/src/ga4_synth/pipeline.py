"""Turn raw GA4-style events, Search Console and Ads rows into report tables."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def read_events(folder: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(folder.glob("events_*.jsonl")):
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return rows


def read_csv(path: Path, numeric: tuple[str, ...]) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in numeric:
            r[k] = float(r[k]) if "." in r[k] else int(r[k])
    return rows


def channel_group(source: str, medium: str) -> str:
    """Simplified version of GA4's default channel group rules."""
    if medium == "cpc":
        return "Paid Search"
    if medium == "paid_social":
        return "Paid Social"
    if medium == "organic":
        return "Organic Search"
    if medium == "email":
        return "Email"
    if medium == "referral":
        return "Referral"
    return "Direct"


def _param(event: dict, key: str, field: str):
    for p in event["event_params"]:
        if p["key"] == key:
            return p["value"][field]
    return None


def sessionize(events: list[dict]) -> list[dict]:
    """Group events by (user_pseudo_id, ga_session_id), as the GA4 export docs recommend."""
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for e in events:
        grouped[(e["user_pseudo_id"], _param(e, "ga_session_id", "int_value"))].append(e)
    sessions = []
    for (user, sid), evs in grouped.items():
        first = min(evs, key=lambda e: e["event_timestamp"])
        ts = first["traffic_source"]
        pages = sum(e["event_name"] == "page_view" for e in evs)
        engaged_ms = sum(_param(e, "engagement_time_msec", "int_value") or 0 for e in evs)
        revenue = sum(e["ecommerce"]["purchase_revenue"] or 0 for e in evs)
        purchases = sum(e["event_name"] == "purchase" for e in evs)
        sessions.append(
            {
                "user": user,
                "session_id": sid,
                "date": first["event_date"],
                "channel": channel_group(ts["source"], ts["medium"]),
                "source_medium": f"{ts['source']} / {ts['medium']}",
                "device": first["device"]["category"],
                "country": first["geo"]["country"],
                "pages": pages,
                # GA4 definition: >=10 s engaged, or a key event, or >=2 page views
                "engaged": engaged_ms >= 10_000 or purchases > 0 or pages >= 2,
                "purchases": purchases,
                "revenue": round(revenue, 2),
            }
        )
    return sessions


def _rate(a: float, b: float) -> float:
    return round(a / b, 4) if b else 0.0


def channel_report(sessions: list[dict]) -> list[dict]:
    acc: dict[str, dict] = defaultdict(
        lambda: {"sessions": 0, "engaged": 0, "purchases": 0, "revenue": 0.0}
    )
    for s in sessions:
        a = acc[s["channel"]]
        a["sessions"] += 1
        a["engaged"] += s["engaged"]
        a["purchases"] += s["purchases"]
        a["revenue"] += s["revenue"]
    out = [
        {
            "channel": ch,
            "sessions": a["sessions"],
            "engagement_rate": _rate(a["engaged"], a["sessions"]),
            "purchases": a["purchases"],
            "conversion_rate": _rate(a["purchases"], a["sessions"]),
            "revenue": round(a["revenue"], 2),
        }
        for ch, a in acc.items()
    ]
    return sorted(out, key=lambda r: -r["sessions"])


def daily_sessions(sessions: list[dict]) -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for s in sessions:
        acc[s["date"]] += 1
    return [{"date": d, "sessions": n} for d, n in sorted(acc.items())]


def ads_report(ads: list[dict], sessions: list[dict]) -> list[dict]:
    """Spend, CPC, CPA and ROAS per campaign. Revenue comes from GA sessions of the matching channel."""
    channel_of = {"google_ads": "Paid Search", "meta_ads": "Paid Social"}
    revenue = defaultdict(float)
    ga_sessions = defaultdict(int)
    for s in sessions:
        revenue[s["channel"]] += s["revenue"]
        ga_sessions[s["channel"]] += 1
    acc: dict[tuple, dict] = defaultdict(
        lambda: {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0}
    )
    for r in ads:
        a = acc[(r["platform"], r["campaign"])]
        a["impressions"] += r["impressions"]
        a["clicks"] += r["clicks"]
        a["cost"] += r["cost"]
        a["conversions"] += r["conversions"]
    out = []
    for (platform, campaign), a in acc.items():
        ch = channel_of[platform]
        out.append(
            {
                "platform": platform,
                "campaign": campaign,
                "impressions": a["impressions"],
                "clicks": a["clicks"],
                "ctr": _rate(a["clicks"], a["impressions"]),
                "cost": round(a["cost"], 2),
                "cpc": round(a["cost"] / a["clicks"], 2) if a["clicks"] else 0.0,
                "conversions": a["conversions"],
                "cpa": round(a["cost"] / a["conversions"], 2) if a["conversions"] else None,
                "ga_sessions": ga_sessions[ch],
                "roas": round(revenue[ch] / a["cost"], 2) if a["cost"] else None,
            }
        )
    return out


def search_report(gsc: list[dict]) -> dict:
    clicks = sum(r["clicks"] for r in gsc)
    impressions = sum(r["impressions"] for r in gsc)
    by_query: dict[str, dict] = defaultdict(
        lambda: {"clicks": 0, "impressions": 0, "pos_x_imp": 0.0}
    )
    for r in gsc:
        q = by_query[r["query"]]
        q["clicks"] += r["clicks"]
        q["impressions"] += r["impressions"]
        q["pos_x_imp"] += r["position"] * r["impressions"]
    top = [
        {
            "query": k,
            "clicks": v["clicks"],
            "impressions": v["impressions"],
            "ctr": _rate(v["clicks"], v["impressions"]),
            # impression-weighted average position, as Search Console reports it
            "position": round(v["pos_x_imp"] / v["impressions"], 1) if v["impressions"] else None,
        }
        for k, v in by_query.items()
    ]
    return {
        "clicks": clicks,
        "impressions": impressions,
        "ctr": _rate(clicks, impressions),
        "top_queries": sorted(top, key=lambda r: -r["clicks"]),
    }


def build_report(data_dir: Path) -> dict:
    sessions = sessionize(read_events(data_dir))
    ads = read_csv(data_dir / "ads.csv", ("impressions", "clicks", "cost", "conversions"))
    gsc = read_csv(data_dir / "search_console.csv", ("clicks", "impressions", "ctr", "position"))
    total_rev = round(sum(s["revenue"] for s in sessions), 2)
    purchases = sum(s["purchases"] for s in sessions)
    return {
        "synthetic": True,
        "totals": {
            "sessions": len(sessions),
            "users": len({s["user"] for s in sessions}),
            "engagement_rate": _rate(sum(s["engaged"] for s in sessions), len(sessions)),
            "purchases": purchases,
            "conversion_rate": _rate(purchases, len(sessions)),
            "revenue": total_rev,
            "ad_spend": round(sum(r["cost"] for r in ads), 2),
        },
        "channels": channel_report(sessions),
        "daily": daily_sessions(sessions),
        "ads": ads_report(ads, sessions),
        "search": search_report(gsc),
    }
