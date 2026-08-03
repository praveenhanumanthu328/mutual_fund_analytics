# Bluestock Mutual Fund Analytics — Data Dictionary

## Project Overview

This document describes the main datasets and SQLite star-schema tables used in the Bluestock Mutual Fund Analytics project.

The analytical database contains two dimension tables and four fact tables:

- `dim_fund`
- `dim_date`
- `fact_nav`
- `fact_transactions`
- `fact_performance`
- `fact_aum`

---

# 1. dim_fund

**Purpose:** Stores descriptive information about each mutual fund scheme.

**Source:** `01_fund_master.csv`

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| amfi_code | INTEGER | Unique AMFI scheme identifier | fund_master |
| scheme_name | TEXT | Name of the mutual fund scheme | fund_master |
| fund_house | TEXT | Asset Management Company / fund house | fund_master |
| category | TEXT | Main mutual fund category | fund_master |
| sub_category | TEXT | Detailed scheme classification | fund_master |
| plan_type | TEXT | Type of mutual fund plan | fund_master |
| option_type | TEXT | Scheme option type | fund_master |
| risk_grade | TEXT | Risk classification assigned to the scheme | fund_master |

**Primary Key:** `amfi_code`

---

# 2. dim_date

**Purpose:** Calendar dimension used for time-based analysis.

**Source:** Generated from dates available in NAV, transaction, and AUM datasets.

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| date_key | INTEGER | Unique date identifier in YYYYMMDD format | Generated |
| full_date | DATE | Complete calendar date | Generated |
| day | INTEGER | Day of month | Generated |
| month | INTEGER | Month number from 1 to 12 | Generated |
| month_name | TEXT | Name of month | Generated |
| quarter | INTEGER | Calendar quarter from 1 to 4 | Generated |
| year | INTEGER | Calendar year | Generated |

**Primary Key:** `date_key`

---

# 3. fact_nav

**Purpose:** Stores historical NAV values for mutual fund schemes.

**Source:** `02_nav_history.csv`

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| nav_id | INTEGER | Unique database-generated NAV record identifier | Generated |
| amfi_code | INTEGER | AMFI identifier of the mutual fund | nav_history |
| date_key | INTEGER | Date associated with the NAV observation | nav_history / dim_date |
| nav | REAL | Net Asset Value of the scheme | nav_history |

**Primary Key:** `nav_id`

**Foreign Keys:**

- `amfi_code → dim_fund.amfi_code`
- `date_key → dim_date.date_key`

### Cleaning Rules

- Dates converted to standard datetime format.
- Records sorted by `amfi_code` and date.
- Duplicate records removed.
- NAV values validated to ensure `NAV > 0`.
- Missing calendar-day NAV values are forward-filled using the most recent available NAV.

---

# 4. fact_transactions

**Purpose:** Stores investor-level mutual fund transaction activity.

**Source:** `08_investor_transactions.csv`

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| transaction_id | TEXT | Unique transaction identifier | investor_transactions |
| amfi_code | INTEGER | AMFI code of the transacted scheme | investor_transactions |
| date_key | INTEGER | Date of transaction | investor_transactions / dim_date |
| investor_id | TEXT | Identifier representing the investor | investor_transactions |
| transaction_type | TEXT | Standardised transaction category | investor_transactions |
| amount_inr | REAL | Transaction value in Indian Rupees | investor_transactions |
| units | REAL | Number of mutual fund units involved | investor_transactions |
| nav_at_transaction | REAL | NAV applicable to the transaction | investor_transactions |
| investor_state | TEXT | Investor's state | investor_transactions |
| investor_city | TEXT | Investor's city | investor_transactions |
| kyc_status | TEXT | KYC verification status | investor_transactions |
| data_quality_flag | TEXT | Indicates whether the record passed validation | Generated |

**Primary Key:** `transaction_id`

**Foreign Keys:**

- `amfi_code → dim_fund.amfi_code`
- `date_key → dim_date.date_key`

### Cleaning Rules

Transaction types are standardised to:

- `SIP`
- `Lumpsum`
- `Redemption`

Additional validation:

- `amount_inr > 0`
- Transaction dates converted to standard datetime format.
- KYC status checked against expected enum values.
- Invalid records are flagged for review using `data_quality_flag`.

---

# 5. fact_performance

**Purpose:** Stores mutual fund return and risk-performance metrics.

