import sys
sys.path.append(".")
from app.pipeline import run_pipeline

questions = [
    ("H003", "What is the running total revenue by month in 1995?"),
    ("H006", "Which month had the highest revenue in each year?"),
    ("H007", "What is the month over month revenue change in 1996?"),
    ("H011", "Rank customers by lifetime revenue within each market segment?"),
    ("H015", "What is the cumulative customer count by market segment ordered by lifetime revenue?"),
]

separator = "=" * 60

for test_id, question in questions:
    print("\n" + separator)
    print(f"[{test_id}] {question}")
    print(separator)
    result = run_pipeline(question)
