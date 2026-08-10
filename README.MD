# NIFTY100 Financial Intelligence Platform

## Sprint 1, Sprint 2 & Sprint 3 – Data Foundation, Financial Analytics and Peer Analysis

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

```text
nifty100_project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
│       └── nifty100.db
│
├── db/
│   └── schema.sql
│
├── notebooks/
│   └── exploratory_queries.sql
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   ├── ratio_edge_cases.log
│   └── retrospective.md
│
├── src/
│   ├── etl/
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── normaliser.py
│   │   ├── manual_review.py
│   │   └── fk_check.py
│   │
│   └── analytics/
│       ├── ratios.py
│       ├── cagr.py
│       ├── populate_financial_ratios.py
│       └── __init__.py
│
├── tests/
│   ├── etl/
│   └── analytics/
│
├── README.md
├── requirements.txt
├── Makefile
└── .env
```

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


## Author

**Bhargavi**

NIFTY100 Financial Intelligence Platform

Sprint 1 – Data Foundation & ETL

Sprint 2 – Financial Ratio Engine

Sprint 3 - implemented the financial screener, peer analysis, radar charts, and peer comparison reports.