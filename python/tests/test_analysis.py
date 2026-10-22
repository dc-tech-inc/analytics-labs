import json
from pathlib import Path

import pytest

from penguin_lab.analysis import (
    DEFAULT_CSV,
    expected_stats,
    load_penguins,
    mass_on_flipper,
    species_summary,
    welch_test,
)
from penguin_lab.cli import make_figure
from penguin_lab.model import train_species_model


@pytest.fixture(scope="module")
def df():
    return load_penguins()


def test_complete_cases(df):
    assert len(df) == 333
    assert df.isna().sum().sum() == 0


def test_species_counts(df):
    assert species_summary(df).set_index("species")["n"].to_dict() == {
        "Adelie": 146,
        "Chinstrap": 68,
        "Gentoo": 119,
    }


def test_welch_gentoo_flippers_are_longer(df):
    res = welch_test(df, "Adelie", "Gentoo")
    assert res["mean_diff"] < -25
    assert res["p_value"] < 1e-50
    assert 240 < res["df"] < 262  # Welch-Satterthwaite df is below n1 + n2 - 2


def test_regression_slope_is_positive(df):
    res = mass_on_flipper(df)
    assert 49 < res["slope"] < 51
    assert 0.75 < res["r_squared"] < 0.78


def test_expected_stats_file_is_current(df):
    """The JSON the R tests read must match what this code computes today."""
    on_disk = json.loads((Path(DEFAULT_CSV).parent / "expected_stats.json").read_text())
    fresh = json.loads(json.dumps(expected_stats(df)))
    for section in ("welch_flipper_adelie_gentoo", "ols_mass_on_flipper"):
        for key, value in fresh[section].items():
            # last-digit float differences between platforms are expected; 1e-9 is far below the R tolerance
            assert on_disk[section][key] == pytest.approx(value, rel=1e-9), (section, key)
    assert on_disk["n_complete"] == fresh["n_complete"]


def test_model_is_deterministic_and_accurate(df):
    a, b = train_species_model(df, seed=1), train_species_model(df, seed=1)
    assert a == b
    assert a["cv_accuracy"] > 0.95
    assert sum(map(sum, a["confusion_matrix"])) == a["n_test"]


def test_figure_is_written(df, tmp_path):
    out = make_figure(df, tmp_path / "f.png")
    assert out.stat().st_size > 1000
