import duckdb
import pandas as pd


import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tpch.duckdb")

def execute_sql(sql: str, limit: int = 100) -> dict:
    """Execute SQL against DuckDB and return results."""

    try:
        con = duckdb.connect(DB_PATH, read_only=True)

        # Safety check — only allow SELECT statements
        sql_clean = sql.strip().upper()
        if not sql_clean.startswith("SELECT") and not sql_clean.startswith("WITH"):
            return {
                "success": False,
                "error": "Only SELECT statements are allowed",
                "df": None,
                "row_count": 0
            }

        df = con.execute(sql).df()
        con.close()

        return {
            "success": True,
            "df": df,
            "row_count": len(df),
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "df": None,
            "row_count": 0,
            "error": str(e)
        }