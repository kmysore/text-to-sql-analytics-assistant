import sys
import traceback
import os

# Add project root to path regardless of where script is called from
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import yaml
from mcp.server.fastmcp import FastMCP
from app.execute_sql import execute_sql

# Log errors to stderr so Claude Desktop captures them
def log_error(msg):
    print(msg, file=sys.stderr, flush=True)

# Initialize MCP server
mcp = FastMCP("Analytics Warehouse")

# Load semantic context once at startup
def load_context():
    yaml_path = os.path.join(project_root, "docs", "semantic_context.yaml")
    with open(yaml_path) as f:
        return yaml.safe_load(f)

try:
    context = load_context()
    log_error("✅ Context loaded successfully")
except Exception as e:
    log_error("❌ Failed to load context: " + str(e))
    log_error(traceback.format_exc())
    sys.exit(1)


def get_schema_description() -> str:
    lines = ["Available tables:\n"]
    for model in context["models"]:
        lines.append("Table: " + model["name"])
        lines.append("Description: " + model["description"].strip())
        lines.append("Use when: " + ", ".join(model["use_when"]))
        lines.append("Columns:")
        for col, desc in model["columns"].items():
            lines.append("  - " + col + ": " + desc)
        lines.append("")
    lines.append("SQL Guidelines:")
    for g in context["sql_guidelines"]:
        lines.append("  - " + g)
    return "\n".join(lines)


@mcp.tool()
def query_warehouse(sql: str) -> str:
    """
    Execute a SQL SELECT or WITH (CTE) query against the analytics warehouse.
    Always call get_warehouse_schema first to understand available tables.
    """
    result = execute_sql(sql)

    if not result["success"]:
        return "Query failed: " + str(result["error"])

    df = result["df"]

    if df is None or len(df) == 0:
        return "Query returned no results."

    output = "Query returned " + str(len(df)) + " rows.\n\n"
    output += df.to_string(index=False)
    return output


@mcp.tool()
def get_warehouse_schema() -> str:
    """
    Get the schema and documentation for all available tables.
    Always call this before writing SQL so you know what tables and columns exist.
    """
    return get_schema_description()


@mcp.tool()
def get_example_queries() -> str:
    """
    Get example questions and SQL queries as reference.
    Call this when writing complex SQL like window functions or time series.
    """
    lines = ["Example queries:\n"]
    for ex in context["few_shot_examples"]:
        lines.append("Question: " + ex["question"])
        lines.append("SQL:\n" + ex["sql"])
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")