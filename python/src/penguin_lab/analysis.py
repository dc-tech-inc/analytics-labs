"""Descriptive statistics, Welch t-test and OLS (mirror of r-quarto/R/analysis.R)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats

NUMERIC = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
DEFAULT_CSV = Path(__file__).resolve().parents[3] / "data" / "penguins.csv"


def load_penguins(path: Path | str = DEFAULT_CSV) -> pd.DataFrame:
    """Read the CSV and keep complete cases (the 4 measurements and sex)."""
    df = pd.read_csv(path)
    return df.dropna(subset=[*NUMERIC, "sex"]).reset_index(drop=True)


def species_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count, mean and sample standard deviation of each measurement per species."""
    g = df.groupby("species")
    out = g[NUMERIC].agg(["mean", "std"]).round(2)
    out.columns = [f"{col}_{fn}" for col, fn in out.columns]
    return out.assign(n=g.size()).reset_index()


def welch_test(df: pd.DataFrame, a: str, b: str, column: str = "flipper_length_mm") -> dict:
    """Welch two-sample t-test (unequal variances) between species a and b."""
    x = df.loc[df["species"] == a, column]
    y = df.loc[df["species"] == b, column]
    res = stats.ttest_ind(x, y, equal_var=False)
    return {
        "a": a,
        "b": b,
        "column": column,
        "t": float(res.statistic),
        "df": float(res.df),
        "p_value": float(res.pvalue),
        "mean_diff": float(x.mean() - y.mean()),
    }


def mass_on_flipper(df: pd.DataFrame) -> dict:
    """Ordinary least squares: body_mass_g ~ flipper_length_mm."""
    res = stats.linregress(df["flipper_length_mm"], df["body_mass_g"])
    return {
        "slope": float(res.slope),
        "intercept": float(res.intercept),
        "r_squared": float(res.rvalue**2),
        "n": int(len(df)),
    }


def expected_stats(df: pd.DataFrame) -> dict:
    """The numbers the R tests must reproduce."""
    return {
        "n_complete": int(len(df)),
        "welch_flipper_adelie_gentoo": welch_test(df, "Adelie", "Gentoo"),
        "ols_mass_on_flipper": mass_on_flipper(df),
    }
