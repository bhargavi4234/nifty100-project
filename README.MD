# NIFTY100 Financial Intelligence Platform

## Sprint 1, Sprint 2, Sprint 3, Sprint 4, Sprint 5 & Sprint 6 – Data Foundation, Financial Analytics, Peer Analysis, Streamlit Dashboard, Valuation, NLP & Automated Reporting
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
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
│       └── nifty100.db
│
├── docs/
│   └── analyst_guide.pdf
│
├── src/
│   ├── etl/
│   │   ├── ingestion.py
│   │   ├── normaliser.py
│   │   ├── validator.py
│   │   └── loader.py
│   │
│   ├── analytics/
│   │   ├── ratios.py
│   │   ├── cagr.py
│   │   ├── cashflow_intelligence.py
│   │   └── distress_detector.py
│   │
│   ├── screener/
│   │   ├── screener.py
│   │   └── presets.py
│   │
│   ├── nlp/
│   │   ├── analyst_guide_parser.py
│   │   └── pros_cons_generator.py
│   │
│   └── reports/
│       ├── generate_tearsheets.py
│       └── generate_sector_reports.py
│
├── tests/
│   ├── test_normaliser.py
│   ├── test_validator.py
│   ├── test_ratios.py
│   ├── test_cagr.py
│   ├── test_cashflow.py
│   ├── test_analysis_parser.py
│   ├── test_pros_cons.py
│   ├── test_cashflow_intelligence.py
│   └── test_distress.py
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   ├── screener_output.xlsx
│   ├── peer_comparison.xlsx
│   ├── capital_allocation.csv
│   ├── analysis_parsed.csv
│   ├── pros_cons_generated.csv
│   ├── cashflow_intelligence.xlsx
│   └── distress_alerts.csv
│
├── reports/
│   ├── radar_charts/
│   ├── tearsheets/
│   │   └── *.pdf
│   │
│   └── sector/
│       └── *.pdf
│
├── config/
│   └── screener.yaml
│
├── notebooks/
│   └── ...
│
├── requirements.txt
├── README.md
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


## Sprint 5 — NLP, Cash Flow Intelligence, Capital Allocation & Reporting

### Day 29 — NLP Analysis Text Parser
- Created `src/nlp/parser.py`
- Parsed financial analysis text using regex.
- Extracted:
  - Compounded Sales Growth
  - Compounded Profit Growth
  - Stock Price CAGR
  - ROE
- Generated `output/analysis_parsed.csv`
- Generated `output/parse_failures.csv`
- Cross-validated parsed CAGR values against the Ratio Engine.
- Flagged divergence greater than 5% for manual review.

### Day 30 — NLP Auto Pros/Cons Generator
- Created `src/nlp/pros_cons_generator.py`
- Implemented 12 Pro rules and 12 Con rules.
- Added confidence scoring for generated signals.
- Generated `output/pros_cons_generated.csv`
- Tested against the 92-company universe.
- Documented unavailable `CON_11` because EBITDA and cash-balance data are not available in the current database.

### Day 31 — Cash Flow Intelligence
- Created `src/analytics/cashflow_kpis.py`
- Implemented CFO Quality Score.
- Implemented CapEx Intensity analysis.
- Added Distress Signal detection.
- Added Deleveraging detection.
- Generated `output/cashflow_intelligence.xlsx`
- Generated `output/distress_alerts.csv`
- Processed all 92 companies.

### Day 32 — Capital Allocation Report
- Created `src/analytics/capital_allocation_report.py`
- Verified Capital Allocation data against the current 92-company database.
- Generated latest-year pattern distribution.
- Added capital allocation information to `cashflow_intelligence.xlsx`
- Generated `output/pattern_changes.csv`
- Generated `output/capital_allocation_distribution.csv`
- Generated `output/capital_allocation_verification.csv`
- Documented ATGL's missing cash-flow data.

### Day 33 — PDF Tearsheet Template
- Created `src/reports/tearsheet.py`
- Implemented a 2-page company tearsheet using ReportLab.
- Added:
  - Company header
  - 6 KPI tiles
  - Revenue and Net Profit charts
  - ROE and ROCE trend chart
  - Balance Sheet composition
  - Cash Flow waterfall
  - Pros and Cons
  - Capital Allocation badge
- Tested with:
  - TCS
  - HDFCBANK
  - RELIANCE
  - SUNPHARMA
  - TATASTEEL
- All 5 test tearsheets passed.

### Day 34 — Batch Report Generation
- Created batch tearsheet generation for the 92-company universe.
- Generated 91 company tearsheets.
- JIOFIN was skipped because it had fewer than 3 years of data.
- Generated sector reports for all 10 actual sectors in the database.
- Generated `output/skipped_tearsheets.csv`
- Generated `output/sector_report_summary.csv`
- Visually checked 5 batch-generated tearsheets.
- No major overflow, blank-page, or chart-rendering issues were found.

