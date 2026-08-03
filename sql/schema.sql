-- =========================================================
-- Bluestock Mutual Fund Analytics
-- Day 2 - SQLite Star Schema
-- =========================================================

PRAGMA foreign_keys = ON;

-- =========================================================
-- DIMENSION: FUND
-- =========================================================

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT,
    category TEXT,
    sub_category TEXT,
    plan_type TEXT,
    option_type TEXT,
    risk_grade TEXT
);


-- =========================================================
-- DIMENSION: DATE
-- =========================================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    day INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER,
    year INTEGER
);


-- =========================================================
-- FACT: NAV
-- =========================================================

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL CHECK (nav > 0),

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    UNIQUE(amfi_code, date_key)
);


-- =========================================================
-- FACT: INVESTOR TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    investor_id TEXT,
    transaction_type TEXT,
    amount_inr REAL CHECK (amount_inr > 0),
    units REAL,
    nav_at_transaction REAL,
    investor_state TEXT,
    investor_city TEXT,
    kyc_status TEXT,
    data_quality_flag TEXT,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);


-- =========================================================
-- FACT: PERFORMANCE
-- =========================================================

CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    return_anomaly_flag INTEGER,
    expense_ratio_anomaly_flag INTEGER,

    FOREIGN KEY (amfi_code)
        REFERENCES dim_fund(amfi_code)
);


-- =========================================================
-- FACT: AUM
-- =========================================================

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT NOT NULL,
    date_key INTEGER,
    aum_crore REAL,
    market_share_pct REAL,

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_nav_fund
ON fact_nav(amfi_code);

CREATE INDEX IF NOT EXISTS idx_nav_date
ON fact_nav(date_key);

CREATE INDEX IF NOT EXISTS idx_transaction_fund
ON fact_transactions(amfi_code);

CREATE INDEX IF NOT EXISTS idx_transaction_date
ON fact_transactions(date_key);

CREATE INDEX IF NOT EXISTS idx_performance_fund
ON fact_performance(amfi_code);