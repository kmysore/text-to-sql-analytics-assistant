import yaml
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

def load_semantic_context(path: str = "docs/semantic_context.yaml") -> dict:
    """Load the semantic context YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_prompt(question: str, context: dict) -> str:
    """Build the prompt for Claude using semantic context."""
    
    # Format models section
    models_text = ""
    for model in context["models"]:
        models_text += f"\nTable: {model['name']}\n"
        models_text += f"Description: {model['description'].strip()}\n"
        models_text += f"Use when: {', '.join(model['use_when'])}\n"
        models_text += "Columns:\n"
        for col, desc in model["columns"].items():
            models_text += f"  - {col}: {desc}\n"

    # Format few-shot examples
    examples_text = ""
    for ex in context["few_shot_examples"]:
        examples_text += f"\nQuestion: {ex['question']}\n"
        examples_text += f"SQL:\n{ex['sql']}\n"

    # Format SQL guidelines
    guidelines_text = "\n".join(
        f"- {g}" for g in context["sql_guidelines"]
    )

    # Build full prompt
    prompt = f"""You are an expert analytics engineer. Convert the user's question into a SQL query.

## Business Context
{context['description'].strip()}
Date range: {context['business_context']['date_range']}
Regions: {', '.join(context['business_context']['regions'])}
Market segments: {', '.join(context['business_context']['market_segments'])}

## Available Tables
{models_text}

## SQL Guidelines
{guidelines_text}

## Examples
{examples_text}

## Instructions
- Return ONLY the SQL query, no explanation, no markdown, no backticks
- Use only the tables listed above
- Follow all SQL guidelines strictly

Question: {question}
SQL:"""

    return prompt


def generate_sql(question: str, context: dict = None) -> dict:
    """Generate SQL from a natural language question."""
    
    if context is None:
        context = load_semantic_context()

    prompt = build_prompt(question, context)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        sql = response.content[0].text.strip()

        return {
            "success": True,
            "sql": sql,
            "question": question,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }

    except Exception as e:
        return {
            "success": False,
            "sql": None,
            "question": question,
            "error": str(e)
        }

def run_agentic_pipeline(question: str, context: dict = None) -> dict:
    """
    Single API call using Claude tool use.
    Claude generates SQL, we execute it, Claude reads results and responds.
    """
    if context is None:
        context = load_semantic_context()

    # Define the SQL tool Claude can call
    tools = [
        {
            "name": "execute_sql",
            "description": "Execute a SQL query against the analytics warehouse and return results. Use this to answer the user's question.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute. Must be a SELECT or WITH statement."
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of why this SQL answers the question"
                    }
                },
                "required": ["sql", "reasoning"]
            }
        }
    ]

    # Build system prompt from semantic context
    models_text = ""
    for model in context["models"]:
        models_text += f"\nTable: {model['name']}\n"
        models_text += f"Description: {model['description'].strip()}\n"
        models_text += f"Use when: {', '.join(model['use_when'])}\n"
        models_text += "Columns:\n"
        for col, desc in model["columns"].items():
            models_text += f"  - {col}: {desc}\n"

    guidelines_text = "\n".join(f"- {g}" for g in context["sql_guidelines"])

    examples_text = ""
    for ex in context["few_shot_examples"]:
        examples_text += f"\nQuestion: {ex['question']}\nSQL:\n{ex['sql']}\n"

    system_prompt = f"""You are a senior data analyst answering business questions using data.

When a user asks a question:
1. Use the execute_sql tool to get the data
2. Read the actual results carefully
3. Answer the question DIRECTLY using specific numbers from the results
4. Write 2-4 sentences maximum in plain business language
5. Never say "the data shows", "I queried", "based on the results", or describe what you did
6. Never describe the SQL or mention technical details
7. Start your response with the actual answer

Examples of BAD responses:
- "I queried the monthly revenue table and found that revenue trended upward..."
- "The data shows that EUROPE had the highest revenue..."
- "Based on the results, the top customer is..."

Examples of GOOD responses:
- "EUROPE leads all regions with $44B in total revenue, narrowly ahead of ASIA at $43.9B..."
- "Customer#000143500 is your top customer with $6.76M in lifetime revenue across 39 orders..."
- "Revenue in 1995 peaked in July at $2.84B and was relatively stable throughout the year, ranging from $2.58B in February to $2.84B in July..."
- "48.8% of orders are open and 48.6% are fulfilled, with a small 2.6% in pending status..."

## Available Tables
{models_text}

## SQL Guidelines
{guidelines_text}

## Examples
{examples_text}

## Business Context
{context['description'].strip()}
Date range: {context['business_context']['date_range']}
Regions: {', '.join(context['business_context']['regions'])}
Market segments: {', '.join(context['business_context']['market_segments'])}"""

    messages = [{"role": "user", "content": question}]

    try:
        # First call — Claude decides to use the SQL tool
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        # Find the tool use block
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
                break

        if not tool_use_block:
            return {
                "success": False,
                "question": question,
                "sql": None,
                "df": None,
                "insight": None,
                "error": "Claude did not call the SQL tool"
            }

        sql = tool_use_block.input["sql"]
        reasoning = tool_use_block.input.get("reasoning", "")
        print(f"\n📝 Generated SQL:\n{sql}")
        print(f"📌 Reasoning: {reasoning}")

        # Execute the SQL
        from app.execute_sql import execute_sql as exec_sql
        exec_result = exec_sql(sql)

        if not exec_result["success"]:
            # Tell Claude the query failed
            tool_result_content = f"Error executing SQL: {exec_result['error']}"
            success = False
        else:
            df = exec_result["df"]
            # Summarize results for Claude — don't send 150k rows
            if len(df) > 20:
                df_summary = f"Results ({len(df)} total rows, showing first 20):\n{df.head(20).to_string(index=False)}"
            else:
                df_summary = f"Results ({len(df)} rows):\n{df.to_string(index=False)}"
            tool_result_content = df_summary
            success = True
            print(f"\n✅ {len(df)} rows returned")

        # Second turn — send results back to Claude for insight
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": tool_result_content
                    }
                ]
            }
        ]

        # Final call — Claude reads results and writes insight
        final_response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=system_prompt,
            tools=tools,
            messages=messages
        )

        # Extract text insight
        insight = ""
        for block in final_response.content:
            if hasattr(block, "text"):
                insight = block.text.strip()
                break

        total_tokens = (
            response.usage.input_tokens +
            response.usage.output_tokens +
            final_response.usage.input_tokens +
            final_response.usage.output_tokens
        )

        return {
            "success": success,
            "question": question,
            "sql": sql,
            "df": exec_result.get("df"),
            "row_count": exec_result.get("row_count", 0),
            "insight": insight,
            "tokens_used": total_tokens,
            "error": None if success else exec_result.get("error")
        }

    except Exception as e:
        return {
            "success": False,
            "question": question,
            "sql": None,
            "df": None,
            "insight": None,
            "error": str(e)
        }