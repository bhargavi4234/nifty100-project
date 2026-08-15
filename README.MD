# NIFTY100 Financial Intelligence Platform

## Sprint 1, Sprint 2, Sprint 3 & Sprint 4 – Data Foundation, Financial Analytics, Peer Analysis, Streamlit Dashboard & Valuation

### Project Overview

The **NIFTY100 Financial Intelligence Platform** is designed to build a reliable financial analytics platform for NIFTY100 companies. The project extracts financial data from multiple Excel source files, validates it using Data Quality (DQ) rules, stores the validated data in a SQLite database, and generates advanced financial ratios for analytics and company screening.


---

# Sprint Goals

## Sprint 1

By the end of Sprint 1, the project successfully:

- Built an ETL pipeline for financial data.
- Loaded data from 12 Excel source files.
- Created a validated SQLite database (`nifty100.db`).
- Implemented 16 Data Quality rules.
- Generated validation and audit reports.
- Established the foundation for future analytics and dashboard modules.

---

## Sprint 2

By the end of Sprint 2, the project successfully:

- Calculated financial ratios for NIFTY100 companies.
- Generated 5-Year CAGR metrics.
- Populated the `financial_ratios` table.
- Validated ROE and ROCE against source Excel data.
- Logged financial ratio edge cases.
- Implemented a financial screener.
- Completed analytics testing and Sprint retrospective.

---

# Project Structure

nifty100_project/
│
├── config/
│   └── screener_config.yaml
│
├── data/
│   ├── raw/
│   │   └── market_cap.xlsx
│   └── db/
│       └── nifty100.db
│
├── output/
│   ├── capital_allocation.csv
│   ├── load_audit.csv
│   ├── peer_comparison.xlsx
│   ├── ratio_edge_cases.log
│   ├── retrospective.md
│   ├── screener_output.xlsx
│   ├── validation_failures.csv
│   ├── valuation_summary.xlsx
│   └── valuation_flags.csv
│
├── reports/
│   ├── radar_charts/
│   │   ├── ABB_radar.png
│   │   ├── ADANIENSOL_radar.png
│   │   ├── ADANIENT_radar.png
│   │   └── ...
│   └── Sprint_3_Retrospective.docx
│
├── src/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── cagr.py
│   │   ├── cashflow.py
│   │   ├── generate_capital_allocation.py
│   │   ├── peer.py
│   │   ├── peer_report.py
│   │   ├── populate_financial_ratios.py
│   │   ├── radar.py
│   │   ├── ratios.py
│   │   └── valuation.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── 01_home.py
│   │   │   ├── 02_profile.py
│   │   │   ├── 03_screener.py
│   │   │   ├── 04_peers.py
│   │   │   ├── 05_trends.py
│   │   │   ├── 06_sectors.py
│   │   │   ├── 07_capital.py
│   │   │   └── 08_reports.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── db.py
│   │
│   ├── etl/
│   │   └── ...
│   │
│   └── screener/
│       ├── __init__.py
│       ├── engine.py
│       └── presets.py
│
├── tests/
│   ├── analytics/
│   │   ├── test_cagr.py
│   │   ├── test_cashflow.py
│   │   └── test_ratios.py
│   └── etl/
│       └── test_normaliser.py
│
├── db/
│   └── schema.sql
│
├── notebooks/
│   └── exploratory_queries.sql
│
├── README.MD
├── Makefile
├── requirements.txt
└── .gitignore
---

# Technologies Used

- Python 3.13
- Pandas
- NumPy
- SQLite
- OpenPyXL
- Pytest
- python-dotenv

---

# Sprint 1 Tasks Completed

## Day 01 – Environment Setup

Completed:

- Created project directory structure
- Configured Python virtual environment
- Installed required libraries
- Configured environment variables
- Created Makefile

---

## Day 02 – Excel Loader & Normaliser

Implemented:

- Excel Loader
- `normalize_year()`
- `normalize_ticker()`

Unit Testing:

- 38 Unit Tests
- 38 Passed
- 0 Failed

---

## Day 03 – Data Quality Validation

Implemented all 16 Data Quality Rules.

### DQ Rules