### Day 35 — Portfolio Summary PDF & Sprint Review
- Created `src/reports/portfolio_summary.py`
- Generated `reports/portfolio/portfolio_summary.pdf`
- Generated 92 pages — one page for each company.
- Companies are arranged alphabetically by ticker.
- Each page contains:
  - Company name
  - Sector
  - Top 6 KPIs
  - Latest and previous values
  - Trend arrows
- Trend indicators:
  - ↑ Improved
  - ↓ Declined
  - → Flat within 2%
- Verified the PDF contains exactly 92 pages.
- Created `reports/Sprint5_Retrospective.md`
- Prepared Sprint 5 demo materials.

### Sprint 5 Deliverables

- `src/nlp/parser.py`
- `src/nlp/pros_cons_generator.py`
- `src/analytics/cashflow_kpis.py`
- `src/analytics/capital_allocation_report.py`
- `src/reports/tearsheet.py`
- `src/reports/batch_reports.py`
- `src/reports/portfolio_summary.py`
- `output/analysis_parsed.csv`
- `output/parse_failures.csv`
- `output/pros_cons_generated.csv`
- `output/cashflow_intelligence.xlsx`
- `output/distress_alerts.csv`
- `output/capital_allocation_distribution.csv`
- `output/capital_allocation_verification.csv`
- `output/pattern_changes.csv`
- `output/skipped_tearsheets.csv`
- `output/sector_report_summary.csv`
- `reports/tearsheets/`
- `reports/sector/`
- `reports/portfolio/portfolio_summary.pdf`
- `reports/Sprint5_Retrospective.md`

### Sprint 5 Retrospective

**Completed:**  
Sprint 5 successfully added NLP parsing, automated Pros/Cons generation, Cash Flow Intelligence, Capital Allocation analysis, company tearsheets, batch reporting, sector reporting, and portfolio-level reporting.

**Challenges:**  
Some companies have incomplete financial data. ATGL has no current cash-flow/financial-ratio data, JIOFIN has fewer than 3 years of data, and CON_11 could not be evaluated because EBITDA and cash-balance data are unavailable. The database contains 10 actual sectors rather than the 11 mentioned in the task specification.

**Future Improvements:**  
Add missing financial data, improve handling of incomplete company histories, add EBITDA and cash-balance data, improve PDF validation, and expand portfolio-level analytics.

### Sprint 5 Status

** COMPLETE — Days 29–35**

### Sprint 5 Data / Specification Notes

- **LICI:** No Con signal was generated because none of the 12 defined Con rules is supported by its latest-year data. Therefore, Pros/Cons coverage is 92/92 for Pros and 91/92 for Cons.
- **JIOFIN:** The company has only 2 years of available data and was skipped from batch tearsheet generation as required by the Day 34 rule to skip companies with fewer than 3 years of data. Therefore, 91 company tearsheets were generated.
- **Sector Reports:** The current database contains 10 broad-sector categories covering all 92 companies, so 10 sector PDFs were generated rather than inventing an 11th sector.
- **Tearsheet File Size:** All 91 generated tearsheets are greater than 30 KB.
- **Visual Validation:** 5 tearsheets were visually reviewed and passed without major overflow, blank-page, or chart-rendering issues.
- **Cash Flow Intelligence:** `cashflow_intelligence.xlsx` contains exactly 92 rows and all required columns.
- **Sector Report Module:** `src/reports/sector_report.py` was created and successfully tested.

# Sprint 6 – NLP Intelligence, Cash-Flow Intelligence & Automated Reports

## Sprint 6 Overview

Sprint 6 extends the Nifty100 financial analytics platform with document intelligence, NLP-based analysis, cash-flow quality assessment, financial distress detection, and automated reporting.

### Objectives

* Parse the Analyst Guide PDF
* Extract structured CAGR and analysis data
* Generate company Pros & Cons
* Build cash-flow intelligence
* Detect financial distress signals
* Generate automated company tear sheets
* Generate sector-level reports
* Run Sprint 6 tests

---

# Day 36 – Analyst Guide PDF Parsing

## Objective

Extract useful financial information from the Analyst Guide PDF and convert unstructured text into structured data.

## Tasks

* Read the Analyst Guide PDF using `pypdf`
* Extract company sections
* Identify financial analysis text
* Extract CAGR-related information
* Normalize extracted values
* Store structured results in CSV format

## Input

```text
docs/analyst_guide.pdf
```

## Run

```powershell
python src/nlp/analyst_guide_parser.py
```

## Test

```powershell
python -m pytest tests/test_analysis_parser.py -v
```

## Deliverable

