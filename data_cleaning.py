from pathlib import Path
import pandas as pd
import numpy as np

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

print("=" * 65)
print("DAY 2 - DATA CLEANING")
print("=" * 65)


# ============================================================
# 1. NAV HISTORY
# ============================================================

print("\nCleaning NAV History...")

nav = pd.read_csv(RAW_DIR / "02_nav_history.csv")

source_nav_rows = len(nav)

# Convert date
nav["date"] = pd.to_datetime(nav["date"], errors="coerce")

# Convert NAV to numeric
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

# Remove exact duplicate records
nav = nav.drop_duplicates()

# Sort
nav = nav.sort_values(
    ["amfi_code", "date"]
).reset_index(drop=True)

# Remove invalid dates
invalid_dates = nav["date"].isna().sum()

if invalid_dates:
    print(f"Invalid NAV dates found: {invalid_dates}")
    nav = nav.dropna(subset=["date"])

# NAV must be positive
invalid_nav = (
    nav["nav"].notna() &
    (nav["nav"] <= 0)
)

print("Invalid NAV <= 0:", invalid_nav.sum())

nav.loc[invalid_nav, "nav"] = np.nan


# ------------------------------------------------------------
# Forward-fill NAV for calendar gaps such as weekends/holidays
# ------------------------------------------------------------

calendar_frames = []

for amfi_code, group in nav.groupby("amfi_code"):

    group = group.sort_values("date")

    full_dates = pd.date_range(
        start=group["date"].min(),
        end=group["date"].max(),
        freq="D"
    )

    group = (
        group.set_index("date")
        .reindex(full_dates)
    )

    group.index.name = "date"

    group["amfi_code"] = amfi_code

    # Forward fill NAV for missing calendar dates
    group["nav"] = group["nav"].ffill()

    group = group.reset_index()

    calendar_frames.append(group)

nav_clean = pd.concat(
    calendar_frames,
    ignore_index=True
)

nav_clean = nav_clean[
    ["amfi_code", "date", "nav"]
]

nav_clean.to_csv(
    PROCESSED_DIR / "02_nav_history_clean.csv",
    index=False
)

print("Source NAV rows:", source_nav_rows)
print("Clean/calendar NAV rows:", len(nav_clean))
print("NAV cleaning complete.")


# ============================================================
# 2. INVESTOR TRANSACTIONS
# ============================================================

print("\nCleaning Investor Transactions...")

transactions = pd.read_csv(
    RAW_DIR / "08_investor_transactions.csv"
)

source_transaction_rows = len(transactions)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

# Standardise transaction types
transaction_mapping = {
    "sip": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "redemption": "Redemption",
}

transactions["transaction_type"] = (
    transactions["transaction_type"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map(transaction_mapping)
)

valid_transaction_types = [
    "SIP",
    "Lumpsum",
    "Redemption"
]

invalid_types = ~transactions[
    "transaction_type"
].isin(valid_transaction_types)

print(
    "Invalid transaction types:",
    invalid_types.sum()
)


# Amount validation
transactions["amount_inr"] = pd.to_numeric(
    transactions["amount_inr"],
    errors="coerce"
)

invalid_amount = (
    transactions["amount_inr"].isna() |
    (transactions["amount_inr"] <= 0)
)

print(
    "Invalid transaction amounts:",
    invalid_amount.sum()
)


# KYC validation
valid_kyc = [
    "Verified",
    "Pending"
]

transactions["kyc_status"] = (
    transactions["kyc_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

invalid_kyc = ~transactions[
    "kyc_status"
].isin(valid_kyc)

print(
    "Invalid KYC values:",
    invalid_kyc.sum()
)

print(
    "KYC values:",
    transactions["kyc_status"].unique()
)


# Flag invalid records instead of silently deleting them
transactions["data_quality_flag"] = np.where(
    invalid_types |
    invalid_amount |
    invalid_kyc |
    transactions["transaction_date"].isna(),
    "Review",
    "Valid"
)

transactions.to_csv(
    PROCESSED_DIR /
    "08_investor_transactions_clean.csv",
    index=False
)

print(
    "Transaction rows:",
    source_transaction_rows
)

print("Transaction cleaning complete.")


# ============================================================
# 3. SCHEME PERFORMANCE
# ============================================================

print("\nCleaning Scheme Performance...")

performance = pd.read_csv(
    RAW_DIR / "07_scheme_performance.csv"
)

source_performance_rows = len(performance)

numeric_columns = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "benchmark_3yr_pct",
    "alpha",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "std_dev_ann_pct",
    "max_drawdown_pct",
    "aum_crore",
    "expense_ratio_pct",
    "morningstar_rating",
]

for column in numeric_columns:

    performance[column] = pd.to_numeric(
        performance[column],
        errors="coerce"
    )


# Flag missing/non-numeric return values
return_columns = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "benchmark_3yr_pct",
]

performance[
    "return_anomaly_flag"
] = performance[
    return_columns
].isna().any(axis=1)


# Expense ratio range check
performance[
    "expense_ratio_anomaly_flag"
] = ~performance[
    "expense_ratio_pct"
].between(
    0.1,
    2.5,
    inclusive="both"
)


print(
    "Return anomalies:",
    performance[
        "return_anomaly_flag"
    ].sum()
)

print(
    "Expense ratio anomalies:",
    performance[
        "expense_ratio_anomaly_flag"
    ].sum()
)


performance.to_csv(
    PROCESSED_DIR /
    "07_scheme_performance_clean.csv",
    index=False
)

print(
    "Performance rows:",
    source_performance_rows
)

print("Performance cleaning complete.")


# ============================================================
# 4. CLEAN/COPY REMAINING DATASETS
# ============================================================

print("\nProcessing remaining datasets...")

special_files = {
    "02_nav_history.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
}

for filename in FILES:

    if filename in special_files:
        continue

    df = pd.read_csv(
        RAW_DIR / filename
    )

    # Remove exact duplicate records
    df = df.drop_duplicates()

    # Remove unnecessary whitespace
    for column in df.select_dtypes(
        include="object"
    ).columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

        # Restore missing values changed to string "nan"
        df[column] = df[column].replace(
            "nan",
            np.nan
        )

    clean_filename = (
        filename.replace(
            ".csv",
            "_clean.csv"
        )
    )

    df.to_csv(
        PROCESSED_DIR / clean_filename,
        index=False
    )

    print(
        f"{filename} -> "
        f"{clean_filename}: {len(df)} rows"
    )


# ============================================================
# 5. FINAL VALIDATION
# ============================================================

print("\n" + "=" * 65)
print("CLEANING SUMMARY")
print("=" * 65)

processed_files = list(
    PROCESSED_DIR.glob("*.csv")
)

print(
    f"Cleaned CSV files created: "
    f"{len(processed_files)}"
)

for file in sorted(processed_files):

    df = pd.read_csv(file)

    print(
        f"{file.name}: "
        f"{len(df)} rows"
    )


print("\nDay 2 data cleaning completed successfully.")