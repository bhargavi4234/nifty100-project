# Sprint 5 Retrospective

## Sprint Overview

Sprint 5 covered Days 29–35 and focused on NLP analysis, financial intelligence,
capital allocation, automated reporting, and portfolio-level reporting.

## Completed Work

### Day 29 — NLP Analysis Text Parser
- Implemented regex-based parsing of analysis text fields.
- Parsed compounded sales growth, compounded profit growth, stock price CAGR, and ROE.
- Generated `output/analysis_parsed.csv`.
- Generated `output/parse_failures.csv`.
- Cross-validated parsed CAGR values against the Ratio Engine.
- Flagged divergence greater than 5% for manual review.

### Day 30 — Auto Pros/Cons Generator
- Implemented 12 Pro rules and 12 Con rules.
- Added confidence scoring.
- Generated `output/pros_cons_generated.csv`.
- Verified coverage across the 92-company universe.
- Documented unavailable CON_11 because EBITDA and cash-balance data are not available.

### Day 31 — Cash Flow Intelligence
- Implemented CFO quality analysis.
- Implemented CapEx intensity analysis.
- Added distress signal detection.
- Added deleveraging detection.
- Generated `output/cashflow_intelligence.xlsx`.
- Generated `output/distress_alerts.csv`.

### Day 32 — Capital Allocation Report
- Verified capital allocation coverage against the current database.
- Generated latest-year pattern distribution.
- Added capital allocation information to the cash-flow workbook.
- Generated year-over-year pattern changes.
- Generated `output/pattern_changes.csv`.
- Documented ATGL's missing cash-flow data.

### Day 33 — PDF Tearsheet Template
- Implemented a two-page company tearsheet using ReportLab.
- Added KPI tiles, financial charts, balance-sheet composition,
  cash-flow visualization, Pros/Cons, and capital allocation.
- Tested the template on TCS, HDFCBANK, RELIANCE, SUNPHARMA, and TATASTEEL.
- All five test tearsheets generated successfully.
- Visually verified the test PDFs for layout and overflow.

### Day 34 — Batch Report Generation
- Generated company tearsheets for the current company universe.
- Generated 91 tearsheets.
- JIOFIN was skipped because it had fewer than three years of data.
- Generated sector reports for all 10 sectors present in the database.
- Generated `output/skipped_tearsheets.csv`.
- Generated `output/sector_report_summary.csv`.
- Visually checked five batch-generated tearsheets.

### Day 35 — Portfolio Summary
- Generated `reports/portfolio/portfolio_summary.pdf`.
- Generated one page per company for all 92 companies.
- Sorted companies alphabetically by ticker.
- Added six KPIs and trend indicators.
- Verified that the portfolio PDF contains exactly 92 pages.

## What Went Well

- New analytics modules were successfully integrated with the existing SQLite database.
- Automated validation helped identify missing or incomplete data.
- The PDF reporting pipeline successfully generated individual and portfolio-level reports.
- Reporting was tested using companies from different sectors.
- The portfolio summary provides a consolidated view of the 92-company universe.

## Challenges Encountered

- Some companies have incomplete financial data.
- ATGL has missing financial-ratio and cash-flow data in the current database.
- JIOFIN has fewer than three years of data and was skipped from batch tearsheet generation.
- EBITDA and cash-balance fields are unavailable, preventing full implementation of CON_11.
- The database contains 10 actual broad sectors, while the task specification mentioned 11 sector PDFs.

## Improvements / Future Work

- Add missing financial data where available.
- Improve handling of companies with incomplete historical records.
- Add EBITDA and cash-balance data to support additional leverage analysis.
- Improve automated PDF layout and visual validation.
- Extend portfolio reporting with additional charts and advanced analytics.
- Review and standardize sector classification if an 11-sector structure is required.

## Sprint Conclusion

Sprint 5 successfully extended the project from financial analytics into
NLP-based insights, cash-flow intelligence, capital-allocation analysis,
and automated PDF reporting. The sprint produced company-level,
sector-level, and portfolio-level outputs for the Nifty 100 company universe
while documenting known data limitations.
