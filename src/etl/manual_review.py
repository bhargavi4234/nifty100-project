import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "db", "nifty100.db")

conn = sqlite3.connect(DB_PATH)

print("=" * 60)
print("DAY 06 - DATA QUALITY MANUAL REVIEW")
print("=" * 60)

# --------------------------------------------------
# 1. Five Random Companies
# --------------------------------------------------

print("\n1. Five Random Companies\n")

query = """
SELECT id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5;
"""

print(pd.read_sql(query, conn))

# --------------------------------------------------
# 2. Year Coverage
# --------------------------------------------------

print("\n2. Year Coverage\n")

query = """
SELECT
    company_id,
    MIN(year) AS first_year,
    MAX(year) AS last_year,
    COUNT(DISTINCT year) AS years_available
FROM profitandloss
GROUP BY company_id
ORDER BY company_id;
"""

coverage = pd.read_sql(query, conn)

print(coverage)

# --------------------------------------------------
# 3. Companies with Less Than 5 Years
# --------------------------------------------------

print("\n3. Companies with Less Than 5 Years of Data\n")

less_than_five = coverage[
    coverage["years_available"] < 5
]

print(less_than_five)

# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\nTotal Companies Reviewed:", len(coverage))
print("Companies with <5 years:", len(less_than_five))

conn.close()