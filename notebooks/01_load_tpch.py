import duckdb
import os

# Create database file in project root
db_path = "tpch.duckdb"
con = duckdb.connect(db_path)

# Load TPC-H extension and generate data
# sf=1 means ~1GB of data, plenty for our purposes
con.execute("INSTALL tpch")
con.execute("LOAD tpch")
con.execute("CALL dbgen(sf=1)")

# Confirm tables loaded
tables = con.execute("SHOW TABLES").fetchall()
print("✅ Tables loaded:")
for t in tables:
    print(f"   - {t[0]}")

# Preview row counts
print("\n✅ Row counts:")
for t in tables:
    count = con.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"   - {t[0]}: {count:,} rows")

con.close()
print("\n✅ DuckDB database created at:", os.path.abspath(db_path))