- DQ-01 Primary Key Uniqueness
- DQ-02 Company-Year Uniqueness
- DQ-03 Foreign Key Integrity
- DQ-04 Balance Sheet Validation
- DQ-05 Operating Profit Margin Validation
- DQ-06 Positive Sales Validation
- DQ-07 Reporting Period Validation
- DQ-08 Ticker Validation
- DQ-09 Cash Flow Validation
- DQ-10 Fixed Assets Validation
- DQ-11 Tax Rate Validation
- DQ-12 Dividend Validation
- DQ-13 URL Validation
- DQ-14 EPS Sign Validation
- DQ-15 Liability Validation
- DQ-16 Coverage Validation

Generated:

- `output/validation_failures.csv`

---

## Day 04 – SQLite Database Schema

Completed:

- SQLite Schema
- Primary Keys
- Foreign Keys
- PRAGMA Foreign Keys Enabled

Database Schema File:

```
db/schema.sql
```
---

## Day 05 – Full Data Load

Successfully loaded:

- 7 Core Excel Files
- 5 Supplementary Excel Files

Generated:

- `nifty100.db`
- `output/load_audit.csv`

Performed:

- Foreign Key Validation
- Load Audit Generation

Foreign Key Check:

```
PASSED (0 Violations)
```

---

## Day 06 – Manual Data Quality Review

Completed:

- Reviewed 5 Random Companies
- Verified Year Coverage
- Identified Companies with Less Than Five Years of Data
- Verified Loader Execution
- Re-ran Database Load
- Verified Foreign Key Integrity

---

## Day 07 – Sprint Wrap-Up

Completed:

- Exploratory SQL Queries
- Unit Testing
- Database Demonstration
- Sprint Retrospective

---

# Database Tables

The SQLite database contains the following tables:

- companies
- sectors
- peer_groups
- profitandloss
- balancesheet
- cashflow
- analysis
- documents
- prosandcons
- financial_ratios
- market_cap
- stock_prices

---

# Deliverables

## Sprint 1

- ✅ `nifty100.db`
- ✅ `output/load_audit.csv`
- ✅ `output/validation_failures.csv`
- ✅ `src/etl/loader.py`
- ✅ `src/etl/validator.py`
- ✅ `src/etl/normaliser.py`
- ✅ `db/schema.sql`
- ✅ `tests/etl/` (38 Unit Tests)
- ✅ `notebooks/exploratory_queries.sql`

---

# Database Validation

| Validation | Result |
|------------|--------|
| Companies Loaded | 92 |
| Foreign Key Check | Passed (0 Violations) |
| Unit Tests | 38 Passed |
| Manual Review | Completed |
| DQ Rules | 16 Implemented |

---

# SQL Queries

Exploratory SQL queries are available in:

```
notebooks/exploratory_queries.sql
```

The file includes queries such as:

- Total Companies
- Total Stock Price Records
- Companies by Sector
- Top Companies by ROE
- Market Capitalization Analysis
- Financial Statement Queries
- Foreign Key Validation
- Companies with Less Than Five Years of Data
- Stock Price Analysis
- Aggregate Financial Statistics
---

# Sprint 2 Tasks Completed

## Day 08 – Financial Ratio Framework

Completed:

- Created analytics module
- Connected analytics module with SQLite database
- Designed the financial_ratios table
- Implemented financial ratio calculation workflow

Files Created:

- `src/analytics/ratios.py`
- `src/analytics/populate_financial_ratios.py`
- `src/analytics/cagr.py`

---

## Day 09 – Profitability Ratios

Implemented:

- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Net Profit Margin
- Operating Profit Margin

Updated:

- `financial_ratios` SQLite table

Calculated:

- Profitability metrics for all companies

---

## Day 10 – Leverage & Efficiency Ratios

Implemented:

- Debt-to-Equity Ratio
- Interest Coverage Ratio
- Asset Turnover Ratio

Updated:

- `financial_ratios` SQLite table

Calculated:

- Leverage metrics
- Efficiency metrics

---

## Day 11 – Growth & Cash Flow Analytics

Implemented:

- Revenue CAGR (5-Year)
- PAT CAGR (5-Year)
- EPS CAGR (5-Year)
- Free Cash Flow
- CFO Quality Score

Generated:

- Composite Quality Score

Updated:

- `financial_ratios` SQLite table

Successfully calculated financial growth metrics for all eligible companies.

