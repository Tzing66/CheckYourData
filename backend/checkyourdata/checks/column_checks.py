import pandas as pd

from checkyourdata.checks.registry import register
from checkyourdata.schema import CheckConfig, CheckType


@register(CheckType.NOT_NULL)
def not_null(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column]
    null_count = int(column.isna().sum())
    return null_count == 0, {"null_count": null_count, "row_count": len(column)}


@register(CheckType.MIN_MAX_RANGE)
def min_max_range(df: pd.DataFrame, check: CheckConfig) -> tuple[bool, dict]:
    column = df[check.column].dropna()
    min_bound = check.params.get("min")
    max_bound = check.params.get("max")

    violations = pd.Series(False, index=column.index)
    if min_bound is not None:
        violations |= column < min_bound
    if max_bound is not None:
        violations |= column > max_bound

    violation_count = int(violations.sum())
    return violation_count == 0, {
        "violation_count": violation_count,
        "observed_min": float(column.min()) if not column.empty else None,
        "observed_max": float(column.max()) if not column.empty else None,
    }
