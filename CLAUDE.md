# CLAUDE.md

## Project overview
**Amazon Product Analysis** — exploratory data analysis (EDA) of pricing, discounts, ratings and customer feedback.

**Objective:** analyse Amazon product data to find patterns in product categories, pricing, discounts, customer ratings and reviews.

**Scope note:** the dataset has NO sales or revenue data. Do not make or imply sales/revenue claims.

**Stack:** Python 3.13, pandas, NumPy, Matplotlib, Seaborn, Jupyter; pytest and Ruff for tests and code quality.

## Workflow (strict)
1. Project Setup
2. Data Acquisition
3. Data Preparation and Cleaning
4. Exploratory Data Analysis
5. Data Visualization
6. Findings and Conclusion
7. Final Demonstration and Report

Rules of engagement:
- Complete one stage at a time. **Never start the next stage without the user's explicit approval.**
- The user is learning: explain concepts and code as you implement.
- Keep things simple; avoid unnecessary complexity or abstraction.
- Keep documentation (README, this file, docstrings) current at every stage.

Status: Stages 1, 2, 3, and 4 merged. Stage 5 (Data Visualization) done on branch `stage-5-visualization`, awaiting PR and merge into `main`.

Git workflow: one branch per stage (`stage-N-topic`); commit there and push; the user opens and merges the PR. Do not install `gh` or open/merge PRs.

## Structure
- `data/raw/` — original, immutable source data (never edit in place)
- `data/processed/` — cleaned/derived datasets (reproducible from raw)
- `data/external/` — third-party reference data
- `notebooks/` — exploratory analysis; name as `NN_topic.ipynb`
- `src/amazon_project/` — reusable code (loading, cleaning, features, analysis, plotting)
- `tests/` — pytest tests mirroring `src/`
- `reports/figures/` — generated charts and outputs