---
## Day 12 – Financial Ratio Population

Completed:

- Calculated financial ratios for all companies
- Populated the `financial_ratios` table
- Updated SQLite database with calculated metrics
- Verified successful database updates

Generated:

- Updated `nifty100.db`

Performed:

- Database Validation
- Financial Ratio Population

Database Update:

```
financial_ratios table populated successfully
```

---

## Day 13 – Ratio Validation & Edge Case Logging

Completed:

- Compared calculated ROE with source Excel values
- Compared calculated ROCE with source Excel values
- Identified financial ratio differences
- Categorized ratio discrepancies

Categories:

- Data Source Issue
- Version Difference
- Formula Discrepancy

Generated:

- `output/ratio_edge_cases.log`

---

## Day 14 – Testing & Sprint Wrap-Up

Completed:

- Executed analytics unit tests
- Reviewed ratio_edge_cases.log
- Verified financial screener query
- Demonstrated financial_ratios table
- Completed Sprint retrospective

Generated:

- `output/retrospective.md`

Unit Testing:

- 55 Unit Tests
- 55 Passed
- 0 Failed

---

# Deliverables

## Sprint 1

- ✅ `nifty100.db`
- ✅ `output/load_audit.csv`
- ✅ `output/validation_failures.csv`
- ✅ `src/etl/loader.py`
- ✅ `src/etl/validator.py`
- ✅ `src/etl/normaliser.py`
- ✅ `db/schema.sql`
- ✅ `tests/etl/` (38 Unit Tests)
- ✅ `notebooks/exploratory_queries.sql`

## Sprint 2

- ✅ `financial_ratios` table in SQLite (1,100+ rows with 14+ KPI columns per company-year)
- ✅ `output/capital_allocation.csv`
- ✅ `output/ratio_edge_cases.log`
- ✅ `src/analytics/ratios.py`
- ✅ `src/analytics/cagr.py`
- ✅ `src/analytics/cashflow.py`
- ✅ `src/analytics/generate_capital_allocation.py`
- ✅ `src/analytics/populate_financial_ratios.py`
- ✅ `tests/analytics/` (55 Unit Tests)


# Running the Project

## Load Data

```bash
python src/etl/loader.py
```

## Validate Data

```bash
python src/etl/validator.py
```

## Manual Data Review

```bash
python src/etl/manual_review.py
```

## Foreign Key Validation

```bash
python src/etl/fk_check.py
```

## Generate Financial Ratios

```bash
python src/analytics/populate_financial_ratios.py
```

---

# Testing

Run all ETL unit tests:

```bash
pytest tests/etl
```

Run all Analytics unit tests:

```bash
pytest tests/analytics
```

Results:

```text
======================================
Sprint 1 : 38 Passed
Sprint 2 : 55 Passed
======================================
Total Tests Passed : 93
Failed : 0
======================================
```

---

# Key Outputs

- SQLite database created successfully.
- Load audit generated successfully.
- Validation report generated successfully.
- Foreign key validation passed.
- Manual review completed.
- Financial ratios calculated successfully.
- CAGR metrics generated successfully.
- Composite Quality Scores calculated.
- Ratio validation completed.
- Edge case log generated successfully.
- Financial screener executed successfully.
- All unit tests passed without failures.

---

# Sprint Outcome

## Sprint 1

Sprint 1 successfully established the data foundation for the **NIFTY100 Financial Intelligence Platform**.

Achievements:

- Built a complete ETL pipeline.
- Loaded financial data from multiple Excel source files.
- Implemented 16 Data Quality validation rules.
- Created a validated SQLite database.
- Generated audit and validation reports.
- Performed manual data quality review.
- Passed all ETL unit tests (38/38).
- Verified database integrity with zero foreign key violations.

---

## Sprint 2

Sprint 2 successfully transformed the project into a financial analytics platform.

Achievements:

- Calculated profitability ratios.
- Calculated leverage and efficiency ratios.
- Generated 5-Year CAGR metrics.
- Calculated Free Cash Flow and CFO Quality Score.
- Generated Composite Quality Scores.
- Populated the financial_ratios table.
- Validated ROE and ROCE against source values.
- Logged financial ratio edge cases.
- Executed financial screener queries.
- Passed all analytics unit tests (55/55).