```text
output/analysis_parsed.csv
```

---

# Day 37 – Automated Pros & Cons Generation

## Objective

Generate structured Pros and Cons for the companies using financial analysis and fundamental data.

## Tasks

* Read company financial data
* Analyze financial strengths
* Identify financial risks
* Generate Pros
* Generate Cons
* Standardize the generated results
* Cover the complete company universe

## Run

```powershell
python src/nlp/pros_cons_generator.py
```

## Test

```powershell
python -m pytest tests/test_pros_cons.py -v
```

## Deliverable

```text
output/pros_cons_generated.csv
```

---

# Day 38 – Cash-Flow Intelligence

## Objective

Analyze the quality and sustainability of company cash flows.

## Tasks

Calculate:

* CFO Quality
* CFO/PAT
* Free Cash Flow
* CapEx Intensity
* Cash conversion
* Cash-flow warning signals

## Formulas

```text
CFO Quality = CFO / PAT
```

```text
CapEx Intensity = CapEx / Revenue
```

```text
FCF = CFO - CapEx
```

## Run

```powershell
python src/analytics/cashflow_intelligence.py
```

## Test

```powershell
python -m pytest tests/test_cashflow_intelligence.py -v
```

## Deliverable

```text
output/cashflow_intelligence.xlsx
```

---

# Day 39 – Financial Distress Detection

## Objective

Identify companies showing potential financial distress or deterioration.

## Distress Indicators

* High Debt/Equity
* Weak Interest Coverage
* Negative Free Cash Flow
* Weak CFO/PAT conversion
* Profit decline
* Revenue decline
* EPS decline
* Persistent financial deterioration

## Distress Scoring

```text
Debt warning       → +1
Weak ICR           → +1
Negative FCF       → +1
Weak CFO/PAT       → +1
Profit decline     → +1
Revenue decline    → +1
EPS decline        → +1
```

A higher score indicates a higher level of potential financial risk.

## Run

```powershell
python src/analytics/distress_detector.py
```

## Test

```powershell
python -m pytest tests/test_distress.py -v
```

## Deliverable

```text
output/distress_alerts.csv
```

---

# Day 40 – Automated Company Tear Sheets

## Objective

Generate an automated PDF tear sheet for each company.

## Tear Sheet Contents

Each tear sheet contains:

* Company name
* Sector
* Market information
* Financial ratios
* Revenue growth
* Profit growth
* ROE
* ROCE
* Debt/Equity
* Interest Coverage
* Cash-flow quality
* Free Cash Flow
* Pros
* Cons
* Distress indicators
* Overall financial interpretation

## Run

```powershell
python src/reports/generate_tearsheets.py
```

## Deliverable

```text
reports/tearsheets/
```

Approximately **92 company PDF reports** are generated.

---

# Day 41 – Sector-Level Reports

## Objective

Aggregate company-level financial intelligence into sector-level reports.

## Sector Report Contents

* Sector overview
* Company count
* Financial-ratio summary
* Growth characteristics
* Profitability
* Debt profile
* Cash-flow quality
* Distress companies
* Strong companies
* Sector-level observations

## Run

```powershell
python src/reports/generate_sector_reports.py
```

## Deliverable

```text
reports/sector/
```

Approximately **11 sector PDF reports** are generated.

---

# Day 42 – Integration & Final Testing

## Objective

Run the complete Sprint 6 pipeline and ensure all components work together.

## Complete Pipeline

```powershell
python src/nlp/analyst_guide_parser.py
python src/nlp/pros_cons_generator.py
python src/analytics/cashflow_intelligence.py
python src/analytics/distress_detector.py
python src/reports/generate_tearsheets.py
python src/reports/generate_sector_reports.py
```

## Run Full Test Suite

```powershell
python -m pytest tests/ -v
```

## Short Test Summary

```powershell
python -m pytest tests/ -q
```

---

# Sprint 6 Deliverables

```text
output/
├── pros_cons_generated.csv
├── analysis_parsed.csv
├── cashflow_intelligence.xlsx
└── distress_alerts.csv

reports/
├── tearsheets/
│   └── ~92 company PDFs
│
└── sector/
    └── ~11 sector PDFs
```

---
sprint-6 status
**completed**



## Author

**Bhargavi**

**NIFTY100 Financial Intelligence Platform**

- **Sprint 1** – Data Foundation & ETL
- **Sprint 2** – Financial Ratio Engine
- **Sprint 3** – Financial Screener, Peer Analysis, Radar Charts & Peer Comparison Reports
- **Sprint 4** – Streamlit Dashboard & Interactive Financial Analytics
- **Sprint 5** – Valuation, Advanced Analytics & Financial Intelligence
- **Sprint 6** – NLP, Cash-Flow Intelligence, Distress Detection & Automated Reporting