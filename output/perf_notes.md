# Day 43 — Performance Testing Notes

## 1. SQLite Query Optimisation

Indexes were added to improve query performance.

### Indexed tables

- financial_ratios: company_id, year
- profitandloss: company_id, year
- balancesheet: company_id, year
- cashflow: company_id, year
- market_cap: company_id, year
- stock_prices: company_id, date
- sectors: company_id
- peer_groups: company_id
- documents: company_id, year

All indexes were successfully created and verified using SQLite PRAGMA index_list().

---

## 2. Concurrent Screener API Load Test

Tested 10 concurrent requests to:

`GET /api/v1/screener?min_roe=15`

### Results

- Concurrent requests: 10
- Successful HTTP 200 responses: 10/10
- Total elapsed time: 0.0443 seconds
- Maximum individual response time: 0.0432 seconds
- Target: all requests complete within 10 seconds
- Result: PASS

No significant performance bottleneck was observed.

---

## 3. Company Profile Performance

Five company profile requests were tested.

| Company | Response Time |
|---|---:|
| ABB | 0.0057 s |
| ADANIENSOL | 0.0036 s |
| ADANIENT | 0.0265 s |
| ADANIGREEN | 0.0144 s |
| ADANIPORTS | 0.0035 s |

Average response time: 0.0107 seconds

Maximum response time: 0.0265 seconds

Target: less than 3 seconds per company.

Result: PASS

No significant profile performance bottleneck was observed.

---

## 4. End-to-End Service Test

FastAPI and Streamlit were started simultaneously.

- FastAPI: port 8000
- Streamlit: port 8501

### Results

FastAPI health endpoint:

HTTP 200 — PASS

Streamlit application:

HTTP 200 — PASS

Both services operated simultaneously without port conflicts.

---

## 5. Performance Bottlenecks

No significant performance bottlenecks were identified during Day 43 testing.

SQLite indexes were added to frequently queried company/year/date columns to improve database lookup performance.

Overall Day 43 performance testing: PASS.