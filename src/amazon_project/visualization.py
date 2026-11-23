"""Data visualization module for the Amazon product analysis project.

This module provides functions to create presentation-ready charts illustrating
statistical distributions, outlier fences, category comparisons, and correlations
using Matplotlib and Seaborn.
"""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURES_PATH = PROJECT_ROOT / "reports" / "figures"


def set_presentation_style() -> None:
    """Set global Matplotlib and Seaborn styling for presentation-quality figures."""
    sns.set_theme(
        style="whitegrid",
        font="sans-serif",
        palette="tab10",
        rc={
            "figure.titlesize": 14,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "figure.autolayout": False,
        },
    )


def save_figure(
    fig: plt.Figure,
    filename: str,
    output_dir: Path | str = FIGURES_PATH,
    dpi: int = 300,
) -> Path:
    """Save a Matplotlib figure to the reports/figures directory.

    Args:
        fig: The Figure object to save.
        filename: Destination filename (e.g., 'price_distribution.png').
        output_dir: Directory path. Defaults to reports/figures/.
        dpi: Dots per inch resolution. Defaults to 300 (print quality).

    Returns:
        Path to the saved figure file.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    destination = output_path / filename
    fig.savefig(destination, dpi=dpi, bbox_inches="tight")
    return destination


def plot_price_distributions(df: pd.DataFrame) -> plt.Figure:
    """Plot raw and log-scaled distributions of discounted price.

    Shows the severe right skew of product prices alongside the log10
    transformation that reveals the underlying log-normal spread.

    Args:
        df: Processed DataFrame containing 'discounted_price'.

    Returns:
        The generated Matplotlib Figure.
    """
    prices = df["discounted_price"].dropna()
    median_val = float(prices.median())
    mean_val = float(prices.mean())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # 1. Raw price distribution
    sns.histplot(prices, kde=True, ax=ax1, color="#2b5c8f", bins=40)
    ax1.axvline(
        median_val,
        color="#d95f02",
        linestyle="--",
        linewidth=2,
        label=f"Median: ₹{median_val:,.0f}",
    )
    ax1.axvline(
        mean_val,
        color="#e7298a",
        linestyle=":",
        linewidth=2,
        label=f"Mean: ₹{mean_val:,.0f}",
    )
    ax1.set_title("Raw Discounted Price (Skew: +4.30)")
    ax1.set_xlabel("Discounted Price (₹)")
    ax1.set_ylabel("Product Count")
    ax1.legend()

    # 2. Log-scaled price distribution
    log_prices = np.log10(prices[prices > 0])
    sns.histplot(log_prices, kde=True, ax=ax2, color="#1b9e77", bins=30)
    ax2.axvline(
        np.log10(median_val),
        color="#d95f02",
        linestyle="--",
        linewidth=2,
        label=f"Median (₹{median_val:,.0f})",
    )
    ax2.set_title("Log10 Transformed Price (Reveals Spread)")
    ax2.set_xlabel("log10(Discounted Price)")
    ax2.set_ylabel("Product Count")
    ax2.legend()

    fig.suptitle("Amazon Product Pricing Distributions", fontsize=14, y=1.02)
    plt.tight_layout()
    return fig


def plot_rating_and_discount_distributions(df: pd.DataFrame) -> plt.Figure:
    """Plot univariate distributions for discount percentage and customer rating.

    Args:
        df: Processed DataFrame containing 'discount_percentage' and 'rating'.

    Returns:
        The generated Matplotlib Figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # 1. Discount Percentage
    discounts = df["discount_percentage"].dropna()
    d_median = float(discounts.median())
    d_mean = float(discounts.mean())

    sns.histplot(discounts, kde=True, ax=ax1, color="#7570b3", bins=25)
    ax1.axvline(
        d_median,
        color="#d95f02",
        linestyle="--",
        linewidth=2,
        label=f"Median: {d_median:.1f}%",
    )
    ax1.axvline(
        d_mean,
        color="#e7298a",
        linestyle=":",
        linewidth=2,
        label=f"Mean: {d_mean:.1f}%",
    )
    ax1.set_title("Discount Percentage (Symmetric Spread)")
    ax1.set_xlabel("Discount Percentage (%)")
    ax1.set_ylabel("Product Count")
    ax1.legend()

    # 2. Rating Distribution
    ratings = df["rating"].dropna()
    r_median = float(ratings.median())
    r_mean = float(ratings.mean())

    sns.histplot(ratings, kde=True, ax=ax2, color="#e6ab02", binwidth=0.1)
    ax2.axvline(
        r_median,
        color="#d95f02",
        linestyle="--",
        linewidth=2,
        label=f"Median: {r_median:.2f}",
    )
    ax2.axvline(
        r_mean,
        color="#e7298a",
        linestyle=":",
        linewidth=2,
        label=f"Mean: {r_mean:.2f}",
    )
    ax2.set_title("Customer Rating (Left-skewed, Clustered at 4.0-4.3)")
    ax2.set_xlabel("Average Rating (Stars)")
    ax2.set_ylabel("Product Count")
    ax2.legend()

    fig.suptitle("Promotional Discounts & Rating Distributions", fontsize=14, y=1.02)
    plt.tight_layout()
    return fig


