import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "db", "nifty100.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

violations = cursor.execute("PRAGMA foreign_key_check;").fetchall()

if len(violations) == 0:
    print("FK Check: PASSED (0 violations)")
else:
    print(f"FK Check: FAILED ({len(violations)} violations)")
    for row in violations:
        print(row)

conn.close()
