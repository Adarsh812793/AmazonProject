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

Status: Stage 1 (Project Setup) complete, awaiting approval to start Stage 2 (Data Acquisition).

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
File: `amazon.csv` (~4.7 MB, UTF-8). Original copy lives outside the repo (Downloads); it is copied unchanged to `data/raw/` in Stage 2. Profiled read-only during setup (pandas default read).

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

**Known quirks / quality issues (to handle in Stage 3):**
- All columns load as text (pandas 3 `str`); price, discount, rating and count columns need conversion.
- Currency is Indian rupees (₹).
- Missing values: `rating_count` has 2 nulls (`B0B94JPY2N`, `B0BQRJ3C47`); no other nulls.
- `rating` has one invalid value: `|` (should be treated as missing).
- No fully duplicate rows, but 114 duplicate `product_id`s (same product listed more than once) — decide on a dedup rule in Stage 3.
- Review columns pack several reviews into one comma-separated cell, so each row is NOT one review; splitting needs care because review text itself contains commas.
- Category mix is skewed: Electronics 526, Computers&Accessories 453, Home&Kitchen 448, OfficeProducts 31, and 5 categories with ≤2 rows each — treat tiny categories carefully in comparisons.
- No sales, revenue, date, or quantity columns.
