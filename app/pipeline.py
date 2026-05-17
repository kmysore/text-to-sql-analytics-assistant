from app.generate_sql import generate_sql, load_semantic_context
from app.execute_sql import execute_sql

def run_pipeline(question: str, context: dict = None) -> dict:
    """Full pipeline: question -> SQL -> results."""

    if context is None:
        context = load_semantic_context()

    print(f"\n🔍 Question: {question}")

    # Step 1: Generate SQL
    gen_result = generate_sql(question, context)

    if not gen_result["success"]:
        return {
            "success": False,
            "question": question,
            "sql": None,
            "df": None,
            "error": gen_result.get("error", "SQL generation failed")
        }

    sql = gen_result["sql"]
    print(f"\n📝 Generated SQL:\n{sql}")

    # Step 2: Execute SQL
    exec_result = execute_sql(sql)

    if not exec_result["success"]:
        return {
            "success": False,
            "question": question,
            "sql": sql,
            "df": None,
            "error": exec_result["error"]
        }

    print(f"\n✅ Results: {exec_result['row_count']} rows returned")
    print(exec_result["df"].head(10).to_string(index=False))

    return {
        "success": True,
        "question": question,
        "sql": sql,
        "df": exec_result["df"],
        "row_count": exec_result["row_count"],
        "tokens_used": gen_result["tokens_used"],
        "error": None
    }