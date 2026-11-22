"""Load the raw Amazon dataset.

This module only *reads* data. It never cleans or modifies it; cleaning is
done in a later stage and written to data/processed/.
"""

from pathlib import Path

import pandas as pd

# Project root = three levels up from this file:
# <root>/src/amazon_project/loading.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "amazon.csv"


def load_raw(path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    """Read the raw CSV exactly as stored, with every column as text.

    Args:
        path: Location of the CSV. Defaults to ``data/raw/amazon.csv``.

    Returns:
        A DataFrame with one row per CSV row and all columns as strings.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Raw data file not found: {path}. "
            "Download amazon.csv from Kaggle and save it there (see README)."
        )
    # encoding="utf-8": the file contains the rupee sign, which needs UTF-8.
    # dtype=str: keep values like "₹1,099" and "64%" untouched. Converting
    # them to numbers is a cleaning step, so it belongs to Stage 3.
    # keep_default_na=False: do not silently turn text into NaN; we want to
    # see the file exactly as it is and decide about missing values later.
    return pd.read_csv(path, encoding="utf-8", dtype=str, keep_default_na=False)
