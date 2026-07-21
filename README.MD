# NIFTY100 Financial Intelligence Platform

## Sprint 1 – Data Foundation & ETL

### Project Overview

The **NIFTY100 Financial Intelligence Platform** is designed to build a reliable data foundation for financial analytics. The project extracts financial data from multiple Excel source files, validates it using Data Quality (DQ) rules, and loads the validated data into a SQLite database for future analysis and dashboard development.

---

# Sprint Goal

By the end of Sprint 1, the project successfully:

- Built an ETL pipeline for financial data.
- Loaded data from 12 Excel source files.
- Created a validated SQLite database (`nifty100.db`).
- Implemented 16 Data Quality rules.
- Generated validation and audit reports.
- Established the foundation for future analytics and dashboard modules.

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
│   └── retrospective.md
│
├── src/
│   └── etl/
│       ├── loader.py
│       ├── validator.py
│       ├── normaliser.py
│       ├── manual_review.py
│       └── fk_check.py
│
├── tests/
│   └── etl/
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

---

# Testing

Run all unit tests:

```bash
pytest
```

Result:

```text
======================================
38 passed in 0.60s
======================================
```

---

# Key Outputs

- SQLite database created successfully.
- Load audit generated successfully.
- Validation report generated successfully.
- Foreign key validation passed.
- Manual review completed.
- Unit tests passed without failures.

---

# Sprint 1 Outcome

Sprint 1 successfully established the data foundation for the **NIFTY100 Financial Intelligence Platform**.

Achievements:

- Built a complete ETL pipeline.
- Loaded financial data from multiple Excel source files.
- Implemented 16 Data Quality validation rules.
- Created a validated SQLite database.
- Generated audit and validation reports.
- Performed manual data quality review.
- Passed all unit tests (38/38).
- Verified database integrity with zero foreign key violations.

The project is now ready for **Sprint 2**, which will build advanced analytics, APIs, and dashboard features on top of this data foundation.

---

## Author

**Bhargavi**

Sprint 1 – Data Foundation & ETL  
NIFTY100 Financial Intelligence Platform