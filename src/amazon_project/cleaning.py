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
