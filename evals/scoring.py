import pandas as pd
import numpy as np
from typing import Optional


def normalize_dates(series: pd.Series) -> pd.Series:
    """Strip time component from date strings and datetime columns."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series.dt.strftime("%Y-%m-%d")
    if series.dtype == object:
        return series.astype(str).str.replace(r"\s00:00:00$", "", regex=True).str.strip()
    return series


def normalize_numeric(series: pd.Series) -> pd.Series:
    """Convert to float rounded to 2 decimal places if possible."""
    try:
        return pd.to_numeric(series).round(2)
    except (ValueError, TypeError):
        return series


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a DataFrame for semantic comparison.
    Handles date formats, numeric precision, case, and ordering.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # Lowercase column names
    df.columns = [c.lower() for c in df.columns]

    # Normalize each column by type
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = normalize_dates(df[col])
        else:
            # Try numeric first
            numeric = pd.to_numeric(df[col], errors="coerce")
            if numeric.notna().all():
                df[col] = numeric.round(2).astype(str)
            else:
                # Treat as string — normalize dates and case
                df[col] = normalize_dates(df[col])
                df[col] = df[col].astype(str).str.strip().str.lower()

    # Sort columns alphabetically
    df = df.reindex(sorted(df.columns), axis=1)

    # Sort rows by all columns
    df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

    return df


def results_match(gold_df: pd.DataFrame, result_df: pd.DataFrame) -> bool:
    """
    Semantically compare two DataFrames.
    Ignores column names, date formatting, case, and row/column ordering.
    """
    if gold_df is None or result_df is None:
        return False

    gold_norm = normalize_df(gold_df)
    result_norm = normalize_df(result_df)

    # Must have same shape
    if gold_norm.shape != result_norm.shape:
        return False

    # Compare column by column by position
    try:
        for i in range(len(gold_norm.columns)):
            gold_col = gold_norm.iloc[:, i]
            result_col = result_norm.iloc[:, i]

            if not gold_col.reset_index(drop=True).equals(
                result_col.reset_index(drop=True)
            ):
                return False
        return True
    except Exception:
        return False


def categorize_error(error: str) -> str:
    """Categorize SQL errors into known failure types."""
    if error is None:
        return None

    error_lower = error.lower()

    if any(x in error_lower for x in ["syntax", "parse", "unexpected", "token"]):
        return "syntax_error"
    elif any(x in error_lower for x in ["column", "field", "attribute"]):
        return "missing_filter"
    elif any(x in error_lower for x in ["table", "catalog", "relation", "does not exist"]):
        return "wrong_table"
    elif any(x in error_lower for x in ["join", "ambiguous"]):
        return "faulty_join"
    elif any(x in error_lower for x in ["aggregat", "group", "sum", "count", "avg"]):
        return "aggregation_error"
    else:
        return "other_error"


def score_result(
    gold_rows: list,
    gold_columns: list,
    result_df: Optional[pd.DataFrame],
    error: Optional[str],
    execution_success: bool
) -> dict:
    """Score a single test case against gold using semantic matching."""

    gold_df = pd.DataFrame(gold_rows, columns=gold_columns) if gold_rows else pd.DataFrame()

    # Tier 1: Did it execute?
    if not execution_success or result_df is None:
        return {
            "execution_success": False,
            "result_match": False,
            "row_count_match": False,
            "error_category": categorize_error(error),
            "gold_row_count": len(gold_df),
            "result_row_count": 0
        }

    # Tier 2: Row count
    row_count_match = len(result_df) == len(gold_df)

    # Tier 3: Semantic match
    match = results_match(gold_df, result_df)

    return {
        "execution_success": True,
        "result_match": match,
        "row_count_match": row_count_match,
        "error_category": None if match else "result_mismatch",
        "gold_row_count": len(gold_df),
        "result_row_count": len(result_df)
    }