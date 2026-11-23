from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from amazon_project.visualization import (
    generate_all_figures,
    plot_bivariate_relationships,
    plot_category_comparisons,
    plot_correlation_heatmap,
    plot_outlier_boxplots,
    plot_price_distributions,
    plot_rating_and_discount_distributions,
    save_figure,
    set_presentation_style,
)


@pytest.fixture
def sample_viz_df() -> pd.DataFrame:
    """Fixture providing a realistic mini dataset for visualization tests."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame(
        {
            "discounted_price": np.random.exponential(scale=1000, size=n) + 100,
            "actual_price": np.random.exponential(scale=2000, size=n) + 300,
            "discount_percentage": np.random.uniform(10, 80, size=n),
            "rating": np.random.uniform(3.0, 5.0, size=n),
            "rating_count": np.random.randint(10, 50000, size=n),
            "n_reviews": np.random.randint(1, 8, size=n),
            "main_category": np.random.choice(
                [
                    "Electronics",
                    "Home&Kitchen",
                    "Computers&Accessories",
                    "OfficeProducts",
                ],
                size=n,
            ),
            "is_small_category": [False] * n,
        }
    )


def test_set_presentation_style():
    """Ensure style application executes without exceptions."""
    set_presentation_style()


def test_save_figure(tmp_path: Path):
    """Ensure save_figure saves the image file with expected name."""
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    saved_path = save_figure(fig, "test_plot.png", output_dir=tmp_path)
    plt.close(fig)

    assert saved_path.is_file()
    assert saved_path.name == "test_plot.png"
    assert saved_path.stat().st_size > 0


def test_plot_price_distributions(sample_viz_df: pd.DataFrame):
    """Test price distribution plotting generates valid Figure with 2 subplots."""
    fig = plot_price_distributions(sample_viz_df)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_plot_rating_and_discount_distributions(sample_viz_df: pd.DataFrame):
    """Test discount and rating distribution plotting."""
    fig = plot_rating_and_discount_distributions(sample_viz_df)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_plot_outlier_boxplots(sample_viz_df: pd.DataFrame):
    """Test outlier boxplots figure structure."""
    fig = plot_outlier_boxplots(sample_viz_df)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_plot_category_comparisons(sample_viz_df: pd.DataFrame):
    """Test category comparisons figure structure."""
    fig = plot_category_comparisons(sample_viz_df)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 3
    plt.close(fig)


def test_plot_correlation_heatmap(sample_viz_df: pd.DataFrame):
    """Test correlation heatmap generation."""
    fig = plot_correlation_heatmap(sample_viz_df)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_plot_bivariate_relationships(sample_viz_df: pd.DataFrame):
    """Test bivariate scatter relationships generation."""
    fig = plot_bivariate_relationships(sample_viz_df)
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_generate_all_figures(sample_viz_df: pd.DataFrame, tmp_path: Path):
    """Test batch figure generation outputs all expected files."""
    saved_dict = generate_all_figures(sample_viz_df, output_dir=tmp_path)
    assert len(saved_dict) == 6
    for filename, path in saved_dict.items():
        assert path.is_file()
        assert path.name == filename
        assert path.stat().st_size > 0
