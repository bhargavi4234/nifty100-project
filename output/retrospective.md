# Sprint 1 Retrospective

## What Went Well
- Successfully developed the ETL pipeline for loading Nifty 100 financial data into SQLite.
- Created the database schema and loaded all required datasets.
- Implemented and validated 16 Data Quality (DQ) rules.
- Generated load audit and validation reports.
- Completed manual data quality review.
- All unit tests passed successfully (38/38).
- Foreign key validation passed with zero violations.

## Challenges
- Some source files contained invalid company IDs, causing foreign key issues.
- Required additional validation and filtering before loading data.

## Improvements
- Enhance the loader to automatically handle missing reference records.
- Increase automated test coverage.
- Add logging and better error handling.

## Outcome
Sprint 1 was completed successfully with a working ETL pipeline, validated SQLite database, and successful unit test execution.


# Sprint 2 Retrospective

## Sprint Objective

The objective of Sprint 2 was to calculate key financial ratios for Nifty 100 companies, validate the results, and store the computed KPIs in the SQLite database.

## Work Completed

- Implemented profitability ratio calculations (ROE, ROCE, Net Profit Margin, Operating Profit Margin).
- Implemented leverage ratios (Debt-to-Equity, Interest Coverage).
- Implemented cash flow metrics (Free Cash Flow and CFO Quality Score).
- Calculated 5-year Revenue, PAT and EPS CAGR.
- Added Composite Quality Score for each company.
- Populated the financial_ratios table successfully.

## Formula Decisions

- ROE = Net Profit / Shareholders' Equity
- ROCE = EBIT / Capital Employed
- Free Cash Flow = Operating Cash Flow − Investing Cash Flow
- CAGR calculated using a rolling 5-year period.
- Composite Quality Score combines profitability, growth, leverage and cash flow quality.

## Edge Case Handling

- Missing companies in companies.xlsx were logged as **Data source issue**.
- Moderate differences between calculated and source values were logged as **Version difference**.
- Significant differences (>5%) were logged as **Formula discrepancy**.
- All anomalies were recorded in output/ratio_edge_cases.log for audit purposes.

## Testing

- All analytics unit tests executed successfully.
- Total Tests Passed: 55
- Failed Tests: 0

## Lessons Learned

- Financial ratios can differ across data providers due to different calculation methodologies.
- Maintaining detailed logs simplifies debugging and validation.
- Automated unit tests improve confidence in financial calculations.
- Using SQLite provides a simple and efficient storage solution for analytics data.

## Sprint Outcome

Sprint 2 objectives were successfully completed. Financial KPIs were calculated, validated, tested, and stored successfully for further analytics and screening.