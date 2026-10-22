"""Seeded generator. Everything it emits is invented; nothing is derived from real traffic.

Event rows follow the documented GA4 BigQuery export schema (`events_YYYYMMDD`):
https://support.google.com/analytics/answer/7029846
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SITE = "https://shop.example.test"  # reserved TLD, cannot resolve

# (source, medium, campaign name, weight of daily sessions, conversion probability)
CHANNELS = [
    ("google", "cpc", "brand-search", 0.14, 0.060),
    ("facebook", "paid_social", "spring-retargeting", 0.12, 0.030),
    ("newsletter", "email", "weekly-digest", 0.08, 0.075),
    ("partner-blog.example.test", "referral", "(referral)", 0.06, 0.035),
    ("(direct)", "(none)", "(direct)", 0.22, 0.045),
]
ORGANIC = ("google", "organic", "(organic)", 0.025)

QUERIES = [  # (query, page, base daily impressions, typical position)
    ("ergonomic desk lamp", "/lamps/desk", 900, 4.2),
    ("led desk lamp", "/lamps/desk", 700, 6.8),
    ("standing desk mat", "/mats", 520, 3.1),
    ("cable organizer box", "/accessories/cables", 430, 5.5),
    ("monitor riser wood", "/risers", 380, 7.9),
    ("laptop stand aluminium", "/stands/laptop", 600, 8.4),
    ("shop.example.test", "/", 300, 1.2),
    ("desk accessories set", "/sets", 260, 11.0),
]

PAGES = ["/", "/lamps/desk", "/mats", "/risers", "/stands/laptop", "/cart"]
DEVICES = [("mobile", 0.58), ("desktop", 0.36), ("tablet", 0.06)]
COUNTRIES = [
    ("United States", 0.5),
    ("United Kingdom", 0.15),
    ("Germany", 0.12),
    ("Brazil", 0.12),
    ("Canada", 0.11),
]


def _pick(rng: random.Random, weighted):
    r, acc = rng.random(), 0.0
    for value, w in weighted:
        acc += w
        if r <= acc:
            return value
    return weighted[-1][0]


def _ctr_for_position(pos: float) -> float:
    return max(0.004, 0.32 * (0.72 ** (pos - 1)))


def _param(key: str, **value) -> dict:
    full = {"string_value": None, "int_value": None, "float_value": None, "double_value": None}
    full.update(value)
    return {"key": key, "value": full}


def generate(seed: int = 7, days: int = 28, start: date = date(2026, 1, 5)) -> dict:
    """Return {"events": [...], "search_console": [...], "ads": [...]} for `days` days."""
    rng = random.Random(seed)
    events, gsc, ads = [], [], []
    for d in range(days):
        day = start + timedelta(days=d)
        weekend = day.weekday() >= 5
        factor = (0.8 if weekend else 1.0) * (1 + 0.004 * d) * rng.uniform(0.92, 1.08)

        organic_clicks = 0
        for query, page, imp, pos in QUERIES:
            impressions = max(0, round(imp * factor * rng.uniform(0.85, 1.15)))
            position = round(max(1.0, pos + rng.uniform(-0.6, 0.6)), 1)
            clicks = round(impressions * _ctr_for_position(position) * rng.uniform(0.85, 1.15))
            organic_clicks += clicks
            gsc.append(
                {
                    "date": day.isoformat(),
                    "query": query,
                    "page": SITE + page,
                    "clicks": clicks,
                    "impressions": impressions,
                    "ctr": round(clicks / impressions, 4) if impressions else 0.0,
                    "position": position,
                }
            )

        plan = [(ORGANIC[0], ORGANIC[1], ORGANIC[2], round(organic_clicks * 0.92), ORGANIC[3])]
        for source, medium, campaign, weight, cr in CHANNELS:
            plan.append(
                (source, medium, campaign, round(400 * weight * factor * rng.uniform(0.9, 1.1)), cr)
            )

        for source, medium, campaign, n_sessions, cr in plan:
            purchases = 0
            for _ in range(n_sessions):
                purchased = _session(rng, events, day, source, medium, campaign, cr)
                purchases += purchased
            if medium in ("cpc", "paid_social"):
                clicks = round(n_sessions * rng.uniform(1.0, 1.12))
                ctr = rng.uniform(0.018, 0.045) if medium == "cpc" else rng.uniform(0.008, 0.02)
                cpc = rng.uniform(0.45, 0.9) if medium == "cpc" else rng.uniform(0.3, 0.7)
                ads.append(
                    {
                        "date": day.isoformat(),
                        "platform": "google_ads" if medium == "cpc" else "meta_ads",
                        "campaign": campaign,
                        "impressions": round(clicks / ctr),
                        "clicks": clicks,
                        "cost": round(clicks * cpc, 2),
                        "conversions": purchases,
                    }
                )
    return {"events": events, "search_console": gsc, "ads": ads}


def _session(rng, events, day, source, medium, campaign, cr) -> int:
    base = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    ts = int((base + timedelta(seconds=rng.randrange(86400))).timestamp() * 1_000_000)
    user = f"{rng.getrandbits(40):010x}.{rng.getrandbits(32):08x}"
    session_id = ts // 1_000_000
    device = _pick(rng, DEVICES)
    country = _pick(rng, COUNTRIES)
    traffic = {"name": campaign, "medium": medium, "source": source}
    n_pages = 1 + int(rng.expovariate(1.1))
    engaged_ms = int(rng.expovariate(1 / 28000))

    def row(name, offset_s, params, ecommerce=None):
        return {
            "event_date": day.strftime("%Y%m%d"),
            "event_timestamp": ts + offset_s * 1_000_000,
            "event_name": name,
            "event_params": [_param("ga_session_id", int_value=session_id), *params],
            "user_pseudo_id": user,
            "device": {"category": device},
            "geo": {"country": country},
            "traffic_source": traffic,
            "ecommerce": ecommerce or {"purchase_revenue": None, "transaction_id": None},
        }

    events.append(row("session_start", 0, []))
    for i in range(n_pages):
        page = rng.choice(PAGES)
        params = [_param("page_location", string_value=SITE + page)]
        if i == n_pages - 1:
            params.append(_param("engagement_time_msec", int_value=engaged_ms))
        events.append(row("page_view", 5 + 20 * i, params))
    if rng.random() < cr:
        revenue = round(rng.lognormvariate(3.9, 0.45), 2)
        events.append(
            row(
                "purchase",
                30 + 20 * n_pages,
                [_param("currency", string_value="USD")],
                {"purchase_revenue": revenue, "transaction_id": f"T{rng.getrandbits(32):08x}"},
            )
        )
        return 1
    return 0


def write(data: dict, out: Path) -> None:
    """events_YYYYMMDD.jsonl per day (one JSON object per line, like a BigQuery export), plus two CSVs."""
    out.mkdir(parents=True, exist_ok=True)
    by_day: dict[str, list] = {}
    for e in data["events"]:
        by_day.setdefault(e["event_date"], []).append(e)
    for day, rows in by_day.items():
        with (out / f"events_{day}.jsonl").open("w", encoding="utf-8", newline="\n") as f:
            f.writelines(json.dumps(r, separators=(",", ":")) + "\n" for r in rows)
    for name in ("search_console", "ads"):
        rows = data[name]
        with (out / f"{name}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
