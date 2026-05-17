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