## Setup
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .      # makes `import amazon_project` work in tests and notebooks
```

## Commands
- Tests: `pytest`
- Lint/format: `ruff check .` / `ruff format .`

## Conventions
- Python 3.13, type hints on public functions, pandas for tabular work.
- Put reusable logic in `src/`, not notebooks; notebooks import from the package.
- Raw data is read-only; all transformations produce files in `data/processed/`.
- Data files are git-ignored; document sources and download steps instead of committing data.
- Keep notebooks' outputs cleared before committing.
- Use fixed random seeds for reproducibility.
- Windows console is cp1252: run scripts with `python -X utf8` when printing `₹`.

## Data
File: `amazon.csv` (~4.7 MB, UTF-8). Source: Kaggle. Stored at `data/raw/amazon.csv` (read-only, git-ignored). SHA-256 `4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77`. Loaded with `amazon_project.loading.load_raw()`, which reads everything as UTF-8 text with no conversion; missing values therefore appear as empty strings, not NaN (Stage 3 decides how to treat them).

**Shape:** 1,465 rows × 16 columns. Each row is a product paired with its reviews (not a transaction).

| Column | Content | Loaded as | Notes |
|---|---|---|---|
| product_id | Amazon ASIN | text | 114 repeated IDs |
| product_name | Product title | text | |
| category | Pipe-delimited hierarchy, e.g. `Computers&Accessories\|Accessories&Peripherals\|...` | text | 211 distinct paths; top level has 9 values |
| discounted_price | Sale price, e.g. `₹399` | text | needs ₹/comma removal → numeric |
| actual_price | List price, e.g. `₹1,099` | text | needs ₹/comma removal → numeric |
| discount_percentage | e.g. `64%` | text | needs % removal → numeric |
| rating | Average rating, e.g. `4.2` | text | numeric after cleaning |
| rating_count | Number of ratings, e.g. `24,269` | text | needs comma removal → integer |
| about_product | Product description | text | |
| user_id | Reviewer IDs | text | comma-separated list of many users per row |
| user_name | Reviewer names | text | comma-separated list |
| review_id | Review IDs | text | comma-separated list |
| review_title | Review titles | text | comma-separated list |
| review_content | Review texts | text | comma-separated list |
| img_link | Image URL | text | |
| product_link | Product page URL | text | |

## Cleaned data (Stage 3)
`data/processed/amazon_clean.csv` (git-ignored): 1,351 rows (one per `product_id`) × 21 columns. Built by `amazon_project.cleaning.clean_data(load_raw())`, saved/loaded with `save_processed()` / `load_processed()` (which restores dtypes lost in CSV). Decisions made:
- Price/discount/rating/count columns are numeric (`rating_count` is nullable `Int64`). Missing values stay NaN, never imputed: `rating` 1 missing, `rating_count` 2 missing.
- Dedup: repeated `product_id`s are the same product scraped from different search pages; keep the row with the highest `rating_count` (ties: first).
- New columns: `main_category`, `sub_category`, `leaf_category`, `is_small_category` (main category with <5 products: 7 products), `n_reviews` (from `review_id`).
- Review text columns (`review_title`, `review_content`, `user_name`) remain raw comma-packed text; only IDs split safely. Text analysis is deferred.
- Validation: no price/rating/discount inconsistencies; outliers deliberately kept for Stage 4.
- Main categories after dedup: Electronics 490, Home&Kitchen 448, Computers&Accessories 375, OfficeProducts 31, others ≤2.

**Original raw-data quirks (all handled in Stage 3):**
- All columns load as text (pandas 3 `str`); price, discount, rating and count columns need conversion.
- Currency is Indian rupees (₹).
- Missing values: `rating_count` has 2 nulls (`B0B94JPY2N`, `B0BQRJ3C47`); no other nulls.
- `rating` has one invalid value: `|` (should be treated as missing).
- No fully duplicate rows, but 114 duplicate `product_id`s (same product listed more than once) — decide on a dedup rule in Stage 3.
- Review columns pack several reviews into one comma-separated cell, so each row is NOT one review; splitting needs care because review text itself contains commas.
- Category mix is skewed: Electronics 526, Computers&Accessories 453, Home&Kitchen 448, OfficeProducts 31, and 5 categories with ≤2 rows each — treat tiny categories carefully in comparisons.
- No sales, revenue, date, or quantity columns.

## Exploratory Data Analysis (Stage 4)
Walkthrough in `notebooks/03_exploratory_data_analysis.ipynb`; reusable functions in `src/amazon_project/analysis.py`.
- **Univariate Magnitudes:**
  - `discounted_price`: Median ₹799, Mean ₹3,125, IQR ₹1,460, Skew +4.30 (heavy right tail up to ₹77,990).
  - `actual_price`: Median ₹1,650, Mean ₹5,448, IQR ₹3,410, Skew +4.43 (max ₹139,900).
  - `discount_percentage`: Median 60.0%, Mean 56.4%, IQR 38.0%, Skew -0.24 (roughly symmetric).
  - `rating`: Median 4.10, Mean 4.09, IQR 0.40, Skew -1.23 (clustered between 4.0 and 4.3).
  - `rating_count`: Median 5,170, Mean 18,295, Skew +5.69, Kurtosis 40.24 (extreme long-tail up to 426,973).
- **Outliers:** Evaluated via Tukey's 1.5 × IQR fences; 114 price outliers and 124 rating count outliers identified and kept for Stage 5 visualization.
- **Category Comparison:** Electronics has the largest price spread (IQR ₹7,600, median ₹1,384); OfficeProducts offers low median discounts (5%) and lowest median price (₹178), but highest median rating (4.3).
- **Correlations (Spearman Rank):**
  - Price vs Rating: +0.077 (no relationship).
  - Discount % vs Rating: -0.147 (very weak negative correlation).
  - Discount % vs Discounted Price: -0.367 (cheaper items have moderately higher discount percentages).

## Data Visualization (Stage 5)
Walkthrough in `notebooks/04_data_visualization.ipynb`; reusable plotting routines in `src/amazon_project/visualization.py`. Exported charts saved to `reports/figures/`.
- `01_price_distributions.png`: Raw right-skewed prices vs log10 transformation.
- `02_discount_and_rating_distributions.png`: Symmetric discount percentages (median 60%) and left-skewed, concentrated customer ratings (4.0–4.3).
- `03_outlier_boxplots.png`: Log-scale boxplots showing Tukey 1.5×IQR fences and luxury/viral outliers.
- `04_category_comparisons.png`: Comparative boxplots of pricing, discounts, and ratings across major categories.
- `05_correlation_heatmap.png`: Spearman rank correlation heatmap.
- `06_bivariate_relationships.png`: Scatter plots for Discount % vs Price and Rating vs Price.
