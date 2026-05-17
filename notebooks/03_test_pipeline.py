import sys
sys.path.append(".")  # make sure app/ is importable

from app.pipeline import run_pipeline

# Test questions — mix of easy, medium, hard
questions = [
    "How many customers do we have?",
    "What is the total revenue by region?",
    "Who are the top 5 customers by lifetime revenue?",
    "How has monthly revenue trended in 1995?",
    "What percentage of orders are fulfilled vs open?"
]

for question in questions:
    result = run_pipeline(question)
    print("\n" + "="*60)