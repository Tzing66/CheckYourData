import pandas as pd

from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


@register(CheckType.ROW_COUNT_MIN)
def row_count_min(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    min_rows = check.params["min_rows"]
    row_count = len(df)
    return row_count >= min_rows, {"row_count": row_count, "min_rows": min_rows}


@register(CheckType.ROW_COUNT_CHANGE_PCT)
def row_count_change_pct(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    row_count = len(df)
    baseline_row_count = check.params["baseline_row_count"]
    pct_tolerance = check.params.get("pct", 0.2)

    if baseline_row_count == 0:
        diff_pct = 0.0 if row_count == 0 else float("inf")
    else:
        diff_pct = abs(row_count - baseline_row_count) / baseline_row_count

    return diff_pct <= pct_tolerance, {
        "row_count": row_count,
        "baseline_row_count": baseline_row_count,
        "diff_pct": diff_pct,
        "pct_tolerance": pct_tolerance,
    }


@register(CheckType.ROW_COUNT_MAX)
def row_count_max(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    max_rows = check.params["max_rows"]
    row_count = len(df)
    return row_count <= max_rows, {"row_count": row_count, "max_rows": max_rows}


@register(CheckType.COLUMN_COUNT_MATCH)
def column_count_match(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    expected_count = check.params["expected_count"]
    column_count = len(df.columns)
    return column_count == expected_count, {"column_count": column_count, "expected_count": expected_count}


@register(CheckType.COLUMN_ORDER_MATCH)
def column_order_match(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    expected_columns = check.params["expected_columns"]
    actual_columns = df.columns.tolist()
    return actual_columns == expected_columns, {"actual_columns": actual_columns, "expected_columns": expected_columns}


@register(CheckType.FRESHNESS_CHECK)
def freshness_check(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = pd.to_datetime(df[check.column].dropna(), errors="coerce")
    max_age_hours = check.params["max_age_hours"]

    if column.empty:
        return False, {"latest_timestamp": None, "age_hours": None, "max_age_hours": max_age_hours}

    latest = column.max()
    age_hours = (pd.Timestamp.now() - latest).total_seconds() / 3600
    return age_hours <= max_age_hours, {
        "latest_timestamp": latest.isoformat(),
        "age_hours": age_hours,
        "max_age_hours": max_age_hours,
    }
