# Text-to-SQL Analytics Assistant

A natural-language analytics interface that generates SQL queries against a dbt-modeled data warehouse, with a built-in evaluation framework measuring accuracy and failure modes.

## Why This Project

Most text-to-SQL demos hit raw tables and fail on real business questions. This project explores a more realistic pattern: layering an LLM over governed dbt models with a semantic context layer, then rigorously measuring how well it works.

## Architecture

User question → Streamlit UI → Claude API → Generated SQL → DuckDB → Results
                                    ↑
                          Semantic context (dbt model metadata + KPI definitions)

## Status

🚧 In development.

## Tech Stack

- **LLM:** Anthropic Claude (Sonnet 4.5)
- **Warehouse:** DuckDB with TPC-H benchmark dataset
- **Transformation:** dbt
- **UI:** Streamlit
- **Evaluation:** Custom Python harness

## Roadmap

- [x] Step 1: Environment setup
- [ ] Step 2: Load TPC-H, build dbt models
- [ ] Step 3: Semantic context layer
- [ ] Step 4: End-to-end query generation
- [ ] Step 5-8: Evaluation framework (50 test cases)
- [ ] Step 9-11: UI and deployment

## Setup

git clone https://github.com/YOUR_USERNAME/text-to-sql-analytics-assistant.git
cd text-to-sql-analytics-assistant
conda create -n text-to-sql python=3.11 -y
conda activate text-to-sql
pip install -r requirements.txt
cp .env.example .env  # then add your Anthropic API key

## Results

(To be added after evaluation runs)

## Author

Karthik Mysore — https://linkedin.com/in/kmysore03