def plot_outlier_boxplots(df: pd.DataFrame) -> plt.Figure:
    """Plot box plots showing Tukey 1.5x IQR fences and outliers for price and reviews.

    Args:
        df: Processed DataFrame with 'discounted_price' and 'rating_count'.

    Returns:
        The generated Matplotlib Figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # 1. Price Boxplot (log scale for visibility)
    prices = df["discounted_price"].dropna()
    sns.boxplot(
        x=prices,
        ax=ax1,
        color="#6baed6",
        fliersize=4,
        flierprops={"markerfacecolor": "#e6550d", "alpha": 0.6},
    )
    ax1.set_xscale("log")
    ax1.set_title("Discounted Price with Outliers (Log Scale)")
    ax1.set_xlabel("Price in ₹ (Logarithmic Axis)")

    # 2. Rating Count Boxplot (log scale for visibility)
    counts = df["rating_count"].dropna().astype(float)
    sns.boxplot(
        x=counts,
        ax=ax2,
        color="#74c476",
        fliersize=4,
        flierprops={"markerfacecolor": "#de2d26", "alpha": 0.6},
    )
    ax2.set_xscale("log")
    ax2.set_title("Rating Count with Outliers (Log Scale)")
    ax2.set_xlabel("Number of Ratings (Logarithmic Axis)")

    fig.suptitle("Distribution Spread and Outlier Identification", fontsize=14, y=1.02)
    plt.tight_layout()
    return fig


def plot_category_comparisons(df: pd.DataFrame) -> plt.Figure:
    """Plot category-level comparisons for major product categories.

    Excludes small categories (<5 products) to focus on the 4 primary categories.

    Args:
        df: Processed DataFrame containing 'main_category', 'is_small_category',
            'discounted_price', 'discount_percentage', and 'rating'.

    Returns:
        The generated Matplotlib Figure.
    """
    major_df = df[~df["is_small_category"]].copy()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # 1. Price comparison across categories (log scale)
    sns.boxplot(
        data=major_df,
        x="main_category",
        y="discounted_price",
        hue="main_category",
        legend=False,
        ax=axes[0],
        palette="Set2",
    )
    axes[0].set_yscale("log")
    axes[0].set_title("Price Distribution by Category")
    axes[0].set_xlabel("Category")
    axes[0].set_ylabel("Discounted Price (₹, Log Scale)")
    axes[0].tick_params(axis="x", rotation=30)

    # 2. Discount percentage comparison
    sns.boxplot(
        data=major_df,
        x="main_category",
        y="discount_percentage",
        hue="main_category",
        legend=False,
        ax=axes[1],
        palette="Set2",
    )
    axes[1].set_title("Discount % by Category")
    axes[1].set_xlabel("Category")
    axes[1].set_ylabel("Discount (%)")
    axes[1].tick_params(axis="x", rotation=30)

    # 3. Rating comparison
    sns.boxplot(
        data=major_df,
        x="main_category",
        y="rating",
        hue="main_category",
        legend=False,
        ax=axes[2],
        palette="Set2",
    )
    axes[2].set_title("Rating by Category")
    axes[2].set_xlabel("Category")
    axes[2].set_ylabel("Rating (Stars)")
    axes[2].tick_params(axis="x", rotation=30)

    fig.suptitle(
        "Cross-Category Analysis across Major Product Segments", fontsize=14, y=1.02
    )
    plt.tight_layout()
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    method: str = "spearman",
) -> plt.Figure:
    """Plot a correlation heatmap across numeric attributes.

    Args:
        df: Processed DataFrame.
        columns: List of columns to correlate. Defaults to price, discount,
            rating, and count.
        method: Correlation method ('spearman' or 'pearson'). Default 'spearman'.

    Returns:
        The generated Matplotlib Figure.
    """
    if columns is None:
        columns = [
            "discounted_price",
            "actual_price",
            "discount_percentage",
            "rating",
            "rating_count",
            "n_reviews",
        ]

    numeric_df = df[columns].apply(pd.to_numeric, errors="coerce")
    corr = numeric_df.corr(method=method)

    fig, ax = plt.subplots(figsize=(8, 6))
    mask = np.triu(np.ones_like(corr, dtype=bool))

    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt=".3f",
        cmap="vlag",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={
            "shrink": 0.8,
            "label": f"{method.capitalize()} Correlation Coefficient",
        },
        ax=ax,
    )

    ax.set_title(f"{method.capitalize()} Rank Correlation Matrix", fontsize=13, pad=15)
    plt.tight_layout()
    return fig


def plot_bivariate_relationships(df: pd.DataFrame) -> plt.Figure:
    """Plot key bivariate relationships: Discount vs Price and Price vs Rating.

    Args:
        df: Processed DataFrame.

    Returns:
        The generated Matplotlib Figure.
    """
    major_df = df[~df["is_small_category"]].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 1. Discount % vs Discounted Price (log scale)
    sns.scatterplot(
        data=major_df,
        x="discounted_price",
        y="discount_percentage",
        hue="main_category",
        alpha=0.6,
        ax=ax1,
        palette="tab10",
    )
    ax1.set_xscale("log")
    ax1.set_title("Discount % vs Price (r = -0.367)")
    ax1.set_xlabel("Discounted Price (₹, Log Scale)")
    ax1.set_ylabel("Discount Percentage (%)")
    ax1.legend(loc="upper right", fontsize=8)

    # 2. Rating vs Discounted Price (log scale)
    sns.scatterplot(
        data=major_df,
        x="discounted_price",
        y="rating",
        hue="main_category",
        alpha=0.6,
        ax=ax2,
        palette="tab10",
    )
    ax2.set_xscale("log")
    ax2.set_title("Rating vs Price (r = +0.077, No Relationship)")
    ax2.set_xlabel("Discounted Price (₹, Log Scale)")
    ax2.set_ylabel("Rating (Stars)")
    ax2.legend(loc="lower right", fontsize=8)

    fig.suptitle(
        "Bivariate Relationships: Pricing, Discounts, and Ratings",
        fontsize=14,
        y=1.02,
    )
    plt.tight_layout()
    return fig


def generate_all_figures(
    df: pd.DataFrame, output_dir: Path | str = FIGURES_PATH
) -> dict[str, Path]:
    """Generate and save the entire standard suite of presentation figures.

    Args:
        df: Processed DataFrame.
        output_dir: Output directory for image files.

    Returns:
        Dictionary mapping figure names to saved file paths.
    """
    set_presentation_style()
    output_dir = Path(output_dir)

    generators: dict[str, Any] = {
        "01_price_distributions.png": plot_price_distributions,
        "02_discount_and_rating_distributions.png": plot_rating_and_discount_distributions,
        "03_outlier_boxplots.png": plot_outlier_boxplots,
        "04_category_comparisons.png": plot_category_comparisons,
        "05_correlation_heatmap.png": plot_correlation_heatmap,
        "06_bivariate_relationships.png": plot_bivariate_relationships,
    }

    saved_files: dict[str, Path] = {}
    for filename, func in generators.items():
        fig = func(df)
        path = save_figure(fig, filename, output_dir=output_dir)
        plt.close(fig)
        saved_files[filename] = path

    return saved_files
