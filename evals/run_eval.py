import sys
sys.path.append(".")

import yaml
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from app.generate_sql import generate_sql, load_semantic_context
from app.execute_sql import execute_sql
from evals.scoring import score_result

# Paths
TEST_CASES_PATH = "evals/test_cases/test_cases.yaml"
GOLD_RESULTS_PATH = "evals/test_cases/gold_results.json"
RESULTS_DIR = Path("evals/results")
RESULTS_DIR.mkdir(exist_ok=True)


def run_eval(max_questions: int = None):
    """
    Run the full evaluation harness.
    Generates SQL for each test case, executes it,
    scores against gold results, and saves a report.
    """

    # Load test cases
    with open(TEST_CASES_PATH) as f:
        data = yaml.safe_load(f)
    test_cases = data["test_cases"]

    # Load gold results
    with open(GOLD_RESULTS_PATH) as f:
        gold_results = json.load(f)

    # Load semantic context once
    context = load_semantic_context()

    # Optionally limit questions for quick testing
    if max_questions:
        test_cases = test_cases[:max_questions]

    print(f"\n{'='*60}")
    print(f"Running eval on {len(test_cases)} questions")
    print(f"{'='*60}\n")

    results = []

    for tc in test_cases:
        test_id = tc["id"]
        question = tc["question"]
        difficulty = tc["difficulty"]
        category = tc["category"]
        gold = gold_results.get(test_id, {})

        print(f"[{test_id}] {question[:60]}...")

        # Step 1: Generate SQL
        gen_result = generate_sql(question, context)

        if not gen_result["success"]:
            results.append({
                "id": test_id,
                "difficulty": difficulty,
                "category": category,
                "question": question,
                "generated_sql": None,
                "execution_success": False,
                "result_match": False,
                "row_count_match": False,
                "error_category": "generation_failed",
                "error": gen_result.get("error"),
                "gold_row_count": gold.get("row_count", 0),
                "result_row_count": 0,
                "tokens_used": 0
            })
            print(f"  ❌ Generation failed: {gen_result.get('error')}")
            continue

        sql = gen_result["sql"]

        # Step 2: Execute SQL
        exec_result = execute_sql(sql)

        # Step 3: Score
        score = score_result(
            gold_rows=gold.get("rows", []),
            gold_columns=gold.get("columns", []),
            result_df=exec_result.get("df"),
            error=exec_result.get("error"),
            execution_success=exec_result["success"]
        )

        # Log result
        status = "✅" if score["result_match"] else "⚠️" if score["execution_success"] else "❌"
        print(f"  {status} exec={score['execution_success']} match={score['result_match']} rows={score['result_row_count']}/{score['gold_row_count']}")

        results.append({
            "id": test_id,
            "difficulty": difficulty,
            "category": category,
            "question": question,
            "generated_sql": sql,
            "execution_success": score["execution_success"],
            "result_match": score["result_match"],
            "row_count_match": score["row_count_match"],
            "error_category": score["error_category"],
            "error": exec_result.get("error"),
            "gold_row_count": score["gold_row_count"],
            "result_row_count": score["result_row_count"],
            "tokens_used": gen_result.get("tokens_used", 0)
        })

    # Build summary
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"eval_{timestamp}.csv"
    df.to_csv(output_path, index=False)

    # Print report
    print(f"\n{'='*60}")
    print("EVAL RESULTS SUMMARY")
    print(f"{'='*60}")

    total = len(df)
    exec_success = df["execution_success"].sum()
    result_match = df["result_match"].sum()

    print(f"\nOverall:")
    print(f"  Total questions:     {total}")
    print(f"  Execution success:   {exec_success}/{total} ({100*exec_success/total:.1f}%)")
    print(f"  Result match:        {result_match}/{total} ({100*result_match/total:.1f}%)")

    print(f"\nBy difficulty:")
    for diff in ["easy", "medium", "hard"]:
        subset = df[df["difficulty"] == diff]
        if len(subset) > 0:
            match = subset["result_match"].sum()
            print(f"  {diff.capitalize():8} {match}/{len(subset)} ({100*match/len(subset):.1f}%)")

    print(f"\nBy category:")
    for cat in df["category"].unique():
        subset = df[df["category"] == cat]
        match = subset["result_match"].sum()
        print(f"  {cat:20} {match}/{len(subset)} ({100*match/len(subset):.1f}%)")

    print(f"\nFailure breakdown:")
    failures = df[df["result_match"] == False]
    if len(failures) > 0:
        error_counts = failures["error_category"].value_counts()
        for error, count in error_counts.items():
            print(f"  {error:25} {count} cases")
    else:
        print("  No failures!")

    print(f"\n✅ Full results saved to {output_path}")
    print(f"Total tokens used: {df['tokens_used'].sum():,}")
    print(f"Estimated cost: ~${df['tokens_used'].sum() * 0.000003:.2f}")

    return df


if __name__ == "__main__":
    run_eval()