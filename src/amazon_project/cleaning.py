"""Clean the raw Amazon dataset.

Each function takes a DataFrame and returns a *new* one; the input is never
modified. This keeps raw data safe and makes each step easy to test.
"""

import pandas as pd


def _to_number(series: pd.Series, remove: str) -> pd.Series:
    """Strip unwanted characters from text, then convert to a float.

    Args:
        series: Text values such as ``"₹1,099"``.
        remove: Regex of characters to delete, e.g. ``"[₹,]"``.

    Returns:
        Floats. Anything that is still not a valid number (an empty string
        or a stray symbol such as ``"|"``) becomes NaN instead of raising,
        because ``errors="coerce"`` turns bad values into missing ones.
    """
    stripped = series.str.replace(remove, "", regex=True).str.strip()
    return pd.to_numeric(stripped, errors="coerce")


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the price, discount, rating and count text columns into numbers.

    - discounted_price, actual_price: remove ``₹`` and commas -> float
    - discount_percentage: remove ``%`` -> number (64% becomes 64; pandas keeps
      it as an integer because every value is a whole number)
    - rating: -> float; the invalid ``"|"`` becomes NaN
    - rating_count: remove commas -> nullable integer (``Int64``), so the
      missing values stay missing instead of forcing the column to float.
    """
    out = df.copy()
    for col in ["discounted_price", "actual_price"]:
        out[col] = _to_number(out[col], "[₹,]")
    out["discount_percentage"] = _to_number(out["discount_percentage"], "%")
    out["rating"] = _to_number(out["rating"], "")
    out["rating_count"] = _to_number(out["rating_count"], ",").astype("Int64")
    return out


def drop_duplicate_products(df: pd.DataFrame) -> pd.DataFrame:
    """Keep one row per ``product_id``: the one with the highest rating_count.

    The same product appears several times because it was scraped from
    different search-result pages. Counting it more than once would bias
    averages and category counts. Rows with a missing rating_count are
    ranked last; ties keep the row that appears first in the file.
    """
    ordered = df.sort_values(
        "rating_count", ascending=False, na_position="last", kind="stable"
    )
    deduped = ordered.drop_duplicates(subset="product_id", keep="first")
    # Restore the original file order so results stay easy to compare to raw.
    return deduped.sort_index()


def split_category(df: pd.DataFrame, small_threshold: int = 5) -> pd.DataFrame:
    """Split the pipe-delimited ``category`` path into separate columns.

    A path looks like ``Electronics|Mobiles&Accessories|...|Cables``. Adds:

    - main_category: first level (9 distinct values)
    - sub_category: second level (every path has at least two levels)
    - leaf_category: the last, most specific level
    - is_small_category: True when the main category has fewer than
      ``small_threshold`` products, so later comparisons can treat it with care

    The original ``category`` column is kept.
    """
    out = df.copy()
    parts = out["category"].str.split("|")
    out["main_category"] = parts.str[0]
    out["sub_category"] = parts.str[1]
    out["leaf_category"] = parts.str[-1]
    counts = out["main_category"].map(out["main_category"].value_counts())
    out["is_small_category"] = counts < small_threshold
    return out


def add_review_count(df: pd.DataFrame) -> pd.DataFrame:
    """Add ``n_reviews``: how many reviews are packed into each row.

    Counted from ``review_id`` because review IDs never contain commas, so
    splitting on commas is safe there (unlike titles and review text). The
    review text columns are left untouched for now.
    """
    out = df.copy()
    out["n_reviews"] = out["review_id"].str.count(",") + 1
    return out


def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Remove leading/trailing spaces from every text column."""
    out = df.copy()
    for col in out.select_dtypes(include=["object", "string"]).columns:
        out[col] = out[col].str.strip()
    return out


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Run every cleaning step in order and return the cleaned DataFrame.

    Order matters: whitespace is trimmed and numbers converted first, then
    duplicates are dropped (they need numeric rating_count), and only then
    are category sizes counted, so duplicates cannot inflate them.
    """
    df = strip_whitespace(raw)
    df = convert_numeric_columns(df)
    df = drop_duplicate_products(df)
    df = split_category(df)
    df = add_review_count(df)
    return df.reset_index(drop=True)
