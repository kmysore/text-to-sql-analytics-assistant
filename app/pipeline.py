from app.generate_sql import run_agentic_pipeline, load_semantic_context


def run_pipeline(question: str, context: dict = None, generate_insights: bool = True) -> dict:
    """
    Full agentic pipeline using Claude tool use.
    Single API conversation: question -> SQL tool call -> results -> insight.
    """
    if context is None:
        context = load_semantic_context()

    print(f"\n🔍 Question: {question}")
    return run_agentic_pipeline(question, context)