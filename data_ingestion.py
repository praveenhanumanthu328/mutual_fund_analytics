from pathlib import Path
import pandas as pd

# -------------------------------------------------
# 1. File locations
# -------------------------------------------------

RAW_DIR = Path("data/raw")

files = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}


# -------------------------------------------------
# 2. Load all 10 CSV datasets
# -------------------------------------------------

datasets = {}

print("\n" + "=" * 70)
print("MUTUAL FUND DATA INGESTION")
print("=" * 70)

for name, filename in files.items():

    file_path = RAW_DIR / filename

    try:
        df = pd.read_csv(file_path)
        datasets[name] = df

        print("\n" + "=" * 70)
        print(f"DATASET: {name}")
        print(f"FILE: {filename}")
        print("=" * 70)

        print("\nShape:")
        print(df.shape)

        print("\nData Types:")
        print(df.dtypes)

        print("\nFirst 5 Rows:")
        print(df.head())

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

    except Exception as e:
        print(f"\nERROR loading {filename}: {e}")


# -------------------------------------------------
# 3. Basic anomaly checks
# -------------------------------------------------

print("\n" + "=" * 70)
print("BASIC DATA QUALITY / ANOMALY CHECK")
print("=" * 70)

for name, df in datasets.items():

    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    print(f"\n{name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Total missing values: {missing}")
    print(f"Duplicate rows: {duplicates}")

    if missing > 0:
        print("Columns containing missing values:")
        print(df.isnull().sum()[df.isnull().sum() > 0])


# -------------------------------------------------
# 4. Explore fund master
# -------------------------------------------------

print("\n" + "=" * 70)
print("FUND MASTER EXPLORATION")
print("=" * 70)

fund_master = datasets.get("fund_master")

if fund_master is not None:

    print("\nColumns available in fund_master:")
    print(fund_master.columns.tolist())

    columns_to_explore = [
        "fund_house",
        "category",
        "sub_category",
        "risk_grade",
    ]

    for column in columns_to_explore:

        if column in fund_master.columns:
            print(f"\nUnique {column}:")
            print(fund_master[column].dropna().unique())

        else:
            print(f"\nColumn '{column}' not found.")


# -------------------------------------------------
# 5. AMFI scheme code exploration
# -------------------------------------------------

print("\n" + "=" * 70)
print("AMFI SCHEME CODE EXPLORATION")
print("=" * 70)

if fund_master is not None:

    possible_code_columns = [
        "scheme_code",
        "amfi_code",
        "scheme_id",
    ]

    code_column = None

    for column in possible_code_columns:
        if column in fund_master.columns:
            code_column = column
            break

    if code_column:

        print(f"\nAMFI code column detected: {code_column}")

        print("\nSample scheme codes:")
        print(fund_master[code_column].head(10).tolist())

        print("\nNumber of unique scheme codes:")
        print(fund_master[code_column].nunique())

    else:
        print("\nCould not automatically identify the AMFI scheme code column.")


# -------------------------------------------------
# 6. Validate AMFI codes against NAV history
# -------------------------------------------------

print("\n" + "=" * 70)
print("AMFI CODE VALIDATION")
print("=" * 70)

nav_history = datasets.get("nav_history")

if fund_master is not None and nav_history is not None:

    possible_code_columns = [
        "scheme_code",
        "amfi_code",
        "scheme_id",
    ]

    master_code = None
    nav_code = None

    for column in possible_code_columns:
        if column in fund_master.columns:
            master_code = column
            break

    for column in possible_code_columns:
        if column in nav_history.columns:
            nav_code = column
            break

    if master_code and nav_code:

        master_codes = set(
            fund_master[master_code].dropna().astype(str)
        )

        nav_codes = set(
            nav_history[nav_code].dropna().astype(str)
        )

        missing_codes = master_codes - nav_codes

        print(f"\nTotal codes in fund_master: {len(master_codes)}")
        print(f"Total unique codes in nav_history: {len(nav_codes)}")

        if len(missing_codes) == 0:

            print("\nVALIDATION PASSED")
            print("Every AMFI code in fund_master exists in nav_history.")

        else:

            print("\nVALIDATION WARNING")
            print(
                f"{len(missing_codes)} codes from fund_master "
                "were not found in nav_history."
            )

            print("\nMissing codes:")
            print(sorted(missing_codes))

    else:
        print(
            "\nCould not identify the scheme-code column "
            "in one or both datasets."
        )


# -------------------------------------------------
# 7. Final data quality summary
# -------------------------------------------------

print("\n" + "=" * 70)
print("DATA QUALITY SUMMARY")
print("=" * 70)

print(f"\nDatasets successfully loaded: {len(datasets)}/10")

total_rows = sum(len(df) for df in datasets.values())
total_missing = sum(
    int(df.isnull().sum().sum())
    for df in datasets.values()
)
total_duplicates = sum(
    int(df.duplicated().sum())
    for df in datasets.values()
)

print(f"Total rows across datasets: {total_rows}")
print(f"Total missing values: {total_missing}")
print(f"Total duplicate rows: {total_duplicates}")

if len(datasets) == 10:
    print("\nAll 10 CSV datasets loaded successfully.")
else:
    print("\nWARNING: Some datasets failed to load.")

print("\nData ingestion completed.")