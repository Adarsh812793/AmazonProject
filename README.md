# Amazon Product Analysis

Exploratory data analysis of Amazon product pricing, discounts, ratings and customer feedback.

## Objective
Analyse Amazon product data to find patterns in product categories, pricing, discounts, customer ratings and reviews.

> The dataset contains **no sales or revenue data**, so the analysis makes no sales claims.

## Tech stack
Python 3.13 · pandas · NumPy · Matplotlib · Seaborn · Jupyter Notebook · pytest · Ruff

## Dataset
`amazon.csv` — 1,465 rows × 16 columns (product details, prices in ₹, discount %, rating, rating count, and packed review text). The file is not committed to git. Place it at `data/raw/amazon.csv` (done in Stage 2). Full column descriptions and known data-quality issues are in [CLAUDE.md](CLAUDE.md).

## Data acquisition
- **Source:** Kaggle (Amazon product dataset, file `amazon.csv`).
- **Download:** get `amazon.csv` from the Kaggle dataset page and save it as `data/raw/amazon.csv`. The file is git-ignored, so it is not in this repository.
- **Integrity check:** the original file has this SHA-256 checksum:
  ```
  4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77
  ```
  Verify with `certutil -hashfile data\raw\amazon.csv SHA256` (Windows) or `sha256sum data/raw/amazon.csv`.
- **Protection:** `data/raw/amazon.csv` is set read-only. Never edit it; all changes go to `data/processed/`.
  To re-set it on Windows: `attrib +R data\raw\amazon.csv`.

## Data cleaning
Run by `amazon_project.cleaning.clean_data()` (walkthrough: `notebooks/02_data_cleaning.ipynb`). Output: `data/processed/amazon_clean.csv` (git-ignored; 1,351 rows × 21 columns), read back with `amazon_project.loading.load_processed()`.

1. Trim whitespace in text columns.
2. Convert `discounted_price`, `actual_price` (remove `₹`, commas), `discount_percentage` (remove `%`), `rating`, `rating_count` (remove commas) to numbers. Unconvertible values (the `|` rating, 2 empty `rating_count`) become missing (NaN); nothing is imputed.
3. Validation found no problems: discounted price ≤ list price, ratings 2.0–5.0, stated discount matches the prices (max gap 0.5 pt, rounding). Outliers are kept for Stage 4.
4. **Duplicates:** the 114 repeated `product_id`s are the same product scraped from different search pages. Keep one row per product: the one with the highest `rating_count`.
5. Split `category` into `main_category`, `sub_category`, `leaf_category`; `is_small_category` marks main categories with fewer than 5 products.
6. **Reviews:** only `review_id`/`user_id` split safely on commas. Review text stays raw; `n_reviews` (count from `review_id`) is added. Text-level review analysis is deferred.

## Workflow
1. Project Setup — done
2. Data Acquisition — done
3. Data Preparation and Cleaning — done
4. Exploratory Data Analysis (next up)
5. Data Visualization
6. Findings and Conclusion
7. Final Demonstration and Report

Each stage is completed and approved before the next begins.

## Setup on your own computer
The data files are **not** in this repository: `data/raw/` and `data/processed/` are git-ignored. You download the raw file yourself, and the cleaned file is created by running the project's code. Follow these 5 steps in order.

**Before you start:** install **Python 3.13 or newer** and **Git**. Check your Python version with `python --version`.

### Step 1: Get the code
Download (clone) the repository and go into its folder:
```
git clone https://github.com/Adarsh812793/AmazonProject.git
cd AmazonProject
```

### Step 2: Install the project
Create a virtual environment (a private space for this project's packages), switch it on, and install everything:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```
- On Mac/Linux, switch it on with `source .venv/bin/activate` instead.
- When it's on, you'll see `(.venv)` at the start of your terminal line. Switch it on again every time you open a new terminal.
- `pip install -e .` lets the notebooks and tests use `import amazon_project`.

### Step 3: Add the raw dataset
1. Download `amazon.csv` from Kaggle.
2. Put it in the `data/raw/` folder, so its path is exactly **`data/raw/amazon.csv`**. Keep the file name `amazon.csv`.
3. *(Optional)* Check you have the right file:
   ```
   certutil -hashfile data\raw\amazon.csv SHA256
   ```
   (On Mac/Linux: `sha256sum data/raw/amazon.csv`.) It should print:
   ```
   4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77
   ```
   A different value means you have a different version of the file.

### Step 4: Create the cleaned dataset
Run this command once. It reads the raw file, cleans it, and saves the result:
```
python -X utf8 -c "from amazon_project.loading import load_raw, save_processed; from amazon_project.cleaning import clean_data; save_processed(clean_data(load_raw()))"
```
This creates `data/processed/amazon_clean.csv` (1,351 rows × 21 columns). You can also get the same file by running `notebooks/02_data_cleaning.ipynb` from top to bottom.

### Step 5: Check everything works
```
pytest
```
All tests should pass. If a test shows as **skipped**, the project couldn't find `data/raw/amazon.csv`, so go back to Step 3.

Then open the notebooks:
```
jupyter notebook
```

### Useful commands
```
pytest              # run tests
ruff check .        # check code style
ruff format .       # format code
jupyter notebook    # open notebooks
```

## Project structure
```
data/raw/            original data (read-only)
data/processed/      cleaned datasets
data/external/       third-party reference data
notebooks/           NN_topic.ipynb analysis notebooks
src/amazon_project/  reusable code
tests/               pytest tests
reports/figures/     charts and outputs
```
