"""`ga4-synth generate` writes synthetic exports; `ga4-synth report` builds report.json and index.html."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dashboard import render
from .generate import generate, write
from .pipeline import build_report


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="ga4-synth")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--seed", type=int, default=7)
    g.add_argument("--days", type=int, default=28)
    g.add_argument("--out", type=Path, default=Path("data"))
    r = sub.add_parser("report")
    r.add_argument("--data", type=Path, default=Path("data"))
    r.add_argument("--out", type=Path, default=Path("dist"))
    a = p.parse_args(argv)
    if a.cmd == "generate":
        write(generate(seed=a.seed, days=a.days), a.out)
        print(f"wrote synthetic exports to {a.out}")
    else:
        report = build_report(a.data)
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        (a.out / "index.html").write_text(render(report), encoding="utf-8")
        print(f"wrote {a.out / 'index.html'}")


if __name__ == "__main__":
    main()
