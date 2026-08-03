from pathlib import Path
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# ============================================================
# PATHS
# ============================================================

PROCESSED_DIR = Path("data/processed")
SQL_DIR = Path("sql")
DB_PATH = Path("bluestock_mf.db")
SCHEMA_PATH = SQL_DIR / "schema.sql"

print("=" * 65)
print("DAY 2 - SQLITE DATABASE LOADER")
print("=" * 65)


# ============================================================
# 1. LOAD CLEANED CSV FILES
# ============================================================

print("\nLoading cleaned datasets...")

fund = pd.read_csv(
    PROCESSED_DIR / "01_fund_master_clean.csv"
)

nav = pd.read_csv(
    PROCESSED_DIR / "02_nav_history_clean.csv"
)

aum = pd.read_csv(
    PROCESSED_DIR / "03_aum_by_fund_house_clean.csv"
)

performance = pd.read_csv(
    PROCESSED_DIR / "07_scheme_performance_clean.csv"
)

transactions = pd.read_csv(
    PROCESSED_DIR / "08_investor_transactions_clean.csv"
)

print("Fund rows:", len(fund))
print("NAV rows:", len(nav))
print("AUM rows:", len(aum))
print("Performance rows:", len(performance))
print("Transaction rows:", len(transactions))


# ============================================================
# 2. CONVERT DATE COLUMNS
# ============================================================

nav["date"] = pd.to_datetime(
    nav["date"],
    errors="coerce"
)

transactions["transaction_date"] = pd.to_datetime(
    transactions["transaction_date"],
    errors="coerce"
)

aum["date"] = pd.to_datetime(
    aum["date"],
    errors="coerce"
)


# ============================================================
# 3. CREATE DATE DIMENSION
# ============================================================

print("\nCreating dim_date...")

all_dates = pd.concat([
    nav["date"],
    transactions["transaction_date"],
    aum["date"]
]).dropna().drop_duplicates()

dim_date = pd.DataFrame({
    "full_date": all_dates
})

dim_date = dim_date.sort_values(
    "full_date"
).reset_index(drop=True)

