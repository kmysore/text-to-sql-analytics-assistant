import sys
sys.path.append(".")

import yaml
import json
import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "tpch.duckdb"
TEST_CASES_PATH = "evals/test_cases/test_cases.yaml"
GOLD_RESULTS_PATH = "evals/test_cases/gold_results.json"

def generate_gold_results():
    # Load test cases
    with open(TEST_CASES_PATH, "r") as f:
        data = yaml.safe_load(f)

    test_cases = data["test_cases"]
    con = duckdb.connect(DB_PATH, read_only=True)
    gold_results = {}
    errors = []

    print(f"Generating gold results for {len(test_cases)} test cases...\n")

    for tc in test_cases:
        test_id = tc["id"]
        try:
            df = con.execute(tc["gold_sql"]).df()

            # Store as list of dicts for JSON serialization
            gold_results[test_id] = {
                "rows": df.to_dict(orient="records"),
                "row_count": len(df),
                "columns": list(df.columns)
            }
            print(f"✅ {test_id}: {len(df)} rows")

        except Exception as e:
            errors.append(test_id)
            print(f"❌ {test_id}: {str(e)}")

    con.close()

    # Save gold results
    with open(GOLD_RESULTS_PATH, "w") as f:
        json.dump(gold_results, f, indent=2, default=str)

    print(f"\n✅ Gold results saved to {GOLD_RESULTS_PATH}")
    print(f"✅ {len(gold_results)} passed, ❌ {len(errors)} failed")
    if errors:
        print(f"Failed: {errors}")

if __name__ == "__main__":
    generate_gold_results()