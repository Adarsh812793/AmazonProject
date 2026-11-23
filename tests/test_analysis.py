import numpy as np
import pandas as pd
import pytest

from amazon_project.analysis import (
    compute_category_magnitudes,
    compute_correlations,
    compute_univariate_magnitudes,
    detect_iqr_outliers,
    summarize_outliers,
)


@pytest.fixture
def sample_numeric_df() -> pd.DataFrame:
    """Sample DataFrame with prices, discounts, ratings, and outliers."""
    return pd.DataFrame(
        {
            "price": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 1000.0, np.nan],
            "discount": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 50.0],
            "rating": [4.0, 4.2, 4.1, 4.5, 3.8, 4.0, 4.3, 4.2, 4.1, 4.0],
            "main_category": [
                "Tech",
                "Tech",
                "Tech",
                "Tech",
                "Tech",
                "Home",
                "Home",
                "Home",
                "Home",
                "Rare",
            ],
            "is_small_category": [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
            ],
        }
    )


def test_compute_univariate_magnitudes(sample_numeric_df):
    stats = compute_univariate_magnitudes(sample_numeric_df, ["price", "discount"])
    assert "price" in stats.index
    assert "discount" in stats.index

    # Check non-null count and missing count
    assert stats.loc["price", "count"] == 9
    assert stats.loc["price", "missing"] == 1
    assert stats.loc["discount", "count"] == 10
    assert stats.loc["discount", "missing"] == 0

    # Check median and IQR
    assert stats.loc["price", "median"] == 50.0
    assert stats.loc["price", "min"] == 10.0
    assert stats.loc["price", "max"] == 1000.0
    assert (
        stats.loc["price", "iqr"]
        == stats.loc["price", "q75"] - stats.loc["price", "q25"]
    )
    assert stats.loc["price", "skew"] > 1.0  # Right-skewed due to 1000.0


def test_detect_iqr_outliers():
    # 10, 20, 30, 40, 50, 60, 70, 80: Q1=27.5, Q3=62.5, IQR=35
    # upper_bound = 62.5 + 1.5 * 35 = 115
    series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 1000.0])
    _lower, upper, mask = detect_iqr_outliers(series, multiplier=1.5)

    assert upper < 1000.0
    assert mask.sum() == 1
    assert mask.iloc[-1] is True or mask.iloc[-1] == 1


def test_summarize_outliers(sample_numeric_df):
    summary = summarize_outliers(sample_numeric_df, ["price", "discount"])
    assert "price" in summary.index
    assert summary.loc["price", "outlier_count"] == 1
    assert summary.loc["price", "max_outlier"] == 1000.0
    assert summary.loc["discount", "outlier_count"] == 0


def test_compute_category_magnitudes(sample_numeric_df):
    # Without excluding small categories
    grouped = compute_category_magnitudes(
        sample_numeric_df,
        category_col="main_category",
        metric_cols=["price", "discount"],
        exclude_small=False,
    )
    assert "Tech" in grouped.index
    assert "Home" in grouped.index
    assert "Rare" in grouped.index
    assert ("price", "median") in grouped.columns
    assert ("price", "iqr") in grouped.columns

    # With excluding small categories
    grouped_no_rare = compute_category_magnitudes(
        sample_numeric_df,
        category_col="main_category",
        metric_cols=["price", "discount"],
        exclude_small=True,
    )
    assert "Rare" not in grouped_no_rare.index


def test_compute_correlations(sample_numeric_df):
    spearman_corr = compute_correlations(
        sample_numeric_df, ["price", "discount"], method="spearman"
    )
    assert spearman_corr.shape == (2, 2)
    assert spearman_corr.loc["price", "price"] == pytest.approx(1.0)
    # Price and discount increase monotonically in this fixture
    assert spearman_corr.loc["price", "discount"] > 0.9