The project is now ready for future sprints involving advanced analytics, APIs, dashboards, and investment insights.

---


## Sprint 3 — Screener + Peer Engine

### Sprint Objective

Sprint 3 focused on developing the financial screener, composite quality scoring, peer percentile rankings, radar charts, and peer comparison reports for the Nifty 100 Financial Analytics Project.

### Day 15 — Screener Engine

- Implemented `src/screener/engine.py`.
- Developed the financial screening and filtering engine.
- Added filters for ROE, Debt-to-Equity, Free Cash Flow, Revenue CAGR, PAT CAGR, EPS CAGR, Operating Profit Margin, Interest Coverage, Asset Turnover, Market Capitalisation, P/E, P/B, Dividend Yield, Sales, and Net Profit.
- Implemented a composite quality score from 0–100.
- Added profitability, cash quality, growth, and leverage components to the composite score.
- Added sector-relative score normalisation.

### Day 16 — Screener Presets

Implemented six predefined screening presets:

- Quality Compounder
- Value Pick
- Growth Accelerator
- Dividend Champion
- Debt-Free Blue Chip
- Turnaround Watch

The preset threshold definitions are maintained in the analyst-editable configuration file:

`config/screener_config.yaml`

### Day 17 — Screener Excel Report

Generated:

`output/screener_output.xlsx`

The workbook contains six sheets, one for each screener preset.

The report includes financial metrics, composite quality scores, and colour-coded screening results.

All six presets were verified to return between 5 and 50 companies.

### Day 18 — Peer Percentile Rankings

Implemented:

`src/analytics/peer.py`

Peer percentile rankings were calculated for 10 financial metrics across 11 peer groups.

Metrics used:

- ROE
- ROCE
- Net Profit Margin
- Debt-to-Equity
- Free Cash Flow
- PAT CAGR 5yr
- Revenue CAGR 5yr
- EPS CAGR 5yr
- Interest Coverage
- Asset Turnover

For Debt-to-Equity, the percentile ranking is inverted so that lower Debt-to-Equity receives a higher percentile rank.

The results were stored in the SQLite table:

`peer_percentiles`

A total of 7,300 peer percentile rows were created.

Companies without a peer group are handled using `No peer group assigned`.

### Day 19 — Peer Radar Charts

Implemented:

`src/analytics/radar.py`

Radar charts were generated for peer analysis using Python and Matplotlib.

The radar charts contain:

- ROE
- ROCE
- NPM
- D/E
- FCF Score
- PAT CAGR 5yr
- Revenue CAGR 5yr
- Composite Score

Peer-group averages are included as a reference overlay.

The generated PNG files are stored in:

`reports/radar_charts/`

### Day 20 — Peer Comparison Excel Report

Implemented:

`src/analytics/peer_report.py`

Generated:

`output/peer_comparison.xlsx`

The workbook contains exactly 11 peer-group sheets:

- Automobiles
- Consumer Finance
- FMCG
- IT Services
- Life Insurance
- Oil & Gas
- Pharmaceuticals
- Power & Utilities
- Private Banks
- Public Sector Banks
- Steel

The report contains company information, financial metrics, percentile rankings, benchmark highlighting, and peer median values.

Percentile ranking cells are colour-coded as:

- Green — >= 75th percentile
- Yellow — 25th to 75th percentile
- Red — <= 25th percentile

Benchmark company rows are highlighted with a gold/amber background.

### Day 21 — Tests and Sprint Review

- Ran the complete automated test suite.
- Final result: **93 tests passed with 0 failures**.
- Manually verified the Quality Compounder preset.
- Verified that the six presets return between 5 and 50 companies.
- Verified IT Services peer ROE percentile ranking.
- Verified FMCG peer ROE percentile ranking.
- Prepared the Sprint 3 retrospective.
- Prepared the screener and peer comparison reports for team-lead demonstration.

### Sprint 3 Deliverables

- `output/screener_output.xlsx`
- `output/peer_comparison.xlsx`
- `reports/radar_charts/`
- `peer_percentiles` SQLite table
- `config/screener_config.yaml`
- `src/screener/engine.py`
- `src/analytics/peer.py`
- `src/analytics/radar.py`
- `src/analytics/peer_report.py`


