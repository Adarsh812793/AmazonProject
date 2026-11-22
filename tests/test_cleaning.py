import pandas as pd

from amazon_project.cleaning import (
    add_review_count,
    clean_data,
    convert_numeric_columns,
    drop_duplicate_products,
    split_category,
    strip_whitespace,
)
from amazon_project.loading import load_processed, save_processed


def _raw_sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "discounted_price": ["₹399", "₹1,099"],
            "actual_price": ["₹1,099", "₹21,990"],
            "discount_percentage": ["64%", "95%"],
            "rating": ["4.2", "|"],
            "rating_count": ["24,269", ""],
        }
    )


def test_prices_and_discount_become_floats():
    out = convert_numeric_columns(_raw_sample())
    assert out["discounted_price"].tolist() == [399.0, 1099.0]
    assert out["actual_price"].tolist() == [1099.0, 21990.0]
    assert out["discount_percentage"].tolist() == [64.0, 95.0]


def test_invalid_rating_becomes_missing():
    out = convert_numeric_columns(_raw_sample())
    assert out["rating"].iloc[0] == 4.2
    assert pd.isna(out["rating"].iloc[1])


def test_rating_count_is_nullable_integer():
    out = convert_numeric_columns(_raw_sample())
    assert str(out["rating_count"].dtype) == "Int64"
    assert out["rating_count"].iloc[0] == 24269
    assert pd.isna(out["rating_count"].iloc[1])


def test_input_is_not_modified():
    raw = _raw_sample()
    convert_numeric_columns(raw)
    assert raw["actual_price"].iloc[0] == "₹1,099"


def test_dedup_keeps_highest_rating_count_in_original_order():
    df = pd.DataFrame(
        {
            "product_id": ["A", "B", "A", "C", "C"],
            "rating_count": pd.array([10, 5, 12, pd.NA, 7], dtype="Int64"),
        }
    )
    out = drop_duplicate_products(df)
    assert out["product_id"].tolist() == ["B", "A", "C"]
    assert out["rating_count"].tolist() == [5, 12, 7]


def test_dedup_missing_count_loses_to_real_count_and_ties_keep_first():
    df = pd.DataFrame(
        {
            "product_id": ["A", "A", "B", "B"],
            "rating_count": pd.array([pd.NA, 3, 4, 4], dtype="Int64"),
            "note": ["x", "y", "first", "second"],
        }
    )
    out = drop_duplicate_products(df)
    assert out["note"].tolist() == ["y", "first"]


def test_split_category_levels_and_small_flag():
    df = pd.DataFrame(
        {
            "category": [
                "Electronics|Mobiles|Cables",
                "Electronics|Audio",
                "Toys&Games|Puzzles",
            ]
        }
    )
    out = split_category(df, small_threshold=2)
    assert out["main_category"].tolist() == ["Electronics", "Electronics", "Toys&Games"]
    assert out["sub_category"].tolist() == ["Mobiles", "Audio", "Puzzles"]
    assert out["leaf_category"].tolist() == ["Cables", "Audio", "Puzzles"]
    assert out["is_small_category"].tolist() == [False, False, True]


def test_add_review_count_uses_review_ids():
    df = pd.DataFrame({"review_id": ["R1,R2,R3", "R9"]})
    assert add_review_count(df)["n_reviews"].tolist() == [3, 1]


def test_strip_whitespace_only_touches_text():
    df = pd.DataFrame({"name": ["  a ", "b"], "price": [1.0, 2.0]})
    out = strip_whitespace(df)
    assert out["name"].tolist() == ["a", "b"]
    assert out["price"].tolist() == [1.0, 2.0]


def test_clean_data_end_to_end_and_csv_round_trip(tmp_path):
    raw = pd.DataFrame(
        {
            "product_id": ["A", "A", "B"],
            "category": ["Electronics|Cables", "Electronics|Cables", "Toys|Games"],
            "discounted_price": ["₹100", "₹100", "₹50"],
            "actual_price": ["₹200", "₹200", "₹50"],
            "discount_percentage": ["50%", "50%", "0%"],
            "rating": ["4.0", "4.0", "|"],
            "rating_count": ["1,000", "1,001", ""],
            "review_id": ["R1,R2", "R1,R2", "R3"],
        }
    )
    clean = clean_data(raw)
    assert clean["product_id"].tolist() == ["A", "B"]
    assert clean["rating_count"].iloc[0] == 1001
    assert clean["n_reviews"].tolist() == [2, 1]

    path = save_processed(clean, tmp_path / "clean.csv")
    back = load_processed(path)
    assert str(back["rating_count"].dtype) == "Int64"
    assert pd.isna(back["rating_count"].iloc[1])
    assert back["is_small_category"].dtype == bool
    assert pd.isna(back["rating"].iloc[1])
