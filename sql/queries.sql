-- ============================================================
-- BLUESTOCK MUTUAL FUND ANALYTICS
-- DAY 2 - ANALYTICAL SQL QUERIES
-- ============================================================


-- ============================================================
-- QUERY 1
-- Top 5 fund houses by latest AUM
-- ============================================================

SELECT
    fund_house,
    ROUND(aum_crore, 2) AS aum_crore
FROM fact_aum
WHERE date_key = (
    SELECT MAX(date_key)
    FROM fact_aum
)
ORDER BY aum_crore DESC
LIMIT 5;


-- ============================================================
-- QUERY 2
-- Average NAV per month
-- ============================================================

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 2) AS average_nav
FROM fact_nav n
JOIN dim_date d
    ON n.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- QUERY 3
-- SIP year-over-year growth
-- ============================================================

WITH yearly_sip AS (
    SELECT
        d.year,
        SUM(t.amount_inr) AS total_sip_amount
    FROM fact_transactions t
    JOIN dim_date d
        ON t.date_key = d.date_key
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
),

sip_growth AS (
    SELECT
        year,
        total_sip_amount,
        LAG(total_sip_amount)
            OVER (ORDER BY year) AS previous_year_amount
    FROM yearly_sip
)

SELECT
    year,
    ROUND(total_sip_amount, 2)
        AS total_sip_amount,

    ROUND(
        (
            (total_sip_amount - previous_year_amount)
            / previous_year_amount
        ) * 100,
        2
    ) AS yoy_growth_pct

FROM sip_growth
ORDER BY year;


-- ============================================================
-- QUERY 4
-- Transactions by investor state
-- ============================================================

SELECT
    investor_state,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2)
        AS total_transaction_amount
FROM fact_transactions
GROUP BY investor_state
ORDER BY total_transaction_amount DESC;


-- ============================================================
-- QUERY 5
-- Funds with expense ratio below 1%
-- ============================================================

SELECT
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1
ORDER BY p.expense_ratio_pct ASC;


-- ============================================================
-- QUERY 6
-- Top 5 schemes by 3-year return
-- ============================================================

SELECT
    f.scheme_name,
    f.fund_house,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.return_3yr_pct IS NOT NULL
ORDER BY p.return_3yr_pct DESC
LIMIT 5;


-- ============================================================
-- QUERY 7
-- Total transaction amount by transaction type
-- ============================================================

SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2)
        AS total_amount,
    ROUND(AVG(amount_inr), 2)
        AS average_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;


-- ============================================================
-- QUERY 8
-- Fund count by category
-- ============================================================

SELECT
    category,
    COUNT(DISTINCT amfi_code)
        AS number_of_funds
FROM dim_fund
GROUP BY category
ORDER BY number_of_funds DESC;


-- ============================================================
-- QUERY 9
-- Top 5 funds by Sharpe ratio
-- ============================================================

SELECT
    f.scheme_name,
    f.fund_house,
    p.sharpe_ratio,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC
LIMIT 5;


-- ============================================================
-- QUERY 10
-- Monthly transaction trend
-- ============================================================

SELECT
    d.year,
    d.month,
    d.month_name,

    COUNT(*) AS transaction_count,

    ROUND(
        SUM(t.amount_inr),
        2
    ) AS total_transaction_amount

FROM fact_transactions t

JOIN dim_date d
    ON t.date_key = d.date_key

GROUP BY
    d.year,
    d.month,
    d.month_name

ORDER BY
    d.year,
    d.month;