dim_date["date_key"] = (
    dim_date["full_date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

dim_date["day"] = (
    dim_date["full_date"].dt.day
)

dim_date["month"] = (
    dim_date["full_date"].dt.month
)

dim_date["month_name"] = (
    dim_date["full_date"].dt.month_name()
)

dim_date["quarter"] = (
    dim_date["full_date"].dt.quarter
)

dim_date["year"] = (
    dim_date["full_date"].dt.year
)

dim_date = dim_date[
    [
        "date_key",
        "full_date",
        "day",
        "month",
        "month_name",
        "quarter",
        "year"
    ]
]

# SQLite-friendly date string
dim_date["full_date"] = (
    dim_date["full_date"]
    .dt.strftime("%Y-%m-%d")
)

print("Date dimension rows:", len(dim_date))


# ============================================================
# 4. CREATE FUND DIMENSION
# ============================================================

print("\nCreating dim_fund...")

fund_columns = [
    "amfi_code",
    "scheme_name",
    "fund_house",
    "category",
    "sub_category",
    "plan_type",
    "option_type",
    "risk_grade"
]

available_fund_columns = [
    col for col in fund_columns
    if col in fund.columns
]

dim_fund = (
    fund[available_fund_columns]
    .drop_duplicates(subset=["amfi_code"])
    .copy()
)

print("Fund dimension rows:", len(dim_fund))


# ============================================================
# 5. CREATE FACT NAV
# ============================================================

print("\nCreating fact_nav...")

nav_fact = nav.merge(
    pd.DataFrame({
        "date": pd.to_datetime(
            dim_date["full_date"]
        ),
        "date_key": dim_date["date_key"]
    }),
    on="date",
    how="left"
)

fact_nav = nav_fact[
    [
        "amfi_code",
        "date_key",
        "nav"
    ]
].copy()

fact_nav["nav"] = pd.to_numeric(
    fact_nav["nav"],
    errors="coerce"
)

fact_nav = fact_nav[
    fact_nav["nav"] > 0
]

fact_nav = fact_nav.drop_duplicates(
    subset=["amfi_code", "date_key"]
)

print("Fact NAV rows:", len(fact_nav))


# ============================================================
# 6. CREATE TRANSACTION FACT
# ============================================================

print("\nCreating fact_transactions...")

transaction_fact = transactions.merge(
    pd.DataFrame({
        "transaction_date": pd.to_datetime(
            dim_date["full_date"]
        ),
        "date_key": dim_date["date_key"]
    }),
    on="transaction_date",
    how="left"
)

transaction_columns = [
    "transaction_id",
    "amfi_code",
    "date_key",
    "investor_id",
    "transaction_type",
    "amount_inr",
    "units",
    "nav_at_transaction",
    "investor_state",
    "investor_city",
    "kyc_status",
    "data_quality_flag"
]

available_transaction_columns = [
    col for col in transaction_columns
    if col in transaction_fact.columns
]

fact_transactions = transaction_fact[
    available_transaction_columns
].copy()

print(
    "Fact transaction rows:",
    len(fact_transactions)
)


# ============================================================
# 7. CREATE PERFORMANCE FACT
# ============================================================

print("\nCreating fact_performance...")

performance_columns = [
    "amfi_code",
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
    "return_anomaly_flag",
    "expense_ratio_anomaly_flag"
]

available_performance_columns = [
    col for col in performance_columns
    if col in performance.columns
]

fact_performance = performance[
    available_performance_columns
].copy()

# SQLite stores booleans nicely as 0/1
for col in [
    "return_anomaly_flag",
    "expense_ratio_anomaly_flag"
]:
    if col in fact_performance.columns:
        fact_performance[col] = (
            fact_performance[col]
            .astype(int)
        )

print(
    "Fact performance rows:",
    len(fact_performance)
)


# ============================================================
# 8. CREATE AUM FACT
# ============================================================

print("\nCreating fact_aum...")

aum_fact = aum.merge(
    pd.DataFrame({
        "date": pd.to_datetime(
            dim_date["full_date"]
        ),
        "date_key": dim_date["date_key"]
    }),
    on="date",
    how="left"
)

fact_aum = aum_fact[
    [
        "fund_house",
        "date_key",
        "aum_crore"
    ]
].copy()

# Calculate market share because source does not contain it
fact_aum["market_share_pct"] = (
    fact_aum.groupby("date_key")[
        "aum_crore"
    ].transform(
        lambda x: (x / x.sum()) * 100
    )
)

print("Fact AUM rows:", len(fact_aum))


# ============================================================
# 9. REMOVE OLD DATABASE IF IT EXISTS
# ============================================================

if DB_PATH.exists():

    DB_PATH.unlink()

    print(
        "\nOld database removed."
    )


# ============================================================
# 10. CREATE DATABASE USING schema.sql
# ============================================================

print("\nCreating SQLite database...")

connection = sqlite3.connect(
    DB_PATH
)

connection.execute(
    "PRAGMA foreign_keys = ON;"
)

with open(
    SCHEMA_PATH,
    "r",
    encoding="utf-8"
) as schema_file:

    schema_sql = schema_file.read()

connection.executescript(
    schema_sql
)

connection.commit()
connection.close()

print(
    "Database schema created successfully."
)


# ============================================================
# 11. SQLALCHEMY ENGINE
# ============================================================

engine = create_engine(
    f"sqlite:///{DB_PATH}"
)


# ============================================================
# 12. LOAD DIMENSIONS
# ============================================================

print("\nLoading dimension tables...")

dim_fund.to_sql(
    "dim_fund",
    engine,
    if_exists="append",
    index=False
)

dim_date.to_sql(
    "dim_date",
    engine,
    if_exists="append",
    index=False
)

print("Dimension tables loaded.")


# ============================================================
# 13. LOAD FACT TABLES
# ============================================================

print("\nLoading fact tables...")

fact_nav.to_sql(
    "fact_nav",
    engine,
    if_exists="append",
    index=False
)

fact_transactions.to_sql(
    "fact_transactions",
    engine,
    if_exists="append",
    index=False
)

fact_performance.to_sql(
    "fact_performance",
    engine,
    if_exists="append",
    index=False
)

fact_aum.to_sql(
    "fact_aum",
    engine,
    if_exists="append",
    index=False
)

print("Fact tables loaded.")


# ============================================================
# 14. VERIFY DATABASE ROW COUNTS
# ============================================================

print("\n" + "=" * 65)
print("DATABASE ROW COUNT VERIFICATION")
print("=" * 65)

expected_counts = {
    "dim_fund": len(dim_fund),
    "dim_date": len(dim_date),
    "fact_nav": len(fact_nav),
    "fact_transactions": len(
        fact_transactions
    ),
    "fact_performance": len(
        fact_performance
    ),
    "fact_aum": len(fact_aum)
}

all_match = True

with engine.connect() as conn:

    for table, expected in expected_counts.items():

        result = conn.exec_driver_sql(
            f"SELECT COUNT(*) FROM {table}"
        )

        actual = result.scalar()

        status = (
            "MATCH"
            if actual == expected
            else "MISMATCH"
        )

        if actual != expected:
            all_match = False

        print(
            f"{table}: "
            f"expected={expected}, "
            f"database={actual} "
            f"[{status}]"
        )


# ============================================================
# 15. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 65)

if all_match:

    print(
        "SUCCESS: All database row counts match."
    )

else:

    print(
        "WARNING: Some row counts do not match."
    )

print(
    f"SQLite database created: {DB_PATH}"
)

print(
    "Day 2 database loading completed."
)