### Sprint 3 Terminal Commands

```powershell
python -m src.screener.presets
```

```powershell
python -m src.analytics.peer
```

```powershell
python -m src.analytics.radar
```

```powershell
python -m src.analytics.peer_report
```

```powershell
python -m pytest -q
```


### Sprint 3 Retrospective

#### What Went Well
- Successfully implemented the financial screener engine.
- Created six screening presets.
- Implemented composite quality scoring.
- Implemented peer percentile rankings for 11 peer groups.
- Generated radar charts and Excel reports.
- Completed automated testing with 93 passed tests and 0 failures.

#### Challenges
- Some companies did not have an assigned peer group.
- SQL joins required database schema verification.
- Initial peer report generation caused high memory usage.

#### Improvements
- Corrected SQL joins based on the actual database schema.
- Optimised peer report generation to reduce memory usage.
- Handled companies without peer groups safely.

#### Learning Outcomes
- Learned practical financial screening and peer analysis.
- Improved skills in SQLite, Pandas, Excel reporting, and data visualisation.
- Gained experience with automated testing and debugging.
- Learned how to optimise data processing for large datasets.

#### Sprint 3 Status
**Completed**


# Sprint 4 — Streamlit Dashboard, Valuation & QA

## Sprint Objective

Sprint 4 focused on building an interactive Streamlit dashboard for NIFTY100 financial analysis, implementing valuation analytics, and completing integration testing and documentation.

## Day 22 — Streamlit Dashboard Foundation

Completed:

- Created the Streamlit dashboard entry point.
- Created 8 dashboard screens.
- Added sidebar navigation.
- Connected the dashboard to the SQLite database.
- Added reusable database functions.
- Configured the dashboard with a wide layout.

Dashboard entry point:

```text
src/dashboard/app.py
```

Dashboard pages:

```text
src/dashboard/pages/
├── 01_home.py
├── 02_profile.py
├── 03_screener.py
├── 04_peers.py
├── 05_trends.py
├── 06_sectors.py
├── 07_capital.py
└── 08_reports.py
```

## Day 23 — Home & Company Profile

### Home Screen

Implemented:

- Average ROE
- Median P/E
- Median D/E
- Total companies
- Median Revenue CAGR
- Debt-free companies count
- Sector breakdown
- Year selector
- Top quality companies

### Company Profile Screen

Implemented:

- Company search by name or ticker
- Company information
- Sector
- Sub-sector
- NSE ticker
- Company description
- ROE
- ROCE
- Net Profit Margin
- Debt-to-Equity
- Revenue CAGR 5yr
- FCF
- Revenue and Net Profit 10-year trend
- ROE and ROCE 10-year trend
- Pros and Cons
- Partial historical data handling
- N/A display for unavailable metrics

## Day 24 — Screener & Peer Comparison

### Screener

Implemented 10 interactive filters:

- ROE minimum
- D/E maximum
- FCF minimum
- Revenue CAGR minimum
- PAT CAGR minimum
- OPM minimum
- P/E maximum
- P/B maximum
- Dividend Yield minimum
- ICR minimum

Implemented six presets:

- Quality
- Value
- Growth
- Dividend
- Debt-Free
- Turnaround

Additional features:

- Live filtering
- Result count
- Composite quality score
- Financial metrics table
- CSV download

### Peer Comparison

Implemented:

- Peer group selection
- Company selection
- Company vs peer-group radar chart
- KPI comparison
- Peer average comparison
- Benchmark highlighting

## Day 25 — Trend, Sector, Capital Allocation & Reports

### Trend Analysis

Implemented:

- Company search
- Up to 3 metric selection
- 10-year trend chart
- Year-over-year percentage change
- Data-point annotations

### Sector Analysis

Implemented:

- Sector dropdown
- Revenue vs ROE bubble chart
- Market Cap bubble size
- Sub-sector classification
- Sector median KPI chart
- Company table

### Capital Allocation

Implemented:

- Capital allocation treemap
- Company grouping by capital allocation pattern
- Pattern selection
- Company list by selected pattern

Source:

```text
output/capital_allocation.csv
```

### Annual Reports

Implemented:

- Company search
- Company selection
- Available annual report years
- BSE annual report links
- Report unavailable status

## Day 26 — Valuation Module

Implemented:

