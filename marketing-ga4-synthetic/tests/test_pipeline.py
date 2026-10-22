import json

import pytest

from ga4_synth.cli import main
from ga4_synth.dashboard import render
from ga4_synth.generate import generate, write
from ga4_synth.pipeline import (
    build_report,
    channel_group,
    read_events,
    search_report,
    sessionize,
)


@pytest.fixture(scope="module")
def data():
    return generate(seed=3, days=7)


def test_same_seed_same_data():
    assert generate(seed=1, days=2) == generate(seed=1, days=2)
    assert generate(seed=1, days=2) != generate(seed=2, days=2)


def test_events_follow_ga4_export_shape(data):
    e = data["events"][0]
    assert {
        "event_date",
        "event_timestamp",
        "event_name",
        "event_params",
        "user_pseudo_id",
    } <= e.keys()
    assert len(e["event_date"]) == 8 and isinstance(e["event_timestamp"], int)
    assert set(e["event_params"][0]["value"]) == {
        "string_value",
        "int_value",
        "float_value",
        "double_value",
    }
    assert {"name", "medium", "source"} == set(e["traffic_source"])


def test_no_real_hosts_or_people(data):
    blob = json.dumps(data)
    assert "example.test" in blob
    assert "@" not in blob


def test_channel_grouping():
    assert channel_group("google", "cpc") == "Paid Search"
    assert channel_group("google", "organic") == "Organic Search"
    assert channel_group("(direct)", "(none)") == "Direct"


def test_sessionize_counts_every_purchase_once(data):
    sessions = sessionize(data["events"])
    assert sum(s["purchases"] for s in sessions) == sum(
        e["event_name"] == "purchase" for e in data["events"]
    )
    assert all(s["pages"] >= 1 for s in sessions)


def test_paid_clicks_reconcile_with_ga_sessions(tmp_path):
    out = tmp_path / "d"
    write(generate(seed=5, days=7), out)
    report = build_report(out)
    for row in report["ads"]:
        ratio = row["clicks"] / row["ga_sessions"]
        assert 0.95 < ratio < 1.15, (
            row
        )  # ad clicks always at least the sessions GA recorded, within ~12 %


def test_search_report_weights_position_by_impressions():
    rows = [
        {"query": "q", "clicks": 1, "impressions": 90, "ctr": 0.01, "position": 2.0},
        {"query": "q", "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 12.0},
    ]
    assert search_report(rows)["top_queries"][0]["position"] == 3.0


def test_cli_roundtrip_and_dashboard(tmp_path):
    main(["generate", "--days", "3", "--out", str(tmp_path / "d")])
    main(["report", "--data", str(tmp_path / "d"), "--out", str(tmp_path / "o")])
    html = (tmp_path / "o" / "index.html").read_text(encoding="utf-8")
    assert "Synthetic data" in html and "<script" not in html and "http://" not in html
    assert read_events(tmp_path / "d")
    assert json.loads((tmp_path / "o" / "report.json").read_text())["synthetic"] is True


def test_render_escapes_html(data, tmp_path):
    write(data, tmp_path)
    report = build_report(tmp_path)
    report["search"]["top_queries"][0]["query"] = "<img src=x onerror=alert(1)>"
    assert "<img src=x" not in render(report)
