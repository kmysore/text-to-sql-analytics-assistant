import sys
sys.path.append(".")

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from app.pipeline import run_pipeline
from app.generate_sql import load_semantic_context

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Text-to-SQL Analytics Assistant",
    page_icon="🔍",
    layout="wide"
)

# ── Load context once ─────────────────────────────────────────
@st.cache_resource
def get_context():
    return load_semantic_context()

context = get_context()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 Text-to-SQL")
    st.caption("Natural language analytics over TPC-H data")
    st.divider()

    st.markdown("**Available Models**")
    st.markdown("- `fct_orders` — order level")
    st.markdown("- `agg_monthly_revenue` — time series")
    st.markdown("- `agg_customer_stats` — customer level")
    st.divider()

    st.markdown("**Example Questions**")
    examples = [
        "What is the total revenue by region?",
        "Who are the top 10 customers by lifetime revenue?",
        "How has monthly revenue trended in 1995?",
        "What percentage of orders are fulfilled vs open?",
        "Which customers have placed more than 30 orders?",
        "What is the revenue rank of each region?",
        "What was the year over year revenue growth from 1993 to 1994?",
        "What is the month over month revenue change in 1996?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.question_input = ex
            st.rerun()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Ask a Question", "📊 Eval Results"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Ask a Question
# ══════════════════════════════════════════════════════════════
with tab1:
    st.header("Ask a Business Question")
    st.caption("Powered by Claude + dbt models over TPC-H data (1992-1998)")

    # Question input
    question = st.text_input(
        "Your question",
        placeholder="e.g. What is the total revenue by region?",
        key="question_input"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        run = st.button("Run", type="primary", use_container_width=True)
    with col2:
        clear = st.button("Clear", use_container_width=True)

    if clear:
        st.session_state.question_input = ""
        st.rerun()

    if run and question:
        with st.spinner("Generating SQL and fetching results..."):
            result = run_pipeline(question, context)

        if result["success"]:
            # Show results
            st.success(f"✅ {result['row_count']} rows returned")

            # Insight — shown prominently at the top
            if result.get("insight"):
                st.info(f"💡 {result['insight']}")

            # Generated SQL — collapsed by default so insight takes focus
            with st.expander("View Generated SQL", expanded=False):
                st.code(result["sql"], language="sql")

            # Results table
            st.subheader("Results")
            df = result["df"]
            st.dataframe(df, use_container_width=True)

            # Auto chart if numeric columns exist
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            text_cols = df.select_dtypes(exclude="number").columns.tolist()

            if len(numeric_cols) >= 1 and len(text_cols) >= 1:
                st.subheader("Chart")
                chart_col = st.selectbox(
                    "Select metric to chart",
                    numeric_cols,
                    key="chart_col"
                )
                x_col = text_cols[0]

                if len(df) <= 50:
                    fig = px.bar(
                        df,
                        x=x_col,
                        y=chart_col,
                        title=question,
                        color_discrete_sequence=["#4F8BF9"]
                    )
                else:
                    fig = px.line(
                        df,
                        x=x_col,
                        y=chart_col,
                        title=question,
                        color_discrete_sequence=["#4F8BF9"]
                    )

                st.plotly_chart(fig, use_container_width=True)

            # Token usage
            st.caption(f"Tokens used: {result['tokens_used']:,}")

        else:
            st.error(f"❌ {result['error']}")
            if result.get("sql"):
                with st.expander("Failed SQL"):
                    st.code(result["sql"], language="sql")

    elif run and not question:
        st.warning("Please enter a question first.")

# ══════════════════════════════════════════════════════════════
# TAB 2 — Eval Results
# ══════════════════════════════════════════════════════════════
with tab2:
    st.header("Evaluation Results")
    st.caption("50-question benchmark measuring SQL generation accuracy")

    # Load most recent eval results
    results_dir = Path("evals/results")
    csv_files = sorted(results_dir.glob("eval_*.csv"), reverse=True)

    if not csv_files:
        st.info("No eval results found. Run `python evals/run_eval.py` first.")
    else:
        latest = csv_files[0]
        df_eval = pd.read_csv(latest)

        st.caption(f"Latest eval: `{latest.name}`")

        # ── Top metrics ──────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)

        total = len(df_eval)
        exec_success = df_eval["execution_success"].sum()
        result_match = df_eval["result_match"].sum()
        tokens = df_eval["tokens_used"].sum()

        with col1:
            st.metric("Total Questions", total)
        with col2:
            st.metric(
                "Execution Success",
                f"{exec_success}/{total}",
                f"{100*exec_success/total:.1f}%"
            )
        with col3:
            st.metric(
                "Result Match",
                f"{result_match}/{total}",
                f"{100*result_match/total:.1f}%"
            )
        with col4:
            st.metric("Total Tokens", f"{tokens:,}")

        st.divider()

        # ── Accuracy by difficulty ───────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Accuracy by Difficulty")
            diff_data = []
            for diff in ["easy", "medium", "hard"]:
                subset = df_eval[df_eval["difficulty"] == diff]
                if len(subset) > 0:
                    diff_data.append({
                        "difficulty": diff.capitalize(),
                        "accuracy": 100 * subset["result_match"].sum() / len(subset),
                        "correct": subset["result_match"].sum(),
                        "total": len(subset)
                    })

            df_diff = pd.DataFrame(diff_data)
            fig = px.bar(
                df_diff,
                x="difficulty",
                y="accuracy",
                title="Accuracy by Difficulty",
                color="difficulty",
                color_discrete_map={
                    "Easy": "#00C49F",
                    "Medium": "#FFBB28",
                    "Hard": "#FF4444"
                },
                text=df_diff.apply(lambda r: f"{r['correct']}/{r['total']}", axis=1)
            )
            fig.update_layout(yaxis_range=[0, 100], showlegend=False)
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Accuracy by Category")
            cat_data = []
            for cat in df_eval["category"].unique():
                subset = df_eval[df_eval["category"] == cat]
                cat_data.append({
                    "category": cat,
                    "accuracy": 100 * subset["result_match"].sum() / len(subset),
                    "correct": subset["result_match"].sum(),
                    "total": len(subset)
                })

            df_cat = pd.DataFrame(cat_data).sort_values("accuracy", ascending=True)
            fig = px.bar(
                df_cat,
                x="accuracy",
                y="category",
                orientation="h",
                title="Accuracy by Category",
                color_discrete_sequence=["#4F8BF9"],
                text=df_cat.apply(lambda r: f"{r['correct']}/{r['total']}", axis=1)
            )
            fig.update_layout(xaxis_range=[0, 100])
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ── Question by question results ─────────────────────
        st.subheader("Question by Question Results")

        col1, col2 = st.columns(2)
        with col1:
            diff_filter = st.multiselect(
                "Filter by difficulty",
                ["easy", "medium", "hard"],
                default=["easy", "medium", "hard"]
            )
        with col2:
            status_filter = st.multiselect(
                "Filter by status",
                ["pass", "fail"],
                default=["pass", "fail"]
            )

        df_filtered = df_eval[df_eval["difficulty"].isin(diff_filter)].copy()
        if "pass" not in status_filter:
            df_filtered = df_filtered[df_filtered["result_match"] == False]
        if "fail" not in status_filter:
            df_filtered = df_filtered[df_filtered["result_match"] == True]

        for _, row in df_filtered.iterrows():
            status = "✅" if row["result_match"] else "❌"

            with st.expander(
                f"{status} [{row['id']}] {row['question'][:80]}",
                expanded=False
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Execution", "✅ Pass" if row["execution_success"] else "❌ Fail")
                with col2:
                    st.metric("Result Match", "✅ Pass" if row["result_match"] else "❌ Fail")
                with col3:
                    st.metric("Rows", f"{row['result_row_count']}/{row['gold_row_count']}")

                if pd.notna(row.get("generated_sql")):
                    st.code(row["generated_sql"], language="sql")

                if pd.notna(row.get("error")):
                    st.error(row["error"])