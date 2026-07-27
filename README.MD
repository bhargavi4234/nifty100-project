# NIFTY100 Financial Intelligence Platform

## Sprint 1 & Sprint 2 – Data Foundation and Financial Analytics

### Project Overview

The **NIFTY100 Financial Intelligence Platform** is designed to build a reliable financial analytics platform for NIFTY100 companies. The project extracts financial data from multiple Excel source files, validates it using Data Quality (DQ) rules, stores the validated data in a SQLite database, and generates advanced financial ratios for analytics and company screening.

The project is divided into two sprints:

- **Sprint 1** established the ETL pipeline, database, and data validation framework.
- **Sprint 2** implemented financial ratio calculations, CAGR analysis, company screening, and financial analytics.

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

## Author

**Bhargavi**

NIFTY100 Financial Intelligence Platform

Sprint 1 – Data Foundation & ETL

Sprint 2 – Financial Ratio Engine