# Amazon Product Analysis

Exploratory data analysis of Amazon product pricing, discounts, ratings and customer feedback.

## Objective
Analyse Amazon product data to find patterns in product categories, pricing, discounts, customer ratings and reviews.

> The dataset contains **no sales or revenue data**, so the analysis makes no sales claims.

## Tech stack
Python 3.13 · pandas · NumPy · Matplotlib · Seaborn · Jupyter Notebook · pytest · Ruff

## Dataset
`amazon.csv` — 1,465 rows × 16 columns (product details, prices in ₹, discount %, rating, rating count, and packed review text). The file is not committed to git. Place it at `data/raw/amazon.csv` (done in Stage 2). Full column descriptions and known data-quality issues are in [CLAUDE.md](CLAUDE.md).

## Workflow
1. Project Setup — done
2. Data Acquisition
3. Data Preparation and Cleaning
4. Exploratory Data Analysis
5. Data Visualization
6. Findings and Conclusion
7. Final Demonstration and Report

Each stage is completed and approved before the next begins.

## Getting started
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Then:
```
pytest              # run tests
ruff check .        # lint
ruff format .       # format
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
