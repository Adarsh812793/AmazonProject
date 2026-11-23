"""Exploratory Data Analysis (EDA) functions for the Amazon dataset.

This module provides functions to calculate the statistical magnitudes of the
data: central tendency (mean, median), dispersion (standard deviation, IQR),
shape (skewness, kurtosis), outlier detection, category-level comparisons,
and correlation analysis.
"""

from typing import Literal

import numpy as np
import pandas as pd


def compute_univariate_magnitudes(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Compute the full set of summary magnitudes for numeric columns.

    Magnitudes computed per column:
    - count: valid non-null records
    - missing: number of missing (NaN) values
    - mean: arithmetic average
    - std: sample standard deviation (spread)
    - min: lowest value
    - q25: 25th percentile (1st quartile)
    - median: 50th percentile (robust midpoint)
    - q75: 75th percentile (3rd quartile)
    - max: highest value
    - iqr: interquartile range (q75 - q25)
    - skew: skewness (magnitude and direction of asymmetry)
    - kurtosis: Fisher-Pearson kurtosis (tail heaviness)

    Args:
        df: Input DataFrame.
        columns: List of numeric column names to analyze.

    Returns:
        DataFrame indexed by column name with each magnitude as a column.
    """
    records = []
    for col in columns:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) == 0:
            continue

        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr = q75 - q25

        records.append(
            {
                "column": col,
                "count": int(series.count()),
                "missing": int(df[col].isna().sum()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "q25": q25,
                "median": float(series.median()),
                "q75": q75,
                "max": float(series.max()),
                "iqr": iqr,
                "skew": float(series.skew()),
                "kurtosis": float(series.kurtosis()),
            }
        )

    return pd.DataFrame(records).set_index("column")


def detect_iqr_outliers(
    series: pd.Series, multiplier: float = 1.5
) -> tuple[float, float, pd.Series]:
    """Calculate Tukey's IQR fences and identify outlier rows.

    Formula:
        lower_bound = Q1 - (multiplier * IQR)
        upper_bound = Q3 + (multiplier * IQR)

    Args:
        series: Numeric pandas Series.
        multiplier: IQR multiplier (default 1.5 for standard outliers, 3.0 for extreme).

    Returns:
        tuple containing (lower_bound, upper_bound, boolean_mask_of_outliers).
    """
    clean_series = pd.to_numeric(series, errors="coerce")
    q25 = clean_series.quantile(0.25)
    q75 = clean_series.quantile(0.75)
    iqr = q75 - q25

    lower_bound = float(q25 - (multiplier * iqr))
    upper_bound = float(q75 + (multiplier * iqr))

    is_outlier = (clean_series < lower_bound) | (clean_series > upper_bound)
    return lower_bound, upper_bound, is_outlier


def summarize_outliers(
    df: pd.DataFrame, columns: list[str], multiplier: float = 1.5
) -> pd.DataFrame:
    """Summarize the magnitude and frequency of outliers for numeric columns.

    Args:
        df: Input DataFrame.
        columns: List of column names to evaluate.
        multiplier: IQR multiplier (default 1.5).

    Returns:
        DataFrame with columns: lower_bound, upper_bound, outlier_count,
        outlier_pct, min_outlier, max_outlier.
    """
    records = []
    for col in columns:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) == 0:
            continue

        lower, upper, mask = detect_iqr_outliers(series, multiplier=multiplier)
        outliers = series[mask]
        n_outliers = len(outliers)
        pct_outliers = (n_outliers / len(series)) * 100.0

        records.append(
            {
                "column": col,
                "lower_bound": lower,
                "upper_bound": upper,
                "outlier_count": n_outliers,
                "outlier_pct": round(pct_outliers, 2),
                "min_outlier": float(outliers.min()) if n_outliers > 0 else np.nan,
                "max_outlier": float(outliers.max()) if n_outliers > 0 else np.nan,
            }
        )

    return pd.DataFrame(records).set_index("column")


def compute_category_magnitudes(
    df: pd.DataFrame,
    category_col: str = "main_category",
    metric_cols: list[str] | None = None,
    exclude_small: bool = False,
) -> pd.DataFrame:
    """Compute central tendency and spread magnitudes grouped by category.

    Args:
        df: Input DataFrame.
        category_col: Categorical column to group by.
        metric_cols: Numeric columns to aggregate. Defaults to price, discount,
                     rating, and rating_count.
        exclude_small: If True and 'is_small_category' is present, filters out
                       rare categories to ensure robust statistics.

    Returns:
        DataFrame with multi-level columns containing count, median, mean,
        and IQR for each metric per category.
    """
    if metric_cols is None:
        metric_cols = [
            "discounted_price",
            "actual_price",
            "discount_percentage",
            "rating",
            "rating_count",
        ]

    data = df.copy()
    if exclude_small and "is_small_category" in data.columns:
        data = data[~data["is_small_category"]]

    def _iqr(s: pd.Series) -> float:
        clean = s.dropna()
        return float(clean.quantile(0.75) - clean.quantile(0.25))

    agg_dict = {
        col: [
            ("count", "count"),
            ("median", "median"),
            ("mean", "mean"),
            ("iqr", _iqr),
        ]
        for col in metric_cols
        if col in data.columns
    }

    return data.groupby(category_col).agg(agg_dict)


def compute_correlations(
    df: pd.DataFrame,
    columns: list[str],
    method: Literal["pearson", "spearman"] = "spearman",
) -> pd.DataFrame:
    """Compute correlation matrix for selected numeric features.

    Spearman is default because prices, discounts, and review counts are
    often heavily skewed and contain outliers; rank correlation provides
    a robust measure of monotonic relationship.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to correlate.
        method: 'spearman' (rank-based) or 'pearson' (linear).

    Returns:
        Square correlation matrix DataFrame.
    """
    numeric_df = df[columns].apply(pd.to_numeric, errors="coerce")
    return numeric_df.corr(method=method)
