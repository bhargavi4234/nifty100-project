# NIFTY100 Financial Intelligence Platform

## Sprint 1 – Data Foundation & ETL

This project is the Sprint 1 implementation of the NIFTY100 Financial Intelligence Platform. The objective is to build a reliable data foundation by extracting, validating, and loading financial data into a SQLite database.

---

## Project Objectives

- Build an ETL pipeline for NIFTY100 financial data.
- Load data from multiple Excel source files.
- Validate data using 16 Data Quality (DQ) rules.
- Store validated data in a SQLite database.
- Generate audit and validation reports.
- Prepare the data foundation for future analytics and dashboard development.

---

## Project Structure

```
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
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   └── retrospective.md
│
├── sql/
│   └── exploratory_queries.sql
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
├── notebooks/
│
├── README.md
├── requirements.txt
├── Makefile
└── .env
```

---

## Technologies Used

- Python 3.13
- Pandas
- NumPy
- SQLite
- OpenPyXL
- Pytest
- python-dotenv

---

## Sprint 1 Tasks Completed

### Day 01 – Environment Setup

- Project structure created
- Virtual environment configured
- Required libraries installed
- Environment variables configured
- Makefile created

### Day 02 – Excel Loader & Normaliser

- Excel loader developed
- Year normalization implemented
- Ticker normalization implemented
- Unit tests created

### Day 03 – Data Quality Validation

Implemented all 16 DQ Rules:

- DQ-01 Primary Key Uniqueness
- DQ-02 Company-Year Uniqueness
- DQ-03 Foreign Key Integrity
- DQ-04 Balance Sheet Validation
- DQ-05 Operating Profit Margin Check
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
- DQ-16 Data Coverage Validation

Validation report generated:

```
output/validation_failures.csv
```

---

### Day 04 – SQLite Database

- SQLite schema created
- Primary Keys implemented
- Foreign Keys implemented
- PRAGMA foreign_keys enabled

---

### Day 05 – Full Data Load

Successfully loaded all project datasets.

Generated:

- load_audit.csv
- SQLite database

Foreign key validation:

```
PRAGMA foreign_key_check

Result:
0 Violations
```

---

### Day 06 – Manual Review

Completed manual data review.

Verified:

- Five random companies
- Year coverage
- Companies with less than five years of data
- Loader verification
- Database reload
- Foreign key validation

---

### Day 07 – Sprint Wrap-Up

Completed:

- exploratory_queries.sql
- Sprint retrospective
- Database demonstration
- Unit testing

Unit Test Results

```
38 Passed
0 Failed
```

---

## Database Tables

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

## Output Files

- load_audit.csv
- validation_failures.csv
- retrospective.md

---

## SQL Queries

Exploratory SQL queries are available in:

```
sql/exploratory_queries.sql
```

---

## Testing

Run unit tests:

```bash
pytest
```

Result:

```
38 Passed
```

---

## Run Loader

```bash
python src/etl/loader.py
```

---

## Validate Data

```bash
python src/etl/validator.py
```

---

## Manual Review

```bash
python src/etl/manual_review.py
```

---

## Foreign Key Check

```bash
python src/etl/fk_check.py
```

---

## Sprint 1 Outcome

- ETL pipeline completed
- SQLite database created
- Data quality validation completed
- Audit reports generated
- Manual review completed
- Unit tests passed
- Sprint 1 successfully completed

---