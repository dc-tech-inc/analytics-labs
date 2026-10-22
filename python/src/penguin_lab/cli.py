"""Command line: `python -m penguin_lab.cli stats|model|figures`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .analysis import DEFAULT_CSV, expected_stats, load_penguins, species_summary  # noqa: E402
from .model import train_species_model  # noqa: E402


def make_figure(df, out: Path) -> Path:
    """Scatter of flipper length vs body mass by species."""
    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=120)
    for species, g in df.groupby("species"):
        ax.scatter(g["flipper_length_mm"], g["body_mass_g"], s=14, alpha=0.8, label=species)
    ax.set_xlabel("Flipper length (mm)")
    ax.set_ylabel("Body mass (g)")
    ax.set_title("Palmer penguins (CC0)")
    ax.legend(title="Species")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="penguin_lab")
    p.add_argument("command", choices=["stats", "model", "figures"])
    p.add_argument("--csv", default=str(DEFAULT_CSV))
    p.add_argument("--out", default="outputs")
    a = p.parse_args(argv)
    df = load_penguins(a.csv)
    if a.command == "stats":
        path = Path(a.csv).with_name("expected_stats.json")
        path.write_text(json.dumps(expected_stats(df), indent=2) + "\n")
        print(species_summary(df).to_string())
        print(f"wrote {path}")
    elif a.command == "model":
        print(json.dumps(train_species_model(df), indent=2))
    else:
        print(make_figure(df, Path(a.out) / "flipper_vs_mass.png"))


if __name__ == "__main__":
    main()