**Source:** `07_scheme_performance.csv`

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| performance_id | INTEGER | Database-generated performance record identifier | Generated |
| amfi_code | INTEGER | AMFI identifier of the fund | scheme_performance |
| return_1yr_pct | REAL | Fund return over one year (%) | scheme_performance |
| return_3yr_pct | REAL | Fund return over three years (%) | scheme_performance |
| return_5yr_pct | REAL | Fund return over five years (%) | scheme_performance |
| benchmark_3yr_pct | REAL | Three-year benchmark return (%) | scheme_performance |
| alpha | REAL | Risk-adjusted excess return measure | scheme_performance |
| beta | REAL | Sensitivity of fund returns to market movements | scheme_performance |
| sharpe_ratio | REAL | Return earned relative to total risk | scheme_performance |
| sortino_ratio | REAL | Return earned relative to downside risk | scheme_performance |
| std_dev_ann_pct | REAL | Annualised return volatility (%) | scheme_performance |
| max_drawdown_pct | REAL | Maximum observed decline (%) | scheme_performance |
| aum_crore | REAL | Assets under management in ₹ crore | scheme_performance |
| expense_ratio_pct | REAL | Annual fund expense ratio (%) | scheme_performance |
| morningstar_rating | INTEGER | Scheme rating value | scheme_performance |
| return_anomaly_flag | INTEGER | Flags invalid/missing return data | Generated |
| expense_ratio_anomaly_flag | INTEGER | Flags expense ratios outside accepted range | Generated |

**Primary Key:** `performance_id`

**Foreign Key:**

- `amfi_code → dim_fund.amfi_code`

### Validation Rules

Return columns are converted to numeric values.

Expense ratio acceptable range:

`0.1% ≤ expense_ratio_pct ≤ 2.5%`

Values outside this range are flagged as anomalies.

---

# 6. fact_aum

**Purpose:** Stores fund-house-level Assets Under Management information.

**Source:** `03_aum_by_fund_house.csv`

| Column | Data Type | Business Definition | Source |
|---|---|---|---|
| aum_id | INTEGER | Database-generated AUM record identifier | Generated |
| fund_house | TEXT | Name of the fund house | aum_by_fund_house |
| date_key | INTEGER | Date associated with the AUM observation | aum_by_fund_house / dim_date |
| aum_crore | REAL | Total assets under management in ₹ crore | aum_by_fund_house |
| market_share_pct | REAL | Fund house's percentage share of total AUM for the date | Calculated |

**Primary Key:** `aum_id`

**Foreign Key:**

- `date_key → dim_date.date_key`

### Derived Field

`market_share_pct` is calculated as:

`(Fund House AUM / Total Industry AUM for the Date) × 100`

---

# Additional Cleaned Datasets

The following datasets are also cleaned and retained in `data/processed/` for future analysis.

| Dataset | Source File | Purpose |
|---|---|---|
| Fund Master | 01_fund_master.csv | Scheme reference/master information |
| NAV History | 02_nav_history.csv | Historical scheme NAV |
| AUM by Fund House | 03_aum_by_fund_house.csv | Fund-house AUM information |
| Monthly SIP Inflows | 04_monthly_sip_inflows.csv | Monthly SIP investment trends |
| Category Inflows | 05_category_inflows.csv | Fund-category inflow/outflow information |
| Industry Folio Count | 06_industry_folio_count.csv | Industry investor folio trends |
| Scheme Performance | 07_scheme_performance.csv | Scheme return and risk metrics |
| Investor Transactions | 08_investor_transactions.csv | Investor transaction records |
| Portfolio Holdings | 09_portfolio_holdings.csv | Scheme portfolio holdings |
| Benchmark Indices | 10_benchmark_indices.csv | Market benchmark information |

---

# Star Schema Relationships

The primary analytical relationships are:

`dim_fund → fact_nav`

`dim_fund → fact_transactions`

`dim_fund → fact_performance`

`dim_date → fact_nav`

`dim_date → fact_transactions`

`dim_date → fact_aum`

This design separates descriptive dimensions from numerical fact tables and supports efficient mutual fund analytics.

---

# Data Quality Rules

The Day 2 pipeline applies the following major quality controls:

1. Dates are converted into consistent datetime formats.
2. Duplicate records are identified and removed where appropriate.
3. NAV values must be greater than zero.
4. Missing NAV calendar dates are forward-filled within each AMFI scheme.
5. Transaction amounts must be greater than zero.
6. Transaction types are standardised.
7. KYC values are validated.
8. Return metrics are converted to numeric values.
9. Expense ratios outside 0.1%–2.5% are flagged.
10. SQLite table row counts are verified after loading.