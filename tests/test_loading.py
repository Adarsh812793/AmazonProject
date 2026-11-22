import pytest

from amazon_project.loading import RAW_DATA_PATH, load_raw

EXPECTED_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "discounted_price",
    "actual_price",
    "discount_percentage",
    "rating",
    "rating_count",
    "about_product",
    "user_id",
    "user_name",
    "review_id",
    "review_title",
    "review_content",
    "img_link",
    "product_link",
]


def test_load_raw_small_file_keeps_text_unchanged(tmp_path):
    """A tiny CSV is loaded as-is: values stay text, nothing is converted."""
    csv = tmp_path / "tiny.csv"
    csv.write_text('a,b\n"₹1,099",64%\n', encoding="utf-8")
    df = load_raw(csv)
    assert df.loc[0, "a"] == "₹1,099"
    assert df.loc[0, "b"] == "64%"


def test_load_raw_missing_file_raises_helpful_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="Kaggle"):
        load_raw(tmp_path / "nope.csv")


@pytest.mark.skipif(not RAW_DATA_PATH.exists(), reason="raw data not downloaded")
def test_real_dataset_shape_and_columns():
    df = load_raw()
    assert df.shape == (1465, 16)
    assert list(df.columns) == EXPECTED_COLUMNS
