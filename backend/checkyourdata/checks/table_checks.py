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