```text
src/analytics/valuation.py
```

Input:

```text
data/raw/market_cap.xlsx
```

Calculated:

- FCF Yield
- Sector median P/E
- P/E vs sector median
- Valuation flags

Valuation rules:

```text
P/E > Sector Median × 1.5 → Caution
P/E < Sector Median × 0.7 → Discount
Otherwise → Fair
```

Generated:

```text
output/valuation_summary.xlsx
output/valuation_flags.csv
```

Valuation results for 92 companies:

```text
Fair        48
Discount    30
Caution     14
```

## Day 27 — Integration QA & Bug Fixes

Completed integration testing of all 8 Streamlit screens.

Tested companies across:

- Information Technology
- Financials
- Consumer Staples / FMCG
- Energy
- Healthcare

### Partial Data Testing

Tested companies with fewer than 10 years of data:

```text
JIOFIN       2 years
LICI         6 years
ADANIGREEN   8 years
HAL          8 years
IRFC         9 years
LODHA        9 years
```

JIOFIN was tested successfully with the message:

```text
Data available for 2 years. Some historical financial data may be unavailable.
```

Unavailable financial metrics are displayed as:

```text
N/A
```

### Screener QA

Tested:

- Minimum slider values
- Maximum slider values
- Zero-result scenarios
- All six screener presets

No application crash was observed.

### Chart QA

Checked dashboard charts for:

- Page-width overflow
- Clipped content
- Incorrect year-axis behaviour
- Responsive rendering

The ROE and ROCE year axis was corrected to display categorical year labels.

### Performance QA

Company Profile loading was tested with multiple companies.

The loading time remained below the required 3-second limit.

## Day 28 — Retro & Documentation

### Dashboard Run Instructions

Run the dashboard using:

```bash
streamlit run src/dashboard/app.py
```

### Dashboard Screens

### 1. Home

NIFTY100 overview with key financial KPIs, sector breakdown, year selection, and company analysis.

### 2. Company Profile

Company search, company information, financial KPIs, financial trends, and pros and cons.

### 3. Stock Screener

10 financial filters, 6 screening presets, live results, and CSV download.

### 4. Peer Comparison

Peer group selection, radar chart, company vs peer average, and KPI comparison.

### 5. Trend Analysis

Company search, up to 3 financial metrics, 10-year trends, and YoY analysis.

### 6. Sector Analysis

Sector selection, Revenue vs ROE bubble chart, sector median KPIs, and company table.

### 7. Capital Allocation

Treemap showing companies grouped by capital allocation patterns.

### 8. Annual Reports

Company search, available report years, BSE annual report links, and report availability status.

## Sprint 4 Retrospective

### UX Decisions

- Added company search using company name or NSE ticker.
- Added interactive financial filters and preset strategies.
- Used responsive Plotly charts.
- Displayed N/A for unavailable financial metrics.
- Added data availability messages for companies with limited history.
- Added Report unavailable status for inaccessible annual reports.

### Data Edge Cases

- Some companies have fewer than 10 years of historical data.
- Some financial metrics are unavailable.
- Some annual report links are unavailable.
- Some historical financial values contain extreme values.
- Missing data is handled without crashing.

### Performance Findings

- Company Profile loading time was below the required 3-second limit.
- Dashboard charts were checked for page-width overflow.
- Extreme screener filter values were tested successfully.

## Sprint 4 Deliverables

- src/dashboard/app.py
- src/dashboard/pages/01_home.py
- src/dashboard/pages/02_profile.py
- src/dashboard/pages/03_screener.py
- src/dashboard/pages/04_peers.py
- src/dashboard/pages/05_trends.py
- src/dashboard/pages/06_sectors.py
- src/dashboard/pages/07_capital.py
- src/dashboard/pages/08_reports.py
- src/dashboard/utils/db.py
- src/analytics/valuation.py
- output/valuation_summary.xlsx
- output/valuation_flags.csv
- output/capital_allocation.csv

## Sprint 4 Status

**Completed**

## Author

**Bhargavi**

NIFTY100 Financial Intelligence Platform

Sprint 1 – Data Foundation & ETL

Sprint 2 – Financial Ratio Engine

Sprint 3 - implemented the financial screener, peer analysis, radar charts, and peer comparison reports.