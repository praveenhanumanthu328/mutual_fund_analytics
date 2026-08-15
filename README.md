# Bluestock Mutual Fund Analytics

## 1. Project Overview

Bluestock Mutual Fund Analytics is an end-to-end data analytics capstone project for analysing mutual fund schemes, NAV history, performance, investor transactions and portfolio holdings.

The project follows the workflow:

**Data Ingestion → Data Cleaning → SQLite/SQL → EDA → Performance Analytics → Advanced Analytics → Power BI Dashboard → Final Report**

---

## 2. Objectives

- Build a reproducible mutual-fund data pipeline.
- Clean and validate multiple financial datasets.
- Store structured data in SQLite and query it with SQL.
- Perform exploratory data analysis with 15+ charts.
- Calculate fund performance and risk metrics.
- Perform advanced risk, investor and concentration analytics.
- Build an interactive four-page Power BI dashboard.
- Communicate findings through a final report and presentation.

---

## 3. Data

The project uses mutual-fund datasets covering:

- Fund/scheme master information
- Historical NAV
- Scheme performance
- Investor transactions
- Portfolio holdings
- Industry and market-related data used by the dashboard

Processed datasets are maintained under `data/processed/`.

---

## 4. Project Structure

```text
mutual_fund_analytics/
│
├── dashboard/
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── EDA_Analysis.ipynb
│   ├── Performance_Analytics.ipynb
│   └── Advanced_Analytics.ipynb
│
├── reports/
│   ├── charts/
│   └── advanced_analytics/
│       ├── var_cvar_report.csv
│       ├── rolling_sharpe_chart.png
│       ├── cohort_analysis.csv
│       ├── sip_continuity.csv
│       └── sector_hhi.csv
│
├── scripts/
│   └── recommender.py
│
├── sql/
├── database_loader.py
├── data_cleaning.py
├── data_dictionary.md
├── data_ingestion.py
├── live_nav_fetch.py
├── requirements.txt
└── README.md
```

---

## 5. Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- SQLite
- SQL
- Microsoft Power BI
- Git/GitHub

---

## 6. Data Ingestion & ETL

The project uses Python scripts to ingest and process the source datasets.

Main scripts include:

- `data_ingestion.py`
- `data_cleaning.py`
- `database_loader.py`
- `live_nav_fetch.py`

The pipeline performs data loading, cleaning, validation and preparation for downstream analysis.

Important data-quality considerations include:

- Date parsing
- Duplicate handling
- Missing-value handling
- NAV validation
- Transaction validation
- Non-trading-day treatment
- Reproducible project paths

---

## 7. SQLite & SQL

Cleaned data is loaded into SQLite for structured storage and querying.

Main database/query resources are maintained in:

```text
sql/
```

The SQLite layer supports validation and analytical queries across the project datasets.

> The `.db` file should not be unnecessarily committed to GitHub. The project schema and SQL queries should be used to reproduce the database where appropriate.

---

## 8. Exploratory Data Analysis

The EDA stage contains 15+ visual analyses.

The analysis covers areas such as:

- Fund and AUM trends
- NAV and return behaviour
- Fund/category comparisons
- Investor transaction behaviour
- SIP behaviour
- Distributions
- Relationships between analytical variables

EDA results are documented in:

```text
notebooks/EDA_Analysis.ipynb
```

---

## 9. Performance Analytics

Performance analysis is documented in:

```text
notebooks/Performance_Analytics.ipynb
```

The analysis includes daily-return based performance and risk measures such as:

- Daily returns
- CAGR
- Volatility / standard deviation
- Sharpe ratio
- Beta
- Drawdown and other project-specified metrics

---

## 10. Advanced Analytics

Advanced analytics is documented in:

```text
notebooks/Advanced_Analytics.ipynb
```

### Historical VaR and CVaR

Historical 95% VaR is calculated as the 5th percentile of the daily return distribution.

CVaR is calculated as the mean of returns at or below the VaR threshold.

The analysis was completed for **40 schemes**.

Output:

```text
reports/advanced_analytics/var_cvar_report.csv
```

### Rolling 90-Day Sharpe

Rolling Sharpe is calculated as:

```text
rolling(90).mean() / rolling(90).std() × √252
```

The analysis is visualised for five selected funds.

Output:

```text
reports/advanced_analytics/rolling_sharpe_chart.png
```

### Investor Cohort Analysis

Investors are grouped by the year of their first transaction.

The analysis calculates:

- Average SIP amount
- Total invested amount
- Investor count
- SIP transaction count
- Top fund preference

Output:

```text
reports/advanced_analytics/cohort_analysis.csv
```

### SIP Continuity Analysis

Investors with **6 or more SIP transactions** are analysed.

An investor is classified as **at-risk** when the average gap between SIP transaction dates is greater than 35 days.

Completed analysis:

- Eligible investors: **1,362**
- At-risk investors: **1,332**
- Continuity rate: **2.2%**

Output:

```text
reports/advanced_analytics/sip_continuity.csv
```

### Fund Recommender

`scripts/recommender.py` accepts:

- Low
- Moderate
- High

It returns the top three funds by Sharpe ratio within the matching risk grade.

### Sector HHI

Sector concentration is measured using:

```text
HHI = Σ(weight_i²)
```

Higher HHI indicates greater sector concentration.

Output:

```text
reports/advanced_analytics/sector_hhi.csv
```

---

## 11. Power BI Dashboard

The project includes a four-page interactive dashboard.

### Page 1 — Industry Overview

- KPI cards
- Industry AUM trend
- AUM by AMC
- Industry-level overview

### Page 2 — Fund Performance

- Return vs risk analysis
- Fund scorecard
- NAV/benchmark view
- Fund-level filtering

### Page 3 — Investor Analytics

- Transaction amount by state
- Transaction type analysis
- Age-group analysis
- Monthly transaction volume

### Page 4 — SIP & Market Trends

- SIP inflow vs Nifty 50
- Category inflow analysis
- Top category analysis
- Interactive filters

---

## 12. Key Findings

- Historical VaR and CVaR were calculated across 40 schemes.
- Rolling 90-day Sharpe provides a time-varying risk-adjusted performance view.
- Investor cohorts can be compared by SIP investment behaviour and fund preference.
- SIP continuity analysis identified a large at-risk population under the specified >35-day average-gap rule.
- Sector HHI provides a quantitative measure of equity-fund concentration.
- The dashboard provides an interactive business view of industry, fund and investor trends.

---

## 13. How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run data ingestion

```bash
python data_ingestion.py
```

### Run data cleaning

```bash
python data_cleaning.py
```

### Load/query SQLite

```bash
python database_loader.py
```

### Run notebooks

Open Jupyter or VS Code and run:

```text
notebooks/EDA_Analysis.ipynb
notebooks/Performance_Analytics.ipynb
notebooks/Advanced_Analytics.ipynb
```

### Run recommender

```bash
python scripts/recommender.py
```

Enter:

```text
Low
```

or:

```text
Moderate
```

or:

```text
High
```

---

## 14. Deliverables

### Completed analytics deliverables

- ETL/data-ingestion scripts
- Data-cleaning scripts
- SQLite/SQL layer
- EDA notebook
- Performance Analytics notebook
- Advanced Analytics notebook
- Fund recommender
- Advanced analytics CSV outputs
- Rolling Sharpe chart
- Power BI dashboard

### Final documentation

- `Final_Report.pdf`
- `Bluestock_MF_Presentation.pptx`
- `README.md`

---

## 15. Limitations

- Analysis is based on the supplied project datasets and available historical period.
- Historical risk metrics describe observed behaviour and do not guarantee future performance.
- The simple recommender uses risk grade and Sharpe ratio and is not a complete investment-advice system.
- Dashboard values may change when the underlying data is refreshed.

---

## 16. Conclusion

The Bluestock Mutual Fund Analytics project demonstrates an end-to-end analytics workflow from financial data ingestion and cleaning to database storage, exploratory analysis, performance measurement, advanced risk and investor analytics, and interactive business visualization.

The project provides a practical foundation for comparing mutual funds, understanding investor behaviour, monitoring portfolio concentration and communicating analytical findings through dashboards and